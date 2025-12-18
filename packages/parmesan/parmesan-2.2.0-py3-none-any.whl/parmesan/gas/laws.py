# system modules

# internal modules
from parmesan.symbols import *

# external modules
import sympy


@from_sympy()
def mass_from_mole():
    return n * molar_mass


@from_sympy()
def density_canonical():
    return m / V


@from_sympy()
def total_particle_count():
    return n * N_A


@from_sympy()
def specific_gas_constant_definition():
    return R / M


@from_sympy(result=R)
def gas_constant_definition():
    return N_A * k_B


gas_law_boltzmann_equation = sympy.Eq(p * V, N * k_B * T)
"""
Gas Law with the Boltzmann constant in it
"""


@from_sympy(result=pressure)
def gas_law_particle_count():
    # rearrange Boltzmann gas law for p
    return sympy.solve(gas_law_boltzmann_equation, p)[0]
    # N⋅T⋅k_B
    # ───────
    #    V


@from_sympy(result=pressure)
def gas_law_mole():
    return (
        # start with Boltzmann gas law
        gas_law_particle_count.equation
        # replace N with n * N_A
        .subs(
            total_particle_count.equation.lhs,
            total_particle_count.equation.rhs,
        )
    )
    #  N_A⋅T⋅k_B⋅n
    #  ───────────
    #      V


@from_sympy(result=pressure)
def gas_law_meteorology():
    return (
        # start with Boltzmann gas law
        gas_law_mole.equation
        # introduce universal gas constant from k_B and N_A
        .subs(
            gas_constant_definition.equation.rhs,
            gas_constant_definition.equation.lhs,
        )
        # introduce specific gas constant
        .subs(R, sympy.solve(specific_gas_constant_definition.equation, R)[0])
        # merge mole fraction and molar mass into mass
        .subs(mass_from_mole.equation.rhs, mass_from_mole.equation.lhs)
        # introduce density as mass per volume
        .subs(density_canonical.equation.rhs, density_canonical.equation.lhs)
    )
    # p = Rₛ⋅T⋅ρ


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
