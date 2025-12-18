# system modules
import warnings
import itertools

# internal modules
from parmesan.units import units
from parmesan.accessor import ParmesanAccessor

# external modules
import numpy as np
import pandas as pd
import scipy.signal
from pint_pandas import PintArray
from rich.progress import Progress
from rich.console import Console


@ParmesanAccessor.register
def temporal_cycle(x, interval, resolution, times=None, modifier=lambda x: x):
    """
    Calculate a temporal cycle

    Examples
    ========

    .. code-block:: python

        # diurnal/daily cycle
        temporal_cycle(x, interval="D", resolution="m")
        # seasonal/yearly cycle
        temporarl_cycle(x, interval="Y", resolution="D")

    Args:
        x (pandas.DataFrame or pandas.Series or numpy.ndarray): the data to
            aggregate
        times (pandas.DatetimeIndex or numpy.ndarray of datetime64, optional):
            the times to use
        interval (str, optional): the interval to aggregate to. Has to be a
            string usable with numpy.datetime64_, e.g. ``"D"`` for a diurnal
            cycle.
        resolution (str, optional): the resolution to aggregate with. Has to be
            a string usable with numpy.datetime64_, e.g. ``"s"`` for a
            resulting resolution of seconds.
        modifier (callable, optional): a callable modifying the axis to
            aggregate over. This can be used to fine-tune the output
            resolution. For example, to get a diurnal cycle but in a resolution
            of 15 minutes because hours (``resolution="h"``) are too coarse and
            minutes (``resolution="m"``) too fine you could do this:

            .. code-block:: python

                temporal_cycle(
                    x,               # the data
                    interval="D",    # aggregate to daily intervals
                    resolution="m",  # with a minutely resolution
                    # but before grouping, divide the minutes by 15
                    # and drop the precision to get quarterly resolution
                    modifier = lambda minutes: (minutes / 15).astype(int) * 15
                )

    Returns:
        groupby object : the aggregated data. Handle it like the return value
        of :meth:`pandas.DataFrame.groupby`, e.g. call ``mean()`` on it to
        calculate the average value for all periods.


    .. _numpy.datetime64:
        https://numpy.org/devdocs/reference/arrays.datetime.html
    """
    times, x = ParmesanAccessor.whats_time_whats_data(x, times=times)
    interval_dtype = np.dtype("datetime64[{}]".format(interval))
    resolution_dtype = np.dtype("datetime64[{}]".format(resolution))
    # converting times to a coarser type drops the resolution,
    # thus this gives us the interval starting points
    interval_starts = getattr(times, "values", times).astype(interval_dtype)
    # each time point is so much time into the interval
    time_into_interval = (
        getattr(times, "values", times).astype(resolution_dtype)
        - interval_starts
    )
    # turn the time difference into the resolution unit
    aggregate_axis = (
        time_into_interval / np.timedelta64(1, resolution)
    ).astype(int)
    return (x if hasattr(x, "groupby") else pd.Series(x, index=times)).groupby(
        modifier(aggregate_axis)
    )


@ParmesanAccessor.register
def covariances(
    x,
    interval,
    columns=None,
    newname="cov({},{})".format,
    detrend=False,
    dropna=True,
    console=None,
    progress=None,
):
    """
    Resample to ``interval`` (e.g. ``10min``), then calculate covariances
    between combinations of ``columns``, displaying a progress bar to visualize
    the process.

    Args:
        x (DataFrame): the dataframe with time index to use
        interval (str): pandas resample interval to calculate covariances in
        columns (sequence or dict): the columns to perform covariances between.
            Can either be a sequence of column names (e.g.
            ``["col1","col2",...]``), in which case for all combinations
            between those covariances are calculated, or a dict mapping output
            column names for the covariances to a pair of input columns like
            ``{"heatflux":("w","θv"),...}``.  By default, combinations between
            all columns are processed.
        formatter (callable): function that takes two string arguments being
            the two input columns for the covariance and returning a new name
            for the covariance column. The default names output columns like
            ``cov(COL1,COL2)``
        detrend (str, optional): ``type`` for the :any:`scipy.signal.detrend`
            function to detrend the signals in the specific ``interval`` (e.g.
            ``"constant"`` or ``"linear"``).  Default is no detrending.
        dropna (bool, optional): drop NANs within interval before calculating
            covariance
        console (rich.console.Console, optional): the console to show the
            progress bar on.
        progress (rich.progress.Progress, optional): the progress bar to
            integrate with.

    Returns:
        DataFrame : new resampled dataframe with covariances as columns
    """
    if console is None:
        console = Console()
    if progress is None:
        progress = Progress(transient=True, console=console)
    if hasattr(x, "to_frame"):
        x = x.to_frame()
    if columns is None:
        columns = list(x.columns)
    if detrend and not dropna:
        dropna = True
        warnings.warn("Setting {dropna=!r} because {detrend=!r}")
    combinations = {}
    if items := getattr(columns, "items", None):
        columns = list(items())
    else:
        columns = list(columns)  # edge case if columns is generator
        if all(len(c) == 2 for c in columns):
            columns = [(None, c) for c in columns]
        else:
            columns = [
                (None, comb) for comb in itertools.combinations(columns, 2)
            ]
    for name, combination in columns:
        name = name or newname(*combination)
        for c in combination:
            if c not in x:
                warnings.warn(
                    f"Combination {combination} ({name!r}) skipped: column {c!r} not present!"
                )
        if comb := combinations.get(name):
            warnings.warn(
                f"Combination {combination} will shadow combination {comb} named {name!r}"
            )
        combinations[name] = combination
    newcols = []
    with progress:
        for name, (col1, col2) in progress.track(c := combinations.items()):
            cov = []
            times = []
            colunits = []
            for col in (col1, col2):
                try:
                    colunits.append(x[col].pint.u)
                except AttributeError:
                    colunits.append(units.dimensionless)
            for t, g in progress.track(
                x.resample(interval),
                description=name,
            ):
                data = []
                for col in (col1, col2):
                    try:
                        data.append(g[col].pint.m)
                    except AttributeError:
                        data.append(g[col])
                d1, d2 = data
                if dropna:
                    isnan = np.isnan(d1) | np.isnan(d2)
                    d1, d2 = d1[~isnan], d2[~isnan]
                if detrend:
                    d1 = scipy.signal.detrend(d1, type=detrend)
                    d2 = scipy.signal.detrend(d2, type=detrend)
                cov.append(np.cov(d1, d2)[0, 1])
                times.append(t)

            if (unit := colunits[0] * colunits[1]) != units.dimensionless:
                cov = PintArray(cov, dtype=unit)
            newcols.append(pd.Series(cov, name=name, index=times))

    with console.status(f"Merging {len(newcols)} covariance columns..."):
        result = pd.concat(newcols, axis="columns")
    return result
