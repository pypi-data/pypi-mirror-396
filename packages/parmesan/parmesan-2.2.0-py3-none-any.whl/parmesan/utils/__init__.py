# system modules
import sys
import itertools
import inspect
import warnings
import functools
from contextlib import contextmanager
import logging

# internal modules
import parmesan.utils.string
import parmesan.utils.mode
import parmesan.utils.function

# external modules

logger = logging.getLogger(__name__)


@contextmanager
def out_warnings(*categories):
    """
    Context manager to ignore (certain) warnings. The name is just syntactic
    sugar so it reads nicely when used:

    .. code-block:: python

        with out_warnings(): # reads like "without warnings"
            ...
            # code here doesn't show warnings
            ...

    Args:
        categories (sequence of Warning, optional): the
            warning category/-ies to ignore. Defaults to the base class
            :any:`Warning`, effectively ignoring all warnings.
    """
    if not categories:
        categories = (Warning,)
    with warnings.catch_warnings():
        for cat in categories:
            warnings.simplefilter("ignore", cat)
        yield


def ignore_warnings(*categories):
    """
    Decorator for functions to ignore (certain) warnings.

    .. code-block:: python

        @ignore_warnings()
        def bla():
            # code here doesn't show any warnings

    Args:
        categories: see :func:`out_warnings`
    """

    def decorator(decorated_fun):
        @functools.wraps(decorated_fun)
        def wrapper(*args, **kwargs):
            with out_warnings(*categories):
                return decorated_fun(*args, **kwargs)

        return wrapper

    return decorator


def find_object(x):
    """
    Generator yielding tuples of module and variable name pointing to a given
    object.

    Args:
        x (object): the object to look for

    Yields:
        module_name, variable_name : the location of the variable
    """
    for module_name, module in sys.modules.copy().items():
        if module is None:
            continue  # skip unloaded / partial modules
        try:
            with out_warnings(DeprecationWarning, FutureWarning):
                for name, var in inspect.getmembers(module):
                    if var is x:
                        yield module_name, name
        except (ImportError, ModuleNotFoundError):
            # apparently, the 'six' package has 'lazy descriptors'
            # or something which can trigger here.
            # Ignoring those errors gets rid of the dreaded
            # ModuleNotFoundError: No such module '_gdbm' (or '_tkinter') errors
            continue
        except GeneratorExit:
            pass
        except Exception as e:
            logger.error(f"{type(e).__name__}: {e}")
            continue


def doc(x, s):
    """
    Set the docstring of a given object and return it
    """
    x.__doc__ = s
    return x


def is_iterable(x):
    """
    Check if a given object is iterable but not a string.
    """
    if isinstance(x, str):
        return False
    try:
        iter(x)
    except TypeError:
        return False
    return True


def single_argument_combinations(d):
    """
    Given a dict mapping argument names to (sequences of) possible values,
    return an iterable of all single argument combinations yielding :any:`dict`
    s with only one argument as key and the next value.

    For example:

    .. code-block:: python

        single_argument_combinations({"a":[1,2,3],"b":[4,5,6]})
        # yields sequentially
        {'a': 1}
        {'a': 2}
        {'a': 3}
        {'b': 4}
        {'b': 5}
        {'b': 6}
    """
    return (
        dict((t,))
        for t in itertools.chain.from_iterable(
            itertools.product((k,), v if is_iterable(v) else (v,))
            for k, v in d.items()
        )
    )


def all_argument_combinations(d):
    """
    Given a dict mapping argument names to (sequences of) possible values,
    return an iterable of all argument combinations yielding :any:`dict` s of
    the same size as the input but only one value.

    For example:

    .. code-block:: python

        all_argument_combinations({"a":[1,2,3],"b":[4,5,6]})
        # yields sequentially
        {'a': 1, 'b': 4}
        {'a': 1, 'b': 5}
        {'a': 1, 'b': 6}
        {'a': 2, 'b': 4}
        {'a': 2, 'b': 5}
        {'a': 2, 'b': 6}
        {'a': 3, 'b': 4}
        {'a': 3, 'b': 5}
        {'a': 3, 'b': 6}
    """
    return map(
        dict,
        itertools.product(
            *(
                (
                    itertools.product(
                        (arg,), values if is_iterable(values) else (values,)
                    )
                )
                for arg, values in d.items()
            )
        ),
    )
