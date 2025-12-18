# system modules
import warnings

# internal modules
from parmesan.units import units
from parmesan import bounds
from parmesan.utils.function import FunctionCollection
from parmesan.symbols import *

# external modules
import numpy as np

reynolds_number = FunctionCollection()
"""
Collection of functions to calculate the reynolds number
"""


@reynolds_number.register
@from_sympy()
def reynolds_number_from_dynamic_viscosity():
    return ρ * U_char * L_char / dynamic_viscosity


@reynolds_number.register
@from_sympy()
def reynolds_number_from_kinematic_viscosity():
    return U_char * L_char / kinematic_viscosity


turbulence_kinetic_energy = FunctionCollection()
r"""
Collection of functions to calculate the turbulence kinetic energy :math:`k`

.. note::

    Note that calling this returns a different unit depending on the inputs you
    give it. See the actual implementations for the TKE below:
    :any:`turbulence_kinetic_energy_per_unit_volume`,
    :any:`turbulence_kinetic_energy_per_unit_mass`.

"""

tke = turbulence_kinetic_energy
r"""
Shorthand for :any:`turbulence_kinetic_energy`
"""


@turbulence_kinetic_energy.register
@units.ensure("J / kg", u="m/s", v="m/s", w="m/s")
@bounds.ensure([0, None], density=[0, None])
def turbulence_kinetic_energy_per_unit_mass(u, v, w):
    r"""
    Calculate the turbulence kinetic energy (TKE) per unit mass given
    timeseries of all three wind vector components :math:`u`, :math:`v`,
    :math:`w`:

    .. math::

        k = \frac{1}{2}
            \left(
                \overline{(u')^2} + \overline{(v')^2} + \overline{(w')^2}
            \right)

    .. note::

        Consider detrending the input wind vector components with
        :any:`scipy.signal.detrend`.

    Args:
        u, v, w: wind vector component timeseries

    Returns:
        float: the turbulence kinetic energy per unit mass
    """
    return (np.var(u) + np.var(v) + np.var(w)) / 2


@turbulence_kinetic_energy.register
@units.ensure("J / m³", u="m/s", v="m/s", w="m/s", density="kg/m³")
@bounds.ensure([0, None], density=[0, None])
def turbulence_kinetic_energy_per_unit_volume(u, v, w, density):
    r"""
    Calculate the turbulence kinetic energy (TKE) per unit mass given
    timeseries of all three wind vector components :math:`u`, :math:`v`,
    :math:`w` and the density :math:`\rho`:

    .. math::

        k = \frac{\rho}{2}
            \left(
                \overline{(u')^2} + \overline{(v')^2} + \overline{(w')^2}
            \right)

    .. note::

        Consider detrending the input wind vector components with
        :any:`scipy.signal.detrend`.


    Args:
        u, v, w: wind vector component timeseries
        density: the air mass density

    Returns:
        float: the turbulence kinetic energy per unit volume
    """
    return density * turbulence_kinetic_energy_per_unit_mass(u=u, v=v, w=w)


@units.ensure("dimensionless", u="m/s", v="m/s")
@bounds.ensure([0, None])
def turbulence_intensity(u, v):
    r"""
    Calculate the turbulence intensity (TI) from a given
    timeseries of all horizontal wind vector components :math:`u`, :math:`v`:

    .. math::

        \mathrm{TI} = \dfrac{
            \sigma \left( \sqrt( u^2+ v^2 )\right)
            }
            {
            \overline{ \sqrt( u^2 + v^2 )}
            }

    .. note::

        The TI is only calculated with regards to the horizontal wind.

    Args:
        u, v: wind vector component timeseries

    Returns:
        float: the dimensionless turbulence intensity
    """
    return np.sqrt(np.var(np.sqrt(u**2 + v**2))) / np.mean(
        np.sqrt(u**2 + v**2)
    )


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
