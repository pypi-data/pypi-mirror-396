# system modules

# internal modules
from parmesan.units import units
from parmesan import bounds
from parmesan.utils.function import FunctionCollection
from parmesan.stability import (
    monin_obukov_stability_function_heat_dyer_hicks,
    monin_obukov_length_from_virtual_potential_temperature_and_covariance,
)
from parmesan.symbols import *

# external modules


@from_sympy(
    result=K_eddy_mass,
    defaults={Φ_MO: 1},
    paramdoc={
        z: "height (e.g. geometric mean of lower and upper intake height)"
    },
)
def eddy_diffusivity_for_mass_aerodynamic_model_heat():
    r"""
    Turbulent exchange coefficient (aka. eddy diffusivity) after Zhao et. al
    (2019): https://doi.org/10.1016/j.agrformet.2019.05.032
    """
    return κ * u_star * z / Φ_MO_H


@from_sympy(result=F_mass)
def eddy_mass_flux_gradient_approach():
    """
    Eddy mass flux via flux-gradient approach. This is basically Fick's law
    applied to turbulent eddies transporting mass: a positive vertical gradient
    (i.e. ”*above is more than below*”) leads to a *downwards* (negative) flux.
    The eddy diffusivity links the two.
    """
    return -K_eddy_mass * dρTgasdz


@from_sympy(result=F_mass)
def eddy_mass_flux_gradient_approach_from_mass_density_differences():
    return eddy_mass_flux_gradient_approach.equation.subs(
        {dρTgasdz: Δzρ_Tgas / Δz}
    )


@from_sympy(result=F_mass, units_override=dict(_operate_without_units=True))
def eddy_mass_flux_gradient_approach_from_mass_density_differences_full_dyer_hicks():
    return (
        eddy_mass_flux_gradient_approach.equation.subs(
            {
                dρTgasdz: Δzρ_Tgas / Δz,
                eddy_diffusivity_for_mass_aerodynamic_model_heat.equation.lhs: eddy_diffusivity_for_mass_aerodynamic_model_heat.equation.rhs,
            }
        )
        .subs(
            monin_obukov_stability_function_heat_dyer_hicks.equation.lhs,
            monin_obukov_stability_function_heat_dyer_hicks.equation.rhs,
        )
        .subs(
            monin_obukov_length_from_virtual_potential_temperature_and_covariance.equation.lhs,
            monin_obukov_length_from_virtual_potential_temperature_and_covariance.equation.rhs,
        )
    )


@units.ensure(
    "kg * m^-2 * s^-1",
    c="ratio",
    rho_a="kg * m^-3",
    K="m^2 * s^-1",
    r_1="ratio",
    r_2="ratio",
    z_1="m",
    z_2="m",
)
@bounds.ensure(
    (None, None),
    c=(0, None),
    rho_a=(0, None),
    K=(None, None),
    r_1=(0, None),
    r_2=(0, None),
    z_1=(None, None),
    z_2=(None, None),
)
def dynamic_flux_molar(c, rho_a, K, r_1, r_2, z_1, z_2):
    r"""
    flux-gradient calcutation

    .. math::

        F = c \cdot \rho_\mathrm{a} \cdot K \cdot \frac{r_1 - r_2}{z_1 - z_2}

    Args:
        c : unit converation constant from molar to mass mixing ratio
        rho_a : air density
        K: eddy diffusivity
        r_1 : dry molar mixing ratio at height 1
        r_2 : dry molar mixing ratio at height 2
        z_1 : measurment height 1
        z_2 : measurment height 1

    Returns:
        float: dynamic flux-gradient

    https://glossary.ametsoc.org/wiki/Dynamic_flux
    https://www.e-education.psu.edu/meteo300/node/534
    https://www.sciencedirect.com/science/article/abs/pii/S0168192319302096
    """
    return c * rho_a * K * (r_1 - r_2) / (z_1 - z_2)


@units.ensure(
    "kg * m^-2 * s^-1",
    F="kg * m^-2 * s^-1",
    C_a1="ratio",
    C_a2="ratio",
    C_b1="ratio",
    C_b2="ratio",
)
@bounds.ensure(
    (None, None),
    F=(None, None),
    C_a1=(0, None),
    C_a2=(0, None),
    C_b1=(0, None),
    C_b2=(0, None),
)
def dynamic_flux_molar_MBR(F_b, C_a1, C_a2, C_b1, C_b2):
    r"""
    flux-gradient calcutation based on the modified Bowen-ratio model

    .. math::

        F_\mathrm{b} = F_a \cdot \frac{C_\mathrm{b_2} - C_\mathrm{b_1}}{C_\mathrm{a_2} - C_\mathrm{a_1}}

    Args:
        F_a: Flux constitute "a"
        C_a2 : mass mixing ratio of constitute "a" at measurment height 2;
            upper intake
        C_a1 : mass mixing ratio of constitute "a" at measurment height 1;
            lower intake
        C_b2 : mass mixing ratio of constitute "b" at measurment height 2;
            upper intake
        C_b1 : mass mixing ratio of constitute "b" at measurment height 1;
            lower intak

    Returns:
        float: dynamic flux-gradient of constitute "b"

    https://www.sciencedirect.com/science/article/pii/1352231096000829
    https://www.sciencedirect.com/science/article/abs/pii/S0168192319302096
    """
    return F_a * (C_b2 - C_b1) / (C_a2 - C_a1)


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
