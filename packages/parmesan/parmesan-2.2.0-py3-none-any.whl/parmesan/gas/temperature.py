# system modules
import logging
import warnings

# internal modules
from parmesan.gas import humidity
from parmesan.errors import ParmesanWarning, ParmesanError
from parmesan import units
from parmesan import bounds
from parmesan import utils
from parmesan.symbols import *
from parmesan.utils.function import FunctionCollection

# external modules
import numpy as np
import pint
import sympy

logger = logging.getLogger(__name__)


virtual_temperature = FunctionCollection()
"""
Collection of functions to calculate virtual temperature
"""


@virtual_temperature.register
@from_sympy()
def virtual_temperature_from_specific_humidity():
    r"""
    Calculate the virtual temperature via the specific humidity.
    """
    return T * (1 + (R_h2o / R_dryair - 1) * q)


@virtual_temperature.register
@from_sympy()
def virtual_temperature_from_mixing_ratio():
    r"""
    Calculate the virtual temperature via the mixing_ratio.

    https://en.wikipedia.org/wiki/Virtual_temperature#Variations
    """
    ratio = R_dryair / R_h2o
    return T * (r + ratio) / (ratio * (1 + r))


@virtual_temperature.register
@from_sympy()
def virtual_temperature_from_pressures():
    r"""
    Calculate the virtual temperature via the atmospheric pressure and the
    water vapour pressure.

    https://en.wikipedia.org/wiki/Virtual_temperature#Variations
    """
    return T / (1 - e / p * (1 - R_dryair / R_h2o))


@virtual_temperature.register
@from_sympy(**humidity.magnus_overrides)
def virtual_temperature_from_relative_humidity():
    """
    Like :func:`virtual_temperature_from_pressures` but use
    :func:`water_vapour_pressure_over_water_magnus` to calculate the water
    vapour pressure.
    """
    return virtual_temperature_from_pressures.equation.subs(
        e, humidity.water_vapour_pressure_over_water_magnus.equation.rhs
    )


@virtual_temperature.register
@from_sympy()
def virtual_temperature_from_absolute_humidity():
    r"""
    Proxy for :any:`virtual_temperature_from_pressures`, calculating the water
    vapour pressure with :any:`water_vapour_pressure_via_gas_law`.

    https://en.wikipedia.org/wiki/Virtual_temperature#Variations
    """
    return virtual_temperature_from_pressures.equation.subs(
        water_vapour_pressure,
        humidity.water_vapour_pressure_via_gas_law.equation.rhs,
    )


@from_sympy(
    defaults={
        c_p: c_p_dryair.quantity,
        p_ref: units("1000 hPa").to("Pa"),
        R_s: R_dry.quantity,
    }
)
def potential_temperature():
    return T * (p_ref / p) ** (R_s / c_p)


virtual_potential_temperature = FunctionCollection()
"""
Collection of functions to calculate virtual potential temperature
"""


@virtual_potential_temperature.register
@from_sympy()
def virtual_potential_temperature_from_specific_humidity():
    """
    Apply :any:`virtual_potential_temperature_from_specific_humidity` to
    :any:`potential_temperature`.
    """
    return potential_temperature.equation.subs(
        {
            θ: θ_v,
            T: virtual_temperature_from_specific_humidity.equation.rhs,
            c_p: c_p_dryair,
            R_s: R_dry,
        }
    )


@virtual_potential_temperature.register
@from_sympy()
def virtual_potential_temperature_from_mixing_ratio():
    """
    Apply :any:`virtual_potential_temperature_from_mixing_ratio` to
    :any:`potential_temperature`.
    """
    return potential_temperature.equation.subs(
        {
            θ: θ_v,
            T: virtual_temperature_from_mixing_ratio.equation.rhs,
            c_p: c_p_dryair,
            R_s: R_dry,
        }
    )


@virtual_potential_temperature.register
@from_sympy(check_units=False)
def virtual_potential_temperature_from_relative_humidity():
    """
    Apply :any:`virtual_potential_temperature_from_relative_humidity` to
    :any:`potential_temperature`.
    """
    return potential_temperature.equation.subs(
        {
            θ: θ_v,
            T: virtual_temperature_from_relative_humidity.equation.rhs,
            c_p: c_p_dryair,
            R_s: R_dry,
        }
    )


@virtual_potential_temperature.register
@from_sympy()
def virtual_potential_temperature_from_absolute_humidity():
    """
    Apply :any:`virtual_potential_temperature_from_absolute_humidity` to
    :any:`potential_temperature`.
    """
    return potential_temperature.equation.subs(
        {
            θ: θ_v,
            T: virtual_temperature_from_absolute_humidity.equation.rhs,
            c_p: c_p_dryair,
            R_s: R_dry,
        }
    )


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
