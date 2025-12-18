# system modules
import functools
import textwrap
import inspect
import csv
import logging
import types
import io
import contextvars
from contextlib import contextmanager

# internal modules;-
from parmesan import utils
from parmesan.utils.mode import Mode

# external modules
import pint
import pint_pandas
from pint_pandas import PintArray
import numpy as np


logger = logging.getLogger(__name__)

mode = Mode(states={None, "implicit", "explicit"}, default="implicit")
"""
When unit mode state is set to ``"explicit"``, :func:`units.ensure` requires
that all specified arguments given to the decorated function have a
:class:`pint.unit.Unit` associated. Otherwise, an error will be raised.

With unit mode ``"implicit"`` (the default), arguments without units
automatically get the desired unit associated.

With unit mode set to ``None`` unit checking is disabled completely. Use this
if there are weird casting problems and you are sure that you provide the input
in the right unit.

It is strongly recommended to active ``explicit`` unit mode.

The unit mode can be set globally with

.. code-block:: python

    # disable unit checking
    parmesan.units.mode.state = None
    # enable automatic unit conversion
    parmesan.units.mode.state = "implicit"
    # enable explicit unit checking
    parmesan.units.mode.state = "explicit"

The unit mode can also be set temporarily for a block of code:

.. code-block:: python

    # temporarily disable unit mode
    with parmesan.units.unit_mode(None):
        # ... code here is executed with loose unit mode
"""

units = pint.UnitRegistry()
"""
The unit registry for :mod:`PARMESAN`.

This unit registry has a couple more units defined:

- fractions, ratios and percentages
- gas particle ratios like ppm, ppt, ppb

"""

units.define("fraction = [] = ratio")
# Can't use the %-sign as short form for 'percent', numerous problems with modulo operator clash...
units.define("percent = 1e-2 fraction")
units.define("ppt = 1e-3 fraction")
units.define("ppm = 1e-6 fraction")
units.define("ppb = 1e-9 fraction")


def add_as_units_method(fun):
    """
    Adds the given (or decorated) function as method to the
    :any:`parmesan.units.units` registry.
    """
    setattr(units, fun.__name__, types.MethodType(fun, units))


def ensure(
    return_unit,
    _units=units,
    _operate_without_units=False,
    _update_docstring=True,
    **argument_units,
):
    """
    Decorator to transparently teach a function what :class:`pint.unit.Unit` s
    its arguments should have. Depending on the current :any:`mode`
    state, the returned function behaves differently:

    ``"implicit"`` (the default)
        Arguments to the decorated function without unit are silently turned
        into a :class:`pint.quantity.Quantity` of the specified unit.

    ``"explicit"``
        Arguments **must** be given as :class:`pint.quantity.Quantity` with a
        *compatible* unit as they will be converted to the target unit,
        otherwise a :class:`ValueError` is raised.

    ``None``
        Disable unit checking completely.

    This is an improved reimplementation of :meth:`pint.UnitRegistry.wraps`.

    A pretty-formated table detailing the units is prepended to the decorated
    function's docstring.


    .. versionadded:: 2.0

        The :any:`from_sympy` decorator automatically applies this decorator.

    .. versionadded:: 2.0

        Support for :mod:`pint_pandas` was added. When any of the input
        arguments is a :any:`PintArray`, a :any:`PintArray` will be returned.
        This enables having less units boilerplate when dealing with
        :any:`pandas.DataFrame`s:

        .. code-block:: python

            # make a dataframe with units attached
            df = pd.DataFrame(
                dict(
                    temperature=pd.Series([25, 30.2, 45], dtype="pint[°C]"),
                    pressure=[990, 995, 1000.1],
                )
            )
            # retroactively set units
            df["pressure"] = df["pressure"].astype("pint[hPa]")
            # 🎉 no need to strip the unit and no warning that unit is stripped
            df["Tpot"] = parmesan.gas.temperature.potential_temperature(
                # 🎉 no need to multiply/set the units for each argument!
                temperature=df["temperature"], pressure=df["pressure"]
            )


    Args:
        return_unit: the unit of the return value
        _units (pint.UnitRegistry, optional): the unit registry to use.
            Defaults to :any:`parmesan.units.units`.
        _operate_without_units (bool, optional): set this to ``True`` if your
            decorated function is problematic to implement with handling units,
            e.g. if it is a weird parametrisation on °C values (like the Magnus
            formula for saturation water vapour pressure). This will cause all
            units to be stripped off the inputs and the result to be
            force-converted to ``return_unit``.
        _update_docstring (bool, optional): whether to add a table of units to
            the decorated function's docstring. Defaults to ``True``.
        **argument_units: mapping of argument names to unit definitions

    Example
    =======

    .. code-block:: python

        import parmesan
        from parmesan import units

        @units.ensure(
            temperature="kelvin",
            density="kg/m^3",
            gas_constant="J / ( kg * kelvin )",
        )
        def calculate_pressure(temperature, density, gas_constant):
            # ideal gas law
            return density * gas_constant * temperature

        # arguments without units are automatically converted
        print(calculate_pressure(300, 1.2, 287).to("hPa"))
        # 1033.2 hectopascal

        # invalid units raise an error
        calculate_pressure(300 * units.pascal, 1.2, 287)
        # ValueError: pascal couldn't be converted to kelvin

        # With explicit unit mode enabled, all arguments need to have a unit
        with parmesan.units.explicit_unit_mode.enabled():
            calculate_pressure(300, 1.2, 287).to("hPa")
            # ValueError: With explicit unit mode enabled temperature=300 needs
            # to be specified with a unit compatible to 'kelvin'
    """
    for arg, unit in argument_units.items():
        try:
            _units.Unit(unit)
        except BaseException as e:
            raise ValueError(
                "@units.ensure(): {decorated_fun.__name__}(): "
                "{}={} is not a pint unit: {}".format(arg, repr(unit), e)
            )

    def decorator(decorated_fun):
        signature = inspect.signature(decorated_fun)

        @functools.wraps(decorated_fun)
        def wrapper(*args, **kwargs):
            if mode.state is None:
                return decorated_fun(*args, **kwargs)
            try:
                bound_args = signature.bind(*args, **kwargs)
            except Exception as e:
                raise Exception(
                    f"@units.ensure(): {decorated_fun.__name__}(): {e}"
                ) from e
            bound_args.apply_defaults()
            arguments = bound_args.arguments
            to_pint_pandas_array = False
            for arg, value in arguments.items():
                should_be_unit = argument_units.get(arg)
                if should_be_unit is None:
                    # never mind if argument was not specified
                    continue
                if not hasattr(value, "units") and (
                    p := getattr(value, "pint", None)
                ):
                    to_pint_pandas_array = True
                    value = p.quantity
                elif hasattr(value, "units") and hasattr(value, "quantity"):
                    to_pint_pandas_array = True
                    value = value.quantity
                if not hasattr(value, "units"):
                    if mode.state == "explicit":
                        raise ValueError(
                            f"@units.ensure(): {decorated_fun.__name__}(): "
                            f"With unit mode {repr(mode.state)} "
                            f" argument {arg}={repr(value)} "
                            f"needs to be specified with a "
                            f"unit compatible to "
                            f"{units.Unit(should_be_unit):P}"
                        )
                    else:
                        try:
                            arguments[arg] = _units.Quantity(
                                getattr(value, "values", value), should_be_unit
                            )
                        except TypeError as e1:
                            try:
                                arguments[arg] = (
                                    getattr(value, "values", value)
                                    * should_be_unit
                                )
                            except BaseException as e2:
                                raise TypeError(
                                    f"@units.ensure(): {decorated_fun.__name__}(): "
                                    "It is not possible to "
                                    "add a unit to this:"
                                    "\n\n{}\n\nError: {} and {}".format(
                                        repr(value), repr(e1), repr(e2)
                                    )
                                )
                        continue
                try:
                    arguments[arg] = value.to(should_be_unit)
                except BaseException as e:
                    raise ValueError(
                        f"@units.ensure(): {decorated_fun.__name__}(): "
                        f"{arg}={repr(value)} could not be converted to "
                        f"{units.Unit(should_be_unit):P}: {e}"
                    )
            if _operate_without_units:
                arguments = {
                    k: getattr(v, "m", v) for k, v in arguments.items()
                }
            return_value = decorated_fun(**arguments)
            if _operate_without_units:
                if hasattr(return_value, "to"):
                    warnings.warn(
                        f"@units.ensure: {decorated_fun.__name__} result has unit {return_value.u!r} "
                        f"although {_operate_without_units=}. Reinterpreting it as {return_unit!r}.",
                        ParmesanWarning,
                    )
                    return_value = return_value.m
                return_value = units.Quantity(return_value, return_unit)

            if mode.state is not None and return_unit is not None:
                if hasattr(return_value, "to"):
                    return_value = return_value.to(return_unit)
                if to_pint_pandas_array:
                    with utils.out_warnings(pint.UnitStrippedWarning):
                        return_value = np.asarray(return_value).reshape(-1)
                    return_value = PintArray(return_value, return_unit)
                else:
                    return_value = units.Quantity(return_value, return_unit)

            return return_value

        if _update_docstring:
            docbuf = io.StringIO()
            writer = csv.DictWriter(
                docbuf,
                fieldnames=["Argument", "Unit"],
                quoting=csv.QUOTE_ALL,
                lineterminator="\n",
            )
            docbuf.write(":header: ")
            writer.writeheader()
            docbuf.write("\n")

            for arg, unit in argument_units.items():
                writer.writerow(
                    {
                        "Argument": "``{}``".format(arg),
                        "Unit": ":math:`{}`".format(
                            r"{:~L}".format(_units.Unit(unit))
                            or r"\mathrm{unitless}"
                        ),
                    }
                )

            wrapper.__doc__ = utils.string.add_to_docstring(
                docstring=getattr(wrapper, "__doc__", "") or "",
                extra_doc=(
                    textwrap.dedent(
                        """

                .. csv-table:: {title}. Arguments will be converted to the below units:
                {csv_table}

                """
                    )
                    if argument_units
                    else "{title}"
                ).format(
                    title="This function is decorated with "
                    ":any:`units.ensure` "
                    + (
                        "and returns values "
                        "with unit :math:`{return_unit}`".format(
                            return_unit="{:~L}".format(
                                _units.Unit(return_unit)
                            )
                            or r"\mathrm{unitless}"
                        )
                        if return_unit
                        else ""
                    ),
                    csv_table=textwrap.indent(
                        docbuf.getvalue(), prefix="    "
                    ),
                ),
                prepend=True,
            )

        return wrapper

    return decorator


@add_as_units_method
@functools.wraps(ensure)
def ensure_monkeypatched(self, *args, **kwargs):
    return ensure(*args, _units=self, **kwargs)


def transfer(x, units=units):
    """
    Transfer a quantity to another :any:`pint.UnitRegistry`.

    .. hint::

        Use this to interface with :any:`metpy`:

        .. code-block::

            import metpy.units
            import metpy.calc
            import parmesan.units

            T = parmesan.units.Quantity(25,"°C")
            metpy.calc.parmesan.units.transfer(T,metpy.units.units)


    Args:
        x (pint.Quantity): the quantity to convert
        _units (pint.UnitRegistry): the unit registry to convert to

    Returns:
        pint.Quantity : converted quantity
    """
    return (
        x
        if getattr(x, "_REGISTRY", None) is units
        else units.Quantity(x.m, str(x.u))
    )


@add_as_units_method
@functools.wraps(transfer)
def transfer_monkeypatched(self, *args, **kwargs):
    return transfer(*args, units=self, **kwargs)


# Use our units also for pint-pandas
pint_pandas.PintType.ureg = units

# Make pandas objects with units attached play nicely with matplotlib
# can be disabled with `units.setup_matplotlib(False)` later
units.setup_matplotlib()

# Condensed format by default
units.default_format = "P~"
