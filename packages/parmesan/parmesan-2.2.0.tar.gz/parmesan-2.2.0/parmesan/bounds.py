# system modules
import functools
import inspect
import re
import io
import warnings
import textwrap
import csv

# internal modules
from parmesan.errors import OutOfBoundsWarning, OutOfBoundsError
from parmesan.units import units
from parmesan import utils
from parmesan.utils import out_warnings

# external modules
import pint
import numpy as np


def bounds_formatted(bounds):  # ignore in tests
    """
    Pretty-format a given bounds specification for human-readable printing.
    """
    if hasattr(bounds, "__call__"):
        # return the first line of the docstring if available
        docstring = getattr(bounds, "__doc__", "") or ""
        if docstring:
            return (
                next(
                    map(
                        str.strip,
                        re.split(r"[\r\n]+", docstring),
                        "a custom function",
                    )
                )
                or "a custom function"
            )
        # if no docstring is available, try to extract the code
        src = inspect.getsource(bounds)
        sensible_lines = "\n".join(
            filter(bool, map(str.strip, re.split(r"[\r\n]+", src)))
        )
        if len(sensible_lines.split("\n")) == 1:
            return sensible_lines
        # otherwise return a generic text
        return "a custom function"
    try:
        if tuple(bounds) == (0, None):
            return "positive"
        elif tuple(bounds) == (None, 0):
            return "negative"
        else:
            return f"between {bounds[0]} and {bounds[1]}"
    except Exception:
        return str(bounds)


def bounds_checker(bounds=None):
    r"""
    Given a bounds specification, create a function that - given a value to
    check as first argument and other additional positional or keyword
    arguments -  will return a boolean (array) indicating which values are
    inside the bounds.

    The bounds are **inclusive**.

    Args:
        bounds: the bounds specification. Either a numeric sequence
            ``(lower,upper)`` or a callable taking the value to check (and
            possibly arbitrary other arguments) as argument. The callable will
            be :any:`numpy.vectorize` ed if it is not yet already, meaning the
            callable can be written for a single value and doesn't need to
            handle arrays.

            .. note::

                Note that :any:`bounds.ensure` will redirect **all** arguments
                the decorated function recieves to the callable generated with
                :any:`bounds_checker`. This means you should use a generic
                variable name when specifying a callable:

                .. code-block:: python

                    # We want to make sure that a positive temperature is
                    # specified
                    @ensure.bounds(
                        None, # not return value bounds

                        # the below would not work, as temperature=... will
                        # also be specified as keyword argument, thus raising a
                        # duplicate argument error:

                        # temperature = \
                        #    lambda temperature, *a, **kw: temperature > 0

                        # instead: use a generic argument name that is not used
                        # in the decorated function (e.g. 'x' here)
                        temperature = lambda x, *a, **kw: x > 0
                    )
                    def func(temperature,pressure):
                        return ...

    Returns:
        callable : Callable function to check bounds. Takes the value to check
        as first argument and arbitrary other arguments.

    Example
    -------

    .. code-block:: python

        import numpy as np
        from parmesan.bounds import bounds_checker

        # given a numeric bounds sequence
        checker = bounds_checker([2,6])
        checker(np.arange(8))
        # [False False  True  True  True  True  True False]

        # given a function that determines if inside bounds
        # (The function should accept any arguments,
        # so make sure to include *args and **kwargs.)
        checker = bounds_checker(lambda x,t: np.sqrt(x) < t)
        checker(np.array([1,2,3,4,7,9,10]), t=3)
        # [ True  True  True  True  True False False]


    """
    if bounds is None:
        return lambda __v, *a, **kw: True
    try:
        bounds_iter = iter(bounds)
        lower_bound = next(bounds_iter, float("-inf"))
        lower_bound = (
            float("-inf") if lower_bound is None else float(lower_bound)
        )
        upper_bound = next(bounds_iter, float("inf"))
        upper_bound = (
            float("inf") if upper_bound is None else float(upper_bound)
        )
        bounds_checker = np.vectorize(
            lambda __v, *a, **kw: lower_bound <= __v and __v <= upper_bound,
            otypes=(bool,),
        )
    except (ValueError, TypeError):
        if not hasattr(bounds, "__call__"):
            raise ValueError(
                f"bounds={repr(bounds)} is neither "
                "a numeric sequence (lower,upper) nor a callable."
            )
        if isinstance(bounds, np.vectorize) or isinstance(bounds, np.ufunc):
            bounds_checker = bounds
        else:
            bounds_checker = functools.wraps(bounds)(
                np.vectorize(bounds, otypes=(bool,))
            )
    return bounds_checker


mode = utils.mode.Mode(states={None, "warning", "strict"}, default="warning")
"""
The bounds mode determines the behaviour of :func:`bounds.ensure`:

When bounds mode state is set to ``"strict"``, :func:`bounds.ensure` requires
that all specified arguments given to the decorated function lie within the
specified bounds. Otherwise, an :class:`OutOfBoundsError` will be raised.

With unit mode ``"warning"`` (the default), a :class:`OutOfBoundsWarning` will
be shown for values outside their bounds.

With unit mode set to ``None`` bounds checking is disabled completely. Use this
to increase performance and you are sure that you the values are in their
correct bounds.

It is strongly recommended to active ``strict`` bounds mode.

The bounds mode can be set globally with

.. code-block:: python

    # disable bounds checking
    parmesan.bounds.mode.state = None
    # enable loose bounds checking
    parmesan.bounds.mode.state = "warning"
    # enable strict bounds checking
    parmesan.bounds.mode.state = "strict"

The bounds mode can also be set temporarily for a block of code:

.. code-block:: python

    # temporarily disable bounds checking
    with parmesan.bounds.mode(None):
        # ... code here is executed without bounds checking
"""


def ensure(return_bounds, _update_docstring=True, **argument_bounds):
    """
    Decorator to ensure bounds on arguments and return value of a function
    depending on the current state of :any:`bounds.mode`:

    ``"warning"`` (the default)
        If any input or output values are out of their respective bounds, an
        :class:`OutOfBoundsWarning` is shown.

    ``"explicit"``
        If any input or output values are out of their respective bounds, an
        :class:`OutOfBoundsError` is raised.

    ``None``
        No bounds checking is performed; the decorated function is called
        without any checks.

    See :func:`bounds_checker` for how to specify the bounds.

    A pretty-formated table detailing the bounds is prepended to the decorated
    function's docstring.

    Args:
        return_bounds: the bounds for the return value
        _update_docstring (bool, optional): whether to add a table of bounds to
            the decorated function's docstring. Defaults to ``True``.
        **argument_bounds: bounds for specific keyword arguments

    .. versionadded:: 2.0

        The :any:`from_sympy` decorator automatically applies this decorator.

    .. warning::

        This decorator is **not** :mod:`pint`-units-aware, i.e. it silently
        strips the unit.  This means that if you want to combine it with
        :func:`bounds.ensure`, you should apply the decorators in the following
        order:

        .. code-block:: python

            from parmesan import bounds

            @units.ensure(...)   # units.ensure first gets the units right
            @bounds.ensure(...)  # bounds.ensure only cares about the magnitude
            def myfunc(a,b,c=1):
                return a + b - c

    The following exceptions/warnings are raised depending on
    :any:`bounds.mode`. If :any:`bounds.mode` is set to ``None``, the decorated
    function is called without any checks.

    Raises:

        OutOfBoundsWarning : if :any:`bounds.mode` state is set to
            ``"warning"``

        OutOfBoundsError : if :any:`bounds.mode` state is set to ``"strict"``
    """

    def decorator(decorated_fun):
        signature = inspect.signature(decorated_fun)

        argument_bounds_checkers = {
            arg: bounds_checker(bounds)
            for arg, bounds in argument_bounds.items()
        }

        return_value_checker = bounds_checker(return_bounds)

        @functools.wraps(decorated_fun)
        def wrapper(*args, **kwargs):
            if mode.state is None:
                return decorated_fun(*args, **kwargs)
            try:
                bound_args = signature.bind(*args, **kwargs)
            except Exception as e:
                raise Exception(
                    f"@bounds.ensure(): {decorated_fun.__name__}(): {e}"
                ) from e
            bound_args.apply_defaults()
            arguments = bound_args.arguments
            for arg, value in arguments.items():
                if arg not in argument_bounds_checkers:
                    continue
                with out_warnings(
                    pint.UnitStrippedWarning,
                    RuntimeWarning,
                    DeprecationWarning,
                ):
                    outliers = np.invert(
                        argument_bounds_checkers[arg](value, *args, **kwargs)
                    )
                    value_array = np.asarray(value)
                    nans = np.isnan(value_array)
                    real_outliers = np.logical_and(outliers, ~nans)
                    n_outliers = np.nansum(real_outliers)
                    outlier_indices = np.where(np.atleast_1d(real_outliers))[0]
                    if n_outliers > 0:
                        msg = (
                            f"{n_outliers} of {outliers.size} "
                            f"input values to {decorated_fun.__name__} "
                            f"for argument {repr(arg)} "
                            f"are out of bounds defined by "
                            f"{repr(bounds_formatted(argument_bounds[arg]))}: "
                            f"{value_array[real_outliers]} "
                            f"at indices {outlier_indices}"
                        )
                        if mode.state == "warning":
                            warnings.warn(
                                msg,
                                category=OutOfBoundsWarning,
                            )
                        elif mode.state == "strict":
                            raise OutOfBoundsError(msg)

            return_value = decorated_fun(*args, **kwargs)
            with out_warnings(
                pint.UnitStrippedWarning, RuntimeWarning, DeprecationWarning
            ):
                try:
                    outliers = np.invert(
                        return_value_checker(return_value, *args, **kwargs)
                    )
                except Exception as e:
                    warnings.warn(
                        f"@bounds.ensure(): {decorated_fun.__name__}(): "
                        f"Can't check whether return value is within bounds "
                        f"{bounds_formatted(return_bounds)}:"
                        f"\n\n{e!r}\n\n"
                        f"This is the return value:\n\n{return_value!r}"
                    )
                return_value_array = np.asarray(return_value)
                nans = np.isnan(return_value_array)
                real_outliers = np.logical_and(outliers, ~nans)
                n_outliers = np.nansum(real_outliers)
                outlier_indices = np.where(np.atleast_1d(real_outliers))[0]
                if n_outliers > 0:
                    msg = (
                        f"{n_outliers} of {outliers.size} "
                        f"return values from {decorated_fun.__name__} "
                        f"are out of bounds defined by "
                        f"{repr(bounds_formatted(return_bounds))} "
                        f"{return_value_array[real_outliers]} "
                        f"at indices {outlier_indices}"
                    )
                    if mode.state == "warning":
                        warnings.warn(
                            msg,
                            category=OutOfBoundsWarning,
                        )
                    elif mode.state == "strict":
                        raise OutOfBoundsError(msg)

            return return_value

        if _update_docstring:
            docbuf = io.StringIO()
            writer = csv.DictWriter(
                docbuf,
                fieldnames=["Argument", "Bounds"],
                quoting=csv.QUOTE_ALL,
                lineterminator="\n",
            )
            docbuf.write(":header: ")
            writer.writeheader()
            docbuf.write("\n")

            for arg, bounds in argument_bounds.items():
                writer.writerow(
                    {
                        "Argument": "``{}``".format(arg),
                        "Bounds": bounds_formatted(bounds),
                    }
                )

            wrapper.__doc__ = utils.string.add_to_docstring(
                docstring=getattr(wrapper, "__doc__", "") or "",
                extra_doc=(
                    textwrap.dedent(
                        """

                .. csv-table:: {title}. Arguments are bounded by:
                {csv_table}

                """
                    )
                    if argument_bounds
                    else "{title}"
                ).format(
                    title="This function is decorated "
                    "with :any:`bounds.ensure` and "
                    "has a return value bounded by {}"
                    "".format(bounds_formatted(return_bounds)),
                    csv_table=textwrap.indent(
                        docbuf.getvalue(), prefix="    "
                    ),
                ),
                prepend=True,
            )

        return wrapper

    return decorator


def smaller_than(arg):
    """
    Utility function to use in :any:`bounds.ensure` for arguments that should
    be smaller than another argument.

    Args:
        arg (str): the other argument to compare against
    """
    return utils.doc((lambda x, *a, **kw: x <= kw[arg]), f"smaller than {arg}")
