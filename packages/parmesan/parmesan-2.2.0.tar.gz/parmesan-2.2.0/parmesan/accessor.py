# system modules
import types
import functools
import inspect
import textwrap
import re
import warnings
import logging

# internal modules
from parmesan import utils
from parmesan.errors import ParmesanWarning

# external modules
from pandas.api.extensions import (
    register_dataframe_accessor,
    register_series_accessor,
)
import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)

PARMESAN_ACCESSOR_NAME = "parmesan"
"""
The name under which the :class:`ParmesanAccessor` is registered with
:func:`pandas.api.extensions.register_dataframe_accessor`.
"""


@register_dataframe_accessor(PARMESAN_ACCESSOR_NAME)
@register_series_accessor(PARMESAN_ACCESSOR_NAME)
class ParmesanAccessor:
    """
    This is a :mod:`pandas.DataFrame`  and :mod:`pandas.Series` accessor,
    meaning :mod:`pandas.DataFrame`  and :mod:`pandas.Series` objects will get
    an attribute named like the content of :any:`PARMESAN_ACCESSOR_NAME`.
    """

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def whats_time_whats_data(cls, x, times=None):
        """
        Given an object and optionally times, determine what to use as data and
        what as times.

        If ``times`` is given specifically, it is used as times. Otherwise, if
        ``x`` is a :class:`pandas.DataFrame` or :class:`pandas.Series` and its
        index contains temporal data, the index is used as times. If that's not
        the case, for :any:`pandas.DataFrame`, if it contains only *one* column
        with temporal data, that is used.

        In all other cases, a :class:`ValueError` is raised.

        .. hint::

            This function is helpful to use in :any:`ParmesanAccessor.register`
            ed functions to support both :mod:`pandas` objects and
            :class:`numpy.ndarray` s.

        Args:
            x (pandas.DataFrame or pandas.Series or numpy.ndarray): given input
                object
            times (pandas.DatetimeIndex or datetime numpy.ndarray, optional):
                the times to use

        Returns:
            sequence: times, x  :  the times and data to use

        Raises:
            ValueError : If no times could be determined
        """
        if times is None:
            if hasattr(x, "index"):
                if x.index.dtype.type is np.datetime64 or "datetime64" in str(
                    x.index.dtype
                ):
                    times = x.index.to_series()
                elif isinstance(x, pd.DataFrame):
                    datetime_cols = {
                        n: c
                        for n, c in x.items()
                        if c.dtype.type == np.datetime64
                    }
                    if not datetime_cols:
                        raise ValueError(
                            "DataFrame neither has a "
                            "DateTimeIndex nor any datetime columns. "
                            "Please specify the times=... argument!"
                        )
                    elif len(datetime_cols) > 1:
                        raise ValueError(
                            "DataFrame has {} datetime columns ({}). "
                            "Please specify (one of these "
                            "as) the times=... argument!".format(
                                len(datetime_cols), ", ".join(datetime_cols)
                            )
                        )
                    times = next(iter(datetime_cols.values()))
                else:
                    raise ValueError(
                        "Please specify the times=... argument "
                        "or make the index a DataTimeIndex"
                    )
            else:
                raise ValueError("Please specify the times=... argument")
        elif isinstance(times, str):
            if isinstance(x, pd.DataFrame):
                if times not in x:
                    raise ValueError("x has no column {}".format(repr(times)))
                if x[times].dtype.type is not np.datetime64:
                    raise ValueError(
                        "column {} is not a datetime column".format(
                            repr(times)
                        )
                    )
                times = x[times]
            else:
                raise ValueError(
                    "x is no DataFrame. "
                    "Don't know how to use {} as times.".format(repr(times))
                )
        times_dtype = (
            times.dtype if hasattr(times, "dtype") else np.asarray(times)
        )
        if not (
            times_dtype.type is np.datetime64
            or "datetime64" in str(times_dtype)
        ):
            warnings.warn(
                "Given times {} don't have datetime type, "
                "assuming seconds".format(times),
                category=ParmesanWarning,
            )
            times = np.array(times, dtype="datetime64[s]")
        return times, x

    @classmethod
    def register(cls, decorated_function):
        """
        Add a function as method to this class, which when called is passed the
        pandas object as first argument.

        A usage hint is appended to the decorated function's docstring.

        .. hint::

            This can be used as a decorator:

            .. code-block:: python

                @ParmesanAccessor.register
                def my_function(dataframe, arg1, keywordarg=None):
                    ...
                    return dataframe.mean()

            Then, ``my_function`` can be applied directly from a
            :class:`pandas.DataFrame` or a :class:`pandas.Series`:

            .. code-block:: python

                df.parmesan.my_function(arg1=..., keywordarg=...)
        """
        if not hasattr(decorated_function, "__call__"):
            raise ValueError(
                "Decorated object {func.__name__} is not a function".format(
                    func=decorated_function
                )
            )
        if hasattr(cls, decorated_function.__name__):
            if hasattr(
                getattr(cls, decorated_function.__name__),
                "__parmesan_accessor_registered",
            ):
                warnings.warn(
                    "Overwriting {cls.__name__}.{func.__name__}".format(
                        cls=cls, func=decorated_function
                    ),
                    category=ParmesanWarning,
                )
            else:
                raise ValueError(
                    "{cls.__name__} already has an "
                    "attribute called {func.__name__}, "
                    "refuse to overwrite".format(
                        cls=cls, func=decorated_function
                    )
                )

        argspec = inspect.getfullargspec(decorated_function)

        if len(argspec.args) < 1:
            raise ValueError(
                "Decorated function {func.__name__} only takes {n} arguments, "
                "To be registered it needs to take "
                "the pandas object as first argument.".format(
                    func=decorated_function, n=len(argspec.args)
                )
            )

        decorated_function.__doc__ = utils.string.add_to_docstring(
            docstring=getattr(decorated_function, "__doc__", "") or "",
            extra_doc=textwrap.dedent(
                """
                .. hint::

                    This function from
                    :any:`{func.__module__}.{func.__name__}` is
                    :any:`ParmesanAccessor.register` ed, meaning you can
                    use it directly from a :class:`pandas.DataFrame` or
                    :class:`pandas.Series` like

                    .. code-block:: python

                        dataframe.{accessor_name}.{func.__name__}({args})
                        dataframe["column"].{accessor_name}.{func.__name__}({args})

                    However it is still usable as usual like

                    .. code-block:: python

                        from {func.__module__} import {func.__name__}
                        {func.__name__}(dataframe, {args})
                        {func.__name__}(dataframe["column"], {args})
                """.format(
                    accessor_name=PARMESAN_ACCESSOR_NAME,
                    func=decorated_function,
                    args=", ".join(
                        argspec.args[1:]
                        + (
                            ["..."]
                            if (argspec.varargs or argspec.varkw)
                            else []
                        )
                    ),
                ),
            ),
        )

        @functools.wraps(decorated_function)
        def wrapper(self, *args, **kwargs):
            return decorated_function(self.obj, *args, **kwargs)

        logger.debug(
            "Registering function {}".format(decorated_function.__name__)
        )
        setattr(cls, decorated_function.__name__, wrapper)
        setattr(decorated_function, "__parmesan_accessor_registered", True)
        setattr(wrapper, "__parmesan_accessor_registered", True)
        return decorated_function
