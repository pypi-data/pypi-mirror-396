# system modules
import logging
import warnings

# internal modules
from parmesan.symbols import *

# external modules
import numpy as np

logger = logging.getLogger(__name__)


@from_sympy(result=pressure)
def extrapolate_barometric_pressure_to_height_constant_temperature():
    r"""
    Extrapolate the barometric pressure, assuming a constant temperature profile

    https://en.wikipedia.org/wiki/Barometric_formula
    """
    return p_ref * sympy.exp(-g * (z - z_ref) / (R_dry * T_ref))


@from_sympy(result=pressure)
def extrapolate_barometric_pressure_to_height_linear_temperature():
    r"""
    Extrapolate the barometric pressure, assuming a linear temperature profile

    https://en.wikipedia.org/wiki/Barometric_formula
    """
    return p_ref * ((T_ref - (z - z_ref) * dTdz) / T_ref) ** (g / R_dry / dTdz)


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
