# system modules

# internal modules
from parmesan.gas import laws
from parmesan.gas import temperature as _temperature
from parmesan.gas import humidity
from parmesan.utils.function import FunctionCollection
from parmesan.symbols import *

# external modules


density = FunctionCollection()
"""
Collection of functions to calculate density
"""


@density.register
@from_sympy(rearrange_from=laws.gas_law_meteorology.equation.subs(R_s, R_dry))
def density_dry_air():
    pass


@density.register
@from_sympy()
def density_humid_air_absolute_humidity():
    r"""
    Calculate the humid-air density :math:`\rho_\mathrm{air}` via the ideal gas
    law, using :any:`virtual_temperature_from_absolute_humidity` to include
    humidity effects in :any:`density_dry_air`.
    """
    return density_dry_air.equation.subs(
        T, _temperature.virtual_temperature_from_absolute_humidity.equation.rhs
    )


@density.register
@from_sympy()
def density_humid_air_relative_humidity():
    r"""
    Calculate the humid-air density :math:`\rho_\mathrm{air}` via the ideal gas
    law, using :any:`virtual_temperature_from_relative_humidity` to include
    humidity effects in :any:`density_dry_air`.
    """
    return density_dry_air.equation.subs(
        T, _temperature.virtual_temperature_from_relative_humidity.equation.rhs
    )


@density.register
@from_sympy()
def density_humid_air_from_mixing_ratio():
    r"""
    Calculate the humid-air density :math:`\rho_\mathrm{air}` via the ideal gas
    law, using :any:`virtual_temperature_from_mixing_ratio` to include
    humidity effects in :any:`density_dry_air`.
    """
    return density_dry_air.equation.subs(
        T, _temperature.virtual_temperature_from_mixing_ratio.equation.rhs
    )


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
