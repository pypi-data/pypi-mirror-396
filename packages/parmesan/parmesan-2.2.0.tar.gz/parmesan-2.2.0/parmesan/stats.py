# system modules

# internal modules

# external modules
import numpy as np


def rmse(x, y, average=np.nanmean):
    """
    Root-Average-Square-Error between two series

    Args:
        x,y: the series to compare
        average (callable, optional): the averaging function. Defaults to
            :any:`numpy.nanmean`.

            .. hint::

                Use :any:`numpy.nanmedian` for the Root-Median-Square-Error.

    Returns:
        float: the Root Average Square Error
    """
    return np.sqrt(average((x - y) ** 2))


def mae(x, y, average=np.nanmean):
    """
    Mean-Absolute-Error between two series

    Args:
        x,y: the series to compare
        average (callable, optional): the averaging function. Defaults to
            :any:`numpy.nanmean`.

            .. hint::

                Use :any:`numpy.nanmedian` for the Median-Absolute-Error.

    Returns:
        float: the Mean Absolute Error
    """
    return average(np.abs(x - y))


def geothmetic_meandian(x, threshold=1e-5):
    """
    Recursive averaging by arithmetic and geometric mean and median.

    Args:
        x (array-like): the input data to average
        threshold (float, optional): convergence threshold

    Returns:
        float : the geothmetic meandian

    .. note::

        Taken from XKCD: https://xkcd.com/2435/

        .. figure:: https://imgs.xkcd.com/comics/geothmetic_meandian.png
            :alt: Geothmetic Meandian definition from https://xkcd.com/2435/
            :target: https://xkcd.com/2435/
    """
    mean = np.mean(x)
    if (np.std(x) / mean) < threshold:  # converges
        return mean
    return geothmetic_meandian(
        (
            mean,  # arithmetic mean
            np.prod(x) ** (1 / len(x)),  # geometric mean
            np.median(x),  # median
        )
    )
