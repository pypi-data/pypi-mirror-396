# system modules

# internal modules
from parmesan.accessor import ParmesanAccessor

# external modules
import scipy.signal
import numpy as np
import pandas as pd


@ParmesanAccessor.register
def find_conspicuous_values(x, rel_prominence=None, **kwargs):
    """
    Find unusual peaks in the distribution of (integer!) values in (each column
    of) x

    This is a shortcut for :func:`scipy.signal.find_peaks` ran on the data's
    histogram.

    Args:
        x (pandas.DataFrame or array-like of int): integer values to check
        rel_prominence (float in range [0;1], optional): threshold for the
            ratio of peak prominence to the value of the peak, which is a loose
            proxy for the ratio to the neighbouring samples. So if you want to
            filter for peaks that ”stand out by at least 40% of their own
            magnitude”, then set `rel_prominence=0.4`.
        **kwargs: further arguments to :any:`scipy.signal.find_peaks`

    Returns:
        dict or sequence of numpy.ndarray : If ``x`` is array-like, return the
        tuple of same-length :class:`numpy.ndarray` s *(indices of conspicuous
        values in x,occurrence frequencies of these values)*. If ``x`` is a
        :class:`pandas.DataFrame`, return a :class:`dict` mapping column names
        to the above tuple per column.
    """
    if isinstance(x, pd.DataFrame):
        return {c: find_conspicuous_values(x[c]) for c in x}
    # count how often every integer value appears
    # make sure the histogram is 0 outside: extend by 3:
    # +1 because in np.arange the upper bound is exclusive,
    # +1 for the rightmost element to be recognized as a peak,
    #  it's right neighbour must be 0
    # and another +1 because??? it doesn't work otherwise...
    x = np.asanyarray(x)
    if (
        not any(np.issubdtype(x.dtype, dt) for dt in (np.integer, float))
        or not np.isfinite(x).any()
    ):
        return np.array([]), np.array([])
    count, edges = np.histogram(
        x,
        bins=np.arange(np.nanmin(x) - 3, np.nanmax(x) + 3, 1),
    )
    find_peaks_kwargs = kwargs.copy()
    find_peaks_kwargs.setdefault("width", 1)
    find_peaks_kwargs.setdefault("rel_height", 1)
    if rel_prominence is not None:
        # Just increase any already given prominence values
        find_peaks_kwargs.update(
            prominence=np.max(
                np.vstack(
                    np.broadcast_arrays(
                        find_peaks_kwargs.get("prominence", 0),
                        count * rel_prominence,
                    )
                ),
                axis=0,
            )
        )
    peak_positions, peak_properties = scipy.signal.find_peaks(
        count, **find_peaks_kwargs
    )
    return edges[:-1][peak_positions], count[peak_positions]


@ParmesanAccessor.register
def find_conspicuous(x, *args, **kwargs):
    """
    Use :func:`find_conspicuous_values` to find which values are conspicuous

    Args:
        args, kwargs: Arguments forwarded to :func:`find_conspicuous_values`

    Returns:
        boolean mask indicating conspicuous values
    """
    if isinstance(x, pd.DataFrame):
        return x.transform(lambda s: find_conspicuous(s, *args, **kwargs))
    conspicuous_values, count = find_conspicuous_values(x, *args, **kwargs)
    if hasattr(x, "isin"):
        return x.isin(conspicuous_values)
    return np.isin(x, conspicuous_values)


@ParmesanAccessor.register
def drop_conspicuous_values(x, *args, **kwargs):
    """
    Use :func:`find_conspicuous` to drop values.

    Args:
        args, kwargs: Arguments forwarded to :func:`find_conspicuous_values`
    """
    conspicuous = find_conspicuous(x, *args, **kwargs)
    if isinstance(conspicuous, pd.DataFrame):
        conspicuous = np.logical_or.reduce(tuple(dict(conspicuous).values()))
    return x[~conspicuous]


@ParmesanAccessor.register
def replace_conspicuous_values(x, replacement, *args, **kwargs):
    """
    Use :func:`find_conspicuous` to replace values

    Args:
        replacement: the value to replace with.
        args, kwargs: Arguments forwarded to :func:`find_conspicuous_values`
    """
    conspicuous = find_conspicuous(x, *args, **kwargs)
    tmp = x.copy()
    tmp[conspicuous] = replacement
    return tmp
