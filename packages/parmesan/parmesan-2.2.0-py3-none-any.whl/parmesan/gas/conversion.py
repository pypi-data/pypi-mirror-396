# system modules

# internal modules
from parmesan.symbols import *
from parmesan.errors import deprecated

# external modules


@from_sympy()
def trace_gas_dry_molar_mixing_ratio_from_molar_fraction():
    return X_Tgas / (1 - X_Tgases)


@from_sympy()
def trace_gas_molar_mixing_ratio_from_molar_fraction():
    return (
        trace_gas_dry_molar_mixing_ratio_from_molar_fraction.equation.rhs.subs(
            X_Tgases, X_Tgas
        )
    )


@from_sympy(rearrange_from=trace_gas_molar_mixing_ratio_from_molar_fraction)
def trace_gas_molar_fraction_from_molar_mixing_ratio():
    return r_Tgas / (1 + r_Tgas)


@from_sympy()
def trace_gas_mass_density_from_molar_fraction():
    """
    https://gitlab.com/tue-umphy/co2mofetten/co2mofetten-project/-/wikis/Gas-Calculations
    """
    return X_Tgas * p / (R_s * T)


@deprecated(
    since="2.2",
    note="use :any:`trace_gas_mass_density_from_molar_fraction` instead, which has more consistent naming",
)
def trace_gas_mass_density_from_particle_ratio(*args, **kwargs):
    return trace_gas_mass_density_from_molar_fraction(*args, **kwargs)


@from_sympy(
    result=X_Tgas, rearrange_from=trace_gas_mass_density_from_molar_fraction
)
def trace_gas_molar_fraction_from_mass_density():
    """
    https://gitlab.com/tue-umphy/co2mofetten/co2mofetten-project/-/wikis/Gas-Calculations
    """
    pass


@deprecated(
    since="2.2",
    note="use :any:`trace_gas_molar_fraction_from_mass_density` instead, which has more consistent naming",
)
def trace_gas_particle_ratio_from_mass_density(*args, **kwargs):
    return trace_gas_molar_fraction_from_mass_density(*args, **kwargs)


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
