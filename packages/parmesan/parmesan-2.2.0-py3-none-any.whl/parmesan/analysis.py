# system modules
import itertools
import math
import sys
import warnings

import matplotlib.pyplot as plt

# external modules
import numpy as np
import pandas as pd
import pint
import scipy.fftpack
import scipy.interpolate
import scipy.optimize
import scipy.signal
import rich.progress
from matplotlib.gridspec import GridSpec
from pint_pandas import PintArray

# internal modules
from parmesan import utils
from parmesan.accessor import ParmesanAccessor
from parmesan.errors import ParmesanWarning, deprecated
from parmesan.units import units


def significant_digits(x):
    """
    Determine the amount of significant digits by looking at the differences

    Args:
        x (array-like): the array to examine

    Returns:
        int: the number of digits, e.g. for use with :any:`round`
    """
    diff = np.abs(np.diff(x))
    return np.clip(
        -(math.floor(np.log10(np.clip(diff, sys.float_info.min, None)).max())),
        0,
        None,
    ).astype(int)


def evenly_spaced_interval(x):
    """
    Heuristic to determine if values are evenly spaced.

    If the :any:`numpy.diff` is not unique, the diff is
    auto-:any:`numpy.round`-ed.  For this, the number of significant digits of
    the diff and **its** diff is determined and the average of those numbers of
    digits is then used for rounding the diff of ``x``. If that doesn't result
    in a unique diff, ``None`` is returned as this probably means the values
    are not evenly spaced.

    Args:
        x (array-like): the values to check

    Returns:
        type of ``x`` : the spacing interval
        None : if ``x`` is not evenly spaced
    """
    diff = np.unique(np.diff(x))  # unique differences between x
    if diff.size == 1:  # if only one unique diff, that's it!
        return diff[0]
    x_digits = significant_digits(x)  # significant digits x itself
    diff_digits = significant_digits(diff)  # significant digits of diff of x
    digits = math.ceil(np.mean([x_digits, diff_digits]))  # average of digits
    if (diff_rounded := np.unique(np.round(diff, digits))).size >= 1:
        if diff_rounded.size > 1:
            warnings.warn(
                f"Couldn't find a unique evenly spaced interval (candidates: {diff_rounded}). Using {diff_rounded[0]}",
                ParmesanWarning,
            )
        # if rounding to this amount of digits yields unique diff, that's it
        return diff_rounded[0]
    return None


@deprecated()
def power_spectrum(*args, **kwargs):
    """
    Deprecated old name for :any:`variance_spectrum` with ``window="hann"`` and
    ``detrend="linear"``.
    """
    return variance_spectrum(
        *args, **{**dict(window="hann", detrend="linear"), **kwargs}
    )


def variance_spectrum(
    x,
    y,
    window=None,
    blocks=1,
    overlap=True,
    detrend="constant",
    norm=True,
    normalize=False,
    density=False,
    double=True,
    interpolation=None,
    returnvalue=("frequency", "power"),
):
    """
    Calculate a variance spectrum for a one-dimensional signal of real values
    according to Stull (1988).

    This is the workhorse for the :func:`spectrum` convenience wrapper which
    should be preferred over direct invocation of this function.

    Args:
        x (:any:`pint.Quantity`-like): the x coordinate (e.g. time in seconds)
        y (:any:`pint.Quantity`-like): the signal
        window (str, optional): windowing function. See
            :any:`scipy.signal.get_window`.
        blocks (int, optional): How many overlapping blocks to use. Defaults to
            1.
        overlap (bool, optional): whether to let the blocks overlap by 50% of
            their width. This means, only an odd number of blocks can be used
            if ``overlap=True``. A warning is raised and the block size
            increased automatically otherwise.
        interpolation (str, optional): interpolation method to use for
            unevenly-spaced times. See ``kind`` argument of
            :func:`scipy.interpolate.interp1d`. By default, no
            interpolation is performed and a warning is raised for
            unevenly-space times.
        detrend (str, optional): detrending method. See
            :any:`scipy.signal.detrend`.
        norm (bool, optional): whether to divide the signal by its length
        normalize (bool, optional): whether to divide the spectral variance by
            the original signal's variance. This causes the spectrum to be
            normalized within the interval ``[0;1]``.
        density (bool, optional): whether to divide by the Δf frequency bin
            size. Defaults to ``False``, which means the default is a
            **discrete variance spectrum**.
        double (bool, optional): whether to double the values (except for the
            constant term) to account for the mirrored negative frequencies.
            Defaults to ``True``, which means that the sum of the output should
            return the original signal's variance according to Parseval's
            Theorem if ``window=None`` and ``detrend=constant`` and
            ``blocks=1``.
        returnvalue (sequence of str, optional): What to return. Values:

            ``"frequency"``
                the frequencies (inverse unit of ``x``)

            ``"period"``
                the periods (inverse of ``frequency``)

            ``"power"``
                the spectral power/variance (squared unit of ``y``)

            ``"blocks"``
                the (possibly conditioned) timeseries blocks used to calculate
                the spectrum as :any:`pint.Quantity`

            ``"kolmogorov"``
                a power-law fit ``A * frequency ^ (-5/3)``

            ``"kolmogorov-scale"``
                factor A of a power-law fit ``A * frequency ^ (-5/3)``

    Returns:
        sequence : as specified with ``returnvalue``
    """
    x = units.Quantity(x)
    y = units.Quantity(y)
    try:
        y + y
    except pint.OffsetUnitCalculusError as e:
        y_u = y.u
        y = y.to_base_units()
        warnings.warn(
            f"Converted y from [{y_u}] to [{y.u}] for compatibility",
            category=ParmesanWarning,
        )
    # make sure number of blocks is correct
    if overlap and blocks % 2 == 0:
        blocks += 1
        warnings.warn(
            "An odd number of blocks is needed if overlap=True. "
            "Increasing number of blocks to {}.".format(blocks),
            category=ParmesanWarning,
        )
    # drop older values to fit the number of blocks
    n_base_blocks = math.ceil(blocks / 2) if overlap else blocks
    if x.size > n_base_blocks:
        drop = x.size % n_base_blocks
        if drop:
            warnings.warn(
                "Dropping first {} of {} samples to fit "
                "evenly into {} blocks".format(drop, x.size, n_base_blocks),
                category=ParmesanWarning,
            )
            x, y = x[drop:], y[drop:]
    block_size = int(x.size / n_base_blocks)
    # interpolate to evenly-spaced times if necessary
    if (Δx := evenly_spaced_interval(x.m)) is None:
        if x.size > 1:
            if interpolation:
                interpolator = scipy.interpolate.interp1d(x, y)
                x = np.linspace(x.min(), x.max(), num=x.size)
                Δx = (x.max() - x.min()) / (x.size - 1)
                y = interpolator(x)
            else:
                timesteps = np.unique(np.diff(x.m))
                warnings.warn(
                    "FFT over unevenly-spaced x coordinates "
                    "({} occurring timesteps: {}) will "
                    "yield unexpected results! "
                    "Consider setting interpolation='linear' "
                    "for example.".format(
                        timesteps.size,
                        timesteps,
                    ),
                    category=ParmesanWarning,
                )
                Δx = timesteps[0]
    Δx = units.Quantity(Δx, x.u)
    # split into blocks
    blocks_cond = []
    if overlap and blocks > 1:
        blocks_cond.extend(units.Quantity(np.split(y.m, n_base_blocks), y.u))
        n_overlap_blocks = blocks - n_base_blocks
        overlap_block_region = slice(
            math.floor(block_size / 2), -math.ceil(block_size / 2)
        )
        assert len(y[overlap_block_region]) % block_size == 0, (
            "Overlap block region should be divisible by {}, "
            "but has size {}"
        ).format(block_size, len(y[overlap_block_region]))
        blocks_cond.extend(
            units.Quantity(
                np.split(
                    y[overlap_block_region].m,
                    n_overlap_blocks,
                ),
                y.u,
            )
        )
    else:
        blocks_cond.extend(units.Quantity(np.split(y.m, blocks), y.u))
    # detrend
    if detrend:
        blocks_cond = [
            units.Quantity(
                scipy.signal.detrend(block.m, type=detrend), block.u
            )
            for block in blocks_cond
        ]
    # apply a window to all blocks if wanted
    if window:
        if window.lower() == "hanning":  # pragma: no cover
            warnings.warn(
                "scipy v1.9 removed the 'hanning' alias for 'hann'. "
                "Please change your usage of "
                "window='hanning' to window='hann'.",
                DeprecationWarning,
            )
            window = "hann"
        blocks_cond = [
            units.Quantity(
                block.m * scipy.signal.get_window(window, block.size), block.u
            )
            for block in blocks_cond
        ]
    if normalize:  # divide by variance (first thing!) if wanted
        blocks_cond = [block / np.var(block, ddof=0) for block in blocks_cond]
    blocks_forfft = blocks_cond.copy()
    if norm:  # divide by size
        blocks_forfft = [block / block.size for block in blocks_forfft]
    if (
        density
    ):  # divide by sqrt(Δf = f/N = 1/(Δt*N)), because the the fft gets squared
        blocks_forfft = [
            block / (Δf := 1 / np.sqrt(Δx * block.size))
            for block in blocks_forfft
        ]
    # calculate power spectrum
    power = (
        # calculate the absolute value of fourrier values
        np.abs(
            # calculate average across blocks/columns
            np.nanmean(
                # stack fft block resuls as rows on top of each other
                np.vstack(
                    # Fourrier transform each block
                    [
                        # FFT doesn't change unit
                        units.Quantity(scipy.fft.rfft(block.m), block.u)
                        for block in blocks_forfft
                    ]
                ),
                axis=0,
            )
        )
        # square the absolute value to get the power
        ** 2
    )
    if double:
        power_const = power[0]
        power *= 2
        power[0] = power_const  # acc. to Stull don't double the constant freq
    # if density:
    #     power /= (Δf := 1 / Δx)
    # calculate frequencies
    freq = units.Quantity(scipy.fft.rfftfreq(block_size, Δx or 1), 1 / x.u)
    retvals = dict(
        frequency=freq,
        power=power,
        blocks=blocks_cond,
    )
    if "kolmogorov" in returnvalue:

        def powerlaw(f, scale):
            return scale * f ** (-5 / 3)

        (scale,), pcov = scipy.optimize.curve_fit(
            powerlaw, freq.m[1:], power.m[1:]
        )
        retvals["kolmogorov-scale"] = scale
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            retvals["kolmogorov"] = units.Quantity(
                powerlaw(freq.m, retvals["kolmogorov-scale"]), power.u
            )
    if "period" in returnvalue:
        with utils.out_warnings(RuntimeWarning):
            retvals["period"] = 1 / freq
    return tuple(retvals.get(k, None) for k in returnvalue)


@ParmesanAccessor.register
def spectrum(
    x, times=None, with_kolmogorov=False, index_with_unit=False, **kwargs
):
    """
    Calculate a power spectrum of a one-dimensional timeseries of real values

    This is a convenience wrapper for :func:`variance_spectrum`.

    For an example, see the `Spectrum Example`_.

    .. _Spectrum Example: ../notebooks/spectrum.ipynb

    Args:
        x (pandas.DataFrame or pandas.Series or numpy.ndarray): the values
            to calculate the spectrum for
        times (array-like of datetime-like, optional): the times to use
        with_kolmogorov (bool, optional): add a power law fit to the output
        index_with_unit (bool, optional): whether to add a unit to the
            resulting index. Expect quirks like slowness and ugly matplotlib
            axis labels when setting this to ``True``. Defaults to ``False``
            which just adds the unit to the index name.
        **kwargs: further keyword arguments to :func:`variance_spectrum`

    Returns:
        sequence, :class:`pandas.Series` or :class:`pandas.DataFrame` :

        Depending on the type of ``x``:

        :class:`numpy.ndarray`
            the sequence ``frequencies,power`` of :class:`numpy.ndarray` s

        :class:`pandas.Series`
            a new :class:`pandas.Series` of the power with the frequency as
            index

        :class:`pandas.DataFrame`
            a new :class:`pandas.DataFrame` with the frequency as index and
            corresponding columns containing the power

    """
    times, x = ParmesanAccessor.whats_time_whats_data(x, times=times)
    # calculate time in seconds
    t = units.Quantity(
        (times - times.min()).values / np.timedelta64(1, "s"), "s"
    )
    if (returnvalue := kwargs.get("returnvalue")) and returnvalue != (
        v := ("frequency", "power")
    ):
        warnings.warn(
            f"Overwriting {returnvalue = !r} with {v!r}. "
            f"Use variance_spectrum(..., {returnvalue = !r}) directly"
            f"If you really need this",
            category=ParmesanWarning,
        )
        kwargs["returnvalue"] = v
        del v

    def get_colname(c):
        return (
            f"{c} spectral variance density"
            if kwargs.get("density")
            else f"{c} discrete spectral variance"
        )

    def make_index(freq):
        if index_with_unit:
            return pd.Index(PintArray(freq), name="frequency")
        else:
            return pd.Index(freq.m, name=f"frequency [{freq.u}]")

    if isinstance(x, pd.Series):
        if with_kolmogorov:
            freq, power, kolmogorov, kolmogorov_scale = variance_spectrum(
                x=t,
                y=getattr(x.values, "quantity", x.values),
                **{
                    **kwargs,
                    **dict(
                        returnvalue=(
                            "frequency",
                            "power",
                            "kolmogorov",
                            "kolmogorov-scale",
                        )
                    ),
                },
            )
            return pd.DataFrame(
                {
                    get_colname(x.name): PintArray(power),
                    f"{get_colname(x.name)} power-law "
                    f"[{kolmogorov_scale:g} f ^ (-5/3)]": PintArray(
                        kolmogorov
                    ),
                },
                index=make_index(freq),
            )
        else:
            freq, power = variance_spectrum(
                x=t, y=getattr(x.values, "quantity", x.values), **kwargs
            )
            s = pd.Series(PintArray(power), name=get_colname(x.name))
            s.index = make_index(freq)
            return s
    elif isinstance(x, pd.DataFrame):
        if with_kolmogorov:
            warnings.warn(
                f"Currently, {with_kolmogorov = } "
                f"is not implemented for DataFrame inputs. "
                f"But you can select a specific column like "
                f"df[{next(iter(x.columns),'colname')!r}]"
                f".parmesan.spectrum({with_kolmogorov = !r})",
                category=ParmesanWarning,
            )
        spectra = {
            get_colname(c): variance_spectrum(
                x=t,
                y=getattr(x[c].values, "quantity", x[c].values),
                **kwargs,
            )
            for c in x
        }
        freq = next(freq for c, (freq, power) in spectra.items())
        return pd.DataFrame(
            {c: PintArray(power) for c, (freq, power) in spectra.items()},
            index=make_index(freq),
        )
    else:
        return variance_spectrum(x=t, y=x, **kwargs)


def structure_function(
    x,
    y,
    order=2,
    minlag=0,
    maxlag="75%",
    lagstep="0.5%",
    normed=True,
    progress=False,
):
    r"""
    Calculate the structure function for a one-dimensional signal of real
    values.

    This is the workhorse for the :func:`structure` convenience wrapper which
    should be preferred over direct invocation of this function.

    Args:
        x (sequence of floats): the x coordinate (e.g. time in seconds)
        y (sequence of floats): the signal
        order (int, optional): The order of the structure function
        minlag, maxlag, lagstep (int or str, optional): lag endpoints and step
            to calculate, e.g. "50%", 100, "1min" or "10s". Default is everything
            up to "75%" at the maximum resolution step (1).
        normed (bool, optional): whether to norm the structure function with
            twice the variances of the signal overlaps. This makes the
            structure function roughly equal :math:`(1 -
            \mathrm{Autocorrelationfunction})` for small lags.
        progress (bool or rich.progress.Progress, optional): whether to display
            progress bar or progress bar instance

    Returns:
        sequence of arrays : x shift, structure function value

    Raises:
        ValueError : if ``x`` is not evenly spaced.
    """
    # convert inputs to numpy arrays
    t = np.asarray(x)
    y = np.asarray(y)
    minlag = units.Quantity(minlag)
    maxlag = units.Quantity(maxlag)
    lagstep = units.Quantity(lagstep)

    if not (dt := evenly_spaced_interval(t)):
        raise ValueError(
            f"x-coordinate not evenly spaced (Found {dt = }). Consider resampling."
        )

    def toshift(min_=0, max_=y.size, default=0, **kwargs):
        q = kwargs.pop(name := next(iter(kwargs)))
        if q.u == units.dimensionless:
            q_ = int(q.m)
        elif q.is_compatible_with("dimensionless"):
            q_ = int(q.to("dimensionless").m * y.size)
        elif q.is_compatible_with("second"):
            q_ = int((q / units.Quantity(dt, "s")).to("dimensionless").m)
        else:
            warnings.warn(
                f"Weird {name} = {q!r}, using {default = }",
                category=ParmesanWarning,
            )
            q_ = default
        q_ = np.clip(q_, min_, max_)
        return q_

    minlag_ = toshift(minlag=minlag, default=0)
    maxlag_ = toshift(maxlag=maxlag, min_=1, default=y.size)
    lagstep_ = toshift(lagstep=lagstep, min_=1, default=1)

    if (nlags := maxlag_ - minlag_) <= 0:
        raise ValueError(
            f"{maxlag=:P} (→{maxlag_}) is not larger than {minlag=:P} (→{minlag_})"
        )
    if lagstep_ >= nlags:
        raise ValueError(
            f"{lagstep=:P} (→{lagstep_}) is not smaller than total shifts ({nlags})"
        )

    if (enabled := progress) in (True, False):
        pbar = rich.progress.Progress(disable=not enabled)
    else:
        pbar = progress

    with pbar:
        shifts = np.arange(minlag_, maxlag_ - 1, lagstep_)
        D = shifts * np.nan  # start with array full of NaNs
        # we want to shift the data against itself in its entirety
        for i, lag in enumerate(pbar.track(shifts, description="structure")):
            y1 = y[: y.size - lag]  # overlap from start
            y2 = y[lag:]  # overlap from end
            var = (
                np.nanstd(y1) * np.nanstd(y2)
            ) or np.nan  # ”variance” of overlap
            D[i] = np.nanmean((y1 - y2) ** order)  # calculate
            if normed:
                # ”norming” the structure function with 2σ²
                # makes it roughly equal (1 - Autocorrelation)
                D[i] /= 2 * var
    lags = shifts * dt  # turn shifts into lags

    return lags, D


@ParmesanAccessor.register
def structure(x, times=None, **kwargs):
    """
    Calculate the structure function of a one-dimensional timeseries of real
    values

    This is a convenience wrapper for :func:`structure_function`.

    Args:
        x (pandas.DataFrame or pandas.Series or numpy.ndarray): the values
            to calculate the structure function for
        times (array-like of datetime-like, optional): the times to use
        **kwargs: further keyword arguments to :func:`structure_function`

    Returns:
        sequence, :class:`pandas.Series` or :class:`pandas.DataFrame` :

        Depending on the type of ``x``:

        :class:`numpy.ndarray`
            the sequence ``timeshifts,structurefunction`` of
            :class:`numpy.ndarray` s

        :class:`pandas.Series`
            a new :class:`pandas.Series` of the structure function with the
            timeshift as index

        :class:`pandas.DataFrame`
            a new :class:`pandas.DataFrame` with the timeshift as index and
            corresponding columns containing the structurefunction

    """
    times, x = ParmesanAccessor.whats_time_whats_data(x, times=times)
    # calculate time in seconds
    t = (times - times.min()) / np.timedelta64(1, "s")
    if isinstance(x, pd.Series):
        shift, DD = structure_function(x=t, y=x, **kwargs)
        s = pd.Series(DD, name=x.name)
        s.index = pd.Index(shift, name="Time Shift [s]")
        return s
    elif isinstance(x, pd.DataFrame):
        structures = {c: structure_function(x=t, y=x[c], **kwargs) for c in x}
        df = pd.DataFrame(
            {c: DD for c, (shift, DD) in structures.items()},
        )
        df.index = pd.Index(
            next(shift for c, (shift, DD) in structures.items()),
            name="Time Shift [s]",
        )
        return df
    else:
        return structure_function(x=t, y=x, **kwargs)


def autocorrelation_function(
    signal,
    times=None,
    detrend="constant",
    only_overlap=None,
    **correlate_kwargs,
):
    """
    Calculate autocorrelation function of a time series.

    Args:
        signal (array-like): the signal
        times (array-like, optional): the times/x-coordinate to use
        detrend (str or None, optional): optional detrending,
            see :any:`scipy.signal.detrend`
        only_overlap (bool, optional): whether to norm with variance of
            overlap, not of the entire signal. Defaults to ``False``, which is
            the same common behaviour of other statistical software (and in
            fact uses :any:`scipy.signal.correlate`) and causes the returned
            values to be bounded within ``[-1;1]``.

    Returns:
        array, array  : lags in units of ``times`` and autocorrelation function
    """
    signal = np.array(signal)
    if (n := np.isnan(signal).sum()) > 0 and not only_overlap:
        only_overlap = True
        warnings.warn(
            f"There are {n} NANs in the signal, forcing {only_overlap=} (slow but correct)"
        )
    if times is None:
        times = np.arange(signal.size)
    elif (dt := evenly_spaced_interval(times)) is None:
        raise ValueError(
            f"Signal times must be evenly-spaced. "
            f"Consider resampling the signal."
        )
    if detrend:
        signal = scipy.signal.detrend(signal, type=detrend)
    else:
        warnings.warn(
            f"{detrend = }, Keep in mind that if you don't detrend, "
            f"the autocorrelation function is not necessarily normalized within [-1;1].",
            category=ParmesanWarning,
        )
    if only_overlap:
        # manual auto-correlation function calculation
        xcorr = np.full(signal.size, np.nan)
        for lag in (shifts := np.arange(signal.size)):
            x1 = signal[: signal.size - lag]
            x2 = signal[lag:]
            var = (np.nanstd(x1) * np.nanstd(x2)) or np.nan
            xcorr[lag] = np.nanmean(x1 * x2) / var
        lags = shifts * dt
    else:
        xcorr = (
            scipy.signal.correlate(
                signal,
                signal,
                **{**dict(mode="full"), **correlate_kwargs},
            )
            / signal.std()
            / signal.std()
            / signal.size
        )
        lags = (
            scipy.signal.correlation_lags(
                signal.size, signal.size, mode="full"
            )
            * dt
        )

        positive = lags >= 0
        xcorr = xcorr[positive]
        lags = lags[positive]
    return lags, xcorr


@ParmesanAccessor.register
def autocorrelation(x, times=None, **kwargs):
    """
    Calculate the autocorrelation function of a one-dimensional timeseries of real
    values

    This is a convenience wrapper for :func:`autocorrelation`.

    Args:
        x (pandas.DataFrame or pandas.Series or numpy.ndarray): the values
            to calculate the structure function for
        times (array-like of datetime-like, optional): the times to use
        **kwargs: further keyword arguments to :func:`autocorrelation_function`

    Returns:
        sequence, :class:`pandas.Series` or :class:`pandas.DataFrame` :

        Depending on the type of ``x``:

        :class:`numpy.ndarray`
            the sequence ``timeshifts,acf`` of
            :class:`numpy.ndarray` s

        :class:`pandas.Series`
            a new :class:`pandas.Series` of the acf with the
            timeshift as index

        :class:`pandas.DataFrame`
            a new :class:`pandas.DataFrame` with the timeshift as index and
            corresponding columns containing the acf

    """
    times, x = ParmesanAccessor.whats_time_whats_data(x, times=times)
    # calculate time in seconds
    t = (times - times.min()) / np.timedelta64(1, "s")
    if isinstance(x, pd.Series):
        lags, acf = autocorrelation_function(times=t, signal=x, **kwargs)
        s = pd.Series(acf, name=x.name)
        s.index = pd.Index(lags, name="Time Shift [s]")
        return s
    elif isinstance(x, pd.DataFrame):
        acfs = {
            c: autocorrelation_function(times=t, signal=x[c], **kwargs)
            for c in x
        }
        df = pd.DataFrame(
            {c: acf for c, (lags, acf) in acfs.items()},
        )
        df.index = pd.Index(
            next(lags for c, (lags, acf) in acfs.items()),
            name="Time Shift [s]",
        )
        return df
    else:
        return autocorrelation_function(times=t, signal=x, **kwargs)


@ParmesanAccessor.register
def quicklook(
    df,
    fig=None,
    timeseries=True,
    timeseries_plot_kwargs=None,
    histogram=True,
    histogram_plot_kwargs=None,
    spectrum=True,
    spectrum_kwargs=None,
    spectrum_plot_kwargs=None,
    spectrum_log="xy",
    structure=True,
    structure_kwargs=None,
    structure_plot_kwargs=None,
    autocorrelation=True,
    autocorrelation_kwargs=None,
    autocorrelation_plot_kwargs=None,
    sync_autocorrelation_and_structure=True,
    sync_timeseries_and_histogram=True,
):  # pragma: no cover
    """
    Make an overview plot of a timeseries to quickly check some important properties.

    Args:
        x (dataframe-like): the dataframe/series to plot
        fig (matplotlib.figure.Figure, optional): the figure to plot into
        timeseries, histogram, spectrum, structure, autocorrelation (bool, optional): (de)activate certain plots
        STEP_kwargs (dict, optional): keyword arguments for the different steps

    Example:

    .. code-block:: python

        # all columns
        df.parmesan.quicklook()
        # one specific column
        df["column"].parmesan.quicklook()
        # specific columns
        df[["column1","column2"]].parmesan.quicklook()
        # resample if it complains about NaNs or unevenly-spaced times
        df_resampled = df.resample("10min").mean().ffill().dropna(how="any")
        df_resampled.parmesan.quicklook()
    """
    nrows = (
        min(timeseries + histogram, 1) + spectrum + structure + autocorrelation
    )
    if nrows <= 0:
        warnings.warn(
            f"All quicklooks disabled, nothing to plot.",
            category=ParmesanWarning,
        )
        return None
    gs = GridSpec(
        nrows=nrows,
        ncols=max(timeseries + histogram, 1),
    )
    fig = fig or plt.figure(
        figsize=(
            plt.rcParams["figure.figsize"][0],
            gs.nrows * plt.rcParams["figure.figsize"][-1] / 2,
        ),
        tight_layout=True,
    )

    row = itertools.count()
    if timeseries or histogram:
        r = next(row)
        if timeseries:
            axplot = fig.add_subplot(
                gs[r, slice(0, max(timeseries - histogram + 1, 1))],
            )
            axplot.set_title(f"Timeseries")
            df.plot(ax=axplot, **(timeseries_plot_kwargs or {}))

        if histogram:
            axhist = fig.add_subplot(
                gs[r, slice(histogram + 0, None)],
                sharey=(
                    axplot
                    if sync_timeseries_and_histogram and histogram
                    else None
                ),
            )
            axhist.set_title(f"Histogram")
            df.plot.hist(
                ax=axhist,
                **{
                    **dict(
                        orientation=(
                            "horizontal"
                            if sync_timeseries_and_histogram and timeseries
                            else "vertical"
                        )
                    ),
                    **(histogram_plot_kwargs or {}),
                },
            )

    if spectrum:
        axspectrum = fig.add_subplot(gs[next(row), :])
        axspectrum.set_title(f"Spectrum")
        if df.isna().any().any():
            warnings.warn(
                f"Interpolating and dropping NAs for spectrum",
                category=ParmesanWarning,
            )
            df_spectrum = df.interpolate().dropna(how="any")
        else:
            df_spectrum = df
        df_spectrum.parmesan.spectrum(
            **{**dict(with_kolmogorov=True), **(spectrum_kwargs or {})}
        ).plot(
            ax=axspectrum,
            **{**dict(logx=True, logy=True), **(spectrum_plot_kwargs or {})},
        )

    if structure:
        if df.isna().any().any():
            warnings.warn(
                f"Interpolating and dropping NAs for structure function",
                category=ParmesanWarning,
            )
            df_structure = df.interpolate().dropna(how="any")
        else:
            df_structure = df
        axstructure = fig.add_subplot(gs[next(row), :])
        axstructure.set_title(f"Structure Function")
        df_structure.parmesan.structure(**(spectrum_kwargs or {})).plot(
            ax=axstructure,
            **{**dict(logy=True), **(structure_plot_kwargs or {})},
        )
        axstructure.xaxis.set_tick_params(labelbottom=True)
        axstructure.set_ylim(top=2)

    if autocorrelation:
        if df.isna().any().any():
            warnings.warn(
                f"Interpolating and dropping NAs for autocorrelation function",
                category=ParmesanWarning,
            )
            d = df.interpolate().dropna(how="any")
        else:
            d = df
        axacf = fig.add_subplot(
            gs[next(row), :],
            sharex=(
                axstructure
                if sync_autocorrelation_and_structure and structure
                else None
            ),
        )
        axacf.set_title(f"Autocorrelation")
        d.parmesan.autocorrelation(**(autocorrelation_kwargs or {})).plot(
            ax=axacf, **(autocorrelation_plot_kwargs or {})
        )
