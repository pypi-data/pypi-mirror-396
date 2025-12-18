# system modules

# internal modules
from parmesan.symbols import *

# external modules
import sympy


@from_sympy(result=irradiance)
def blackbody_radiation():
    r"""
    Calculate the total emitted radiation for a blackbody surface at a given
    temperature according to the Stefan-Boltzmann law
    """
    return σ_SB * T_surf**4


@from_sympy(result=irradiance)
def graybody_radiation():
    r"""
    Calculate the total emitted radiation for a gray body with a certain
    emissivity at a given surface temperature according to the Stefan-Boltzmann
    law
    """
    return ε * blackbody_radiation.equation.rhs


@from_sympy(result=T_surf_adj)
def adjust_radiation_temperature_to_other_emissivity():
    r"""
    Given a radiation temperature :math:`T_surf` that
    was obtained using an emissivity of :math:`\epsilon_\mathrm{1}`, calculate
    an adjusted radiation temperature :math:`T_\mathrm{surf,adj}` that would
    have been obtained if the emissivity had been :math:`\epsilon_\mathrm{2}`,
    optionally taking the reflected ambient radiation temperature :math:`T_amb`
    into account:
    """
    return (
        ((ε_1 * T_surf**4) - (1 - ε_2) * T_amb**4) / ε_2
    ) ** sympy.Rational(1, 4)


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
