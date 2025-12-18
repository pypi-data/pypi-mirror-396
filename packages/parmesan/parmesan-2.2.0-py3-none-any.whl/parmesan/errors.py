# system modules
import functools
import warnings

# internal modules
from parmesan.utils.string import add_to_docstring

# external modules


class ParmesanError(BaseException):
    """
    Base class for warnings raised by functions in the :mod:`parmesan` module.
    """


class OutOfBoundsError(ParmesanError):
    """
    Class for out-of-bounds errors
    """


class ParmesanWarning(UserWarning):
    """
    Base class for warnings raised by functions in the :mod:`parmesan` module.

    You can hide :class:`ParmesanWarning` s as usual in Python:

    .. code-block:: python

        import warnings
        warnings.filterwarnings(
            "ignore",
            category=parmesan.errors.ParmesanWarning
        )
    """


class OutOfBoundsWarning(ParmesanWarning):
    """
    Class for out-of-bounds warnings
    """


def deprecated(since="...", note=""):
    def decorator(decorated_fun):
        @functools.wraps(decorated_fun)
        def wrapper(*args, **kwargs):
            warnings.warn(
                note or f"{decorated_fun.__name__}() is deprecated.",
                category=DeprecationWarning,
            )
            return decorated_fun(*args, **kwargs)

        wrapper.__doc__ = add_to_docstring(
            wrapper.__doc__,
            f"""
        .. deprecated:: {since}
            {note}
        """,
        )
        return wrapper

    return decorator
