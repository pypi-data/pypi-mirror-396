# systeh modules
import collections
import os
import re
import time
import itertools
import inspect
import contextlib
import textwrap
import functools
import warnings

# internal modules
from parmesan.units import units
from parmesan import bounds
from parmesan.utils.string import add_to_docstring
from parmesan.errors import ParmesanWarning, ParmesanError

# external modules
import sympy
from sympy.printing.latex import LatexPrinter, split_super_sub, translate
import numpy as np
from rich.progress import Progress
from rich.console import Console


class ParmesanLatexPrinter(LatexPrinter):
    """
    LaTeX printer that properly formats nested super/subscripts,
    makes subscripts and symbols names with multiple characters non-italic.
    """

    def _deal_with_super_sub(self, string: str, style="plain") -> str:
        """
        Properly nest super- and subscripts
        """
        if "{" in string:
            name, supers, subs = string, [], []
        else:
            name, supers, subs = split_super_sub(string)
            name = translate(name)
            supers = [translate(sup) for sup in supers]
            subs = [translate(sub) for sub in subs]
            if len(name) > 1 and re.fullmatch(
                r"[a-z]+", name, flags=re.IGNORECASE
            ):
                # multichar names not italic
                name = rf"\mathrm{{{name}}}"

        # apply the style only to the name
        if style == "bold":
            name = rf"\mathbf{{{name}}}".format(name)

        # glue all items together:
        if supers:
            name = functools.reduce(
                lambda a, b: rf"{b}^{{{a}}}", reversed([name] + supers)
            )
        if subs:
            name = functools.reduce(
                lambda a, b: rf"{b}_\mathrm{{{a}}}", reversed([name] + subs)
            )
        return name


latexprinter = ParmesanLatexPrinter(settings=dict(mul_symbol=r" \cdot "))


class Symbol(sympy.core.symbol.Symbol):
    """
    Small wrapper around :any:`sympy.core.symbol.Symbol` with sensible default
    constraints (``real=True`` and ``positive=True``) and a way to specify some
    metadata
    """

    __slots__ = ("value", "unit", "title", "description", "bounds", "latex")

    def __new__(
        cls,
        *args,
        value=None,
        unit=units.dimensionless,
        quantity=None,
        description=None,
        bounds=None,
        title=None,
        latex=None,
        **kwargs,
    ):
        symbol = sympy.Symbol.__new__(
            cls, *args, **{**dict(real=True), **kwargs}
        )
        symbol.value = value
        symbol.unit = units.Unit(unit)
        symbol.description = description
        symbol.title = title
        symbol.bounds = bounds
        symbol.latex = latex
        if quantity is not None:
            symbol.quantity = quantity
        return symbol

    @property
    def quantity(self):
        return self.value * self.unit

    @quantity.setter
    def quantity(self, quantity):
        self.value = quantity.m
        self.unit = quantity.u

    def _latex(self, printer):
        # TODO: can we add support for multiple subscript layers here?
        # use custom provided LaTeX or fall back to default
        return self.latex or printer._print_Symbol(self)

    @classmethod
    def PartialDerivative(cls, what, by, *args, **kwargs):
        """
        Helper to make a partial derivative symbol from two others
        """
        if not args:
            args = [f"d{what}d{by}"]
        kwargs.setdefault("unit", what.unit / by.unit)
        kwargs.setdefault(
            "latex",
            rf"\frac{{\partial {{{latexprinter.doprint(what)}}} }}{{\partial {{{latexprinter.doprint(by)}}} }}",
        )
        if by is z:
            kwargs.setdefault("title", f"vertical gradient of {what.title}")
            kwargs.setdefault(
                "description", f"change of {what.title} with {by.title}"
            )
        kwargs.setdefault("title", f"change of {what.title} with {by.title}")
        return cls(*args, **kwargs)

    @classmethod
    def Covariance(cls, s1, s2, *args, **kwargs):
        """
        Helper to make a covariance symbol from two others
        """
        if not args:
            args = [f"cov_{s1}_{s2}"]
        kwargs.setdefault("unit", s1.unit * s2.unit)
        kwargs.setdefault(
            "latex",
            rf"\overline{{ {{{latexprinter.doprint(s1)}}}' {{{latexprinter.doprint(s2)}}}' }}",
        )
        kwargs.setdefault("title", f"covariance of {s1.title} and {s2.title}")
        return cls(*args, **kwargs)

    def difference(self, *args, along=None, **kwargs):
        """
        Helper to generate a difference symbol (SYMBOL → ΔSYMBOL)
        """
        if not args:
            args = [f"Δ{self}"]
        kwargs.setdefault("title", f"{self.title or str(self)} difference")
        kwargs.setdefault("unit", self.unit)
        if self.description:
            kwargs.setdefault(f"difference: {self.description}")
        if isinstance(along, type(self)):
            if isinstance(args, list):
                args[0] = f"Δ{along}{self}"
            kwargs.setdefault(
                "latex",
                rf"\Delta_\mathrm{{{latexprinter.doprint(along)}}}{{{latexprinter.doprint(self)}}}",
            )
        return type(self)(*args, **kwargs)


# ✅ Basic symbols
V = volume = Symbol("V", unit="m³", title="volume", positive=True)
m = mass = Symbol("m", unit="kg", title="mass", positive=True)
m_tot = m_total = mass_total = total_mass = Symbol(
    "m_tot", unit="kg", title="total mass", positive=True
)
n = amount_of_substance = Symbol(
    "n",
    unit="mole",
    title="amount of substance",
    description="amount of particles/substance in moles",
    positive=True,
)
M = molar_mass = Symbol(
    "M",
    unit="kg/mole",
    title="molar mass",
    description="mass of one mole of substance",
    positive=True,
)
M_co2 = molar_mass_co2 = molar_mass_carbon_dioxide = Symbol(
    "M_co2",
    title="molar mass of CO₂",
    description="mass of one mole of CO₂",
    quantity=(44.01 * units.gram).to("kg") / units.mol,
    positive=True,
)
M_h2o = molar_mass_h2o = molar_mass_water_vapour = Symbol(
    "M_h2o",
    title="molar mass of water vapour",
    description="mass of one mole water vapour",
    quantity=(18.02 * units.gram).to("kg") / units.mol,
    positive=True,
)
M_dry = M_dryair = molar_mass_dry_air = Symbol(
    "M_dry",
    title="molar mass of dry air",
    description="mass of one mole of dry air",
    quantity=(28.96 * units.gram).to("kg") / units.mol,
    positive=True,
)
k_B = boltzmann_constant = Symbol(
    # Taken from https://physics.nist.gov/cgi-bin/cuu/Value?k (15.12.2020).
    "k_B",
    title="Boltzmann constant",
    quantity=1.380649e-23 * units.joule / units.kelvin,
    positive=True,
)
N = (
    total_particle_count
) = total_count = total_amount = total_substance = Symbol(
    "N",
    title="Total count",
    description="the total amount of particles",
    positive=True,
)
N_A = avogadro_constant = Symbol(
    "N_A",
    title="Avogadro constant",
    # Taken from https://physics.nist.gov/cgi-bin/cuu/Value?na (15.12.2020,positive=True).
    quantity=6.02214076e23 / units.mol,
)
g = g_earth = earth_acceleration = Symbol(
    "g",
    title="earth acceleration",
    quantity=9.81 * units.meter / units.second**2,
    positive=True,
)
z = height = Symbol(
    "z",
    unit="m",
    title="z coordinate",
    description="typically used as height above ground",
)
z_ref = reference_height = Symbol(
    "z_ref", unit="m", title="reference z coordinate"
)
d = displacement_height = obstacle_height = Symbol(
    "d",
    unit="m",
    title="displacement height",
    description="height offset for the logarithmic wind profile, i.e. the height at which an equivalent flat surface would be placed to produce the observed logarithmic wind profile",
)
z_0 = roughness_length = Symbol(
    "z_0",
    unit="m",
    title="roughness length",
    description="height at which the logarithmic wind profile would become calm",
)
Δz = height_difference = vertical_thickness = z.difference()

# 💨 Wind
u = wind_component_east = wind_component_eastward = Symbol(
    "u", unit="m/s", title="eastward wind component"
)
v = wind_component_east = wind_component_eastward = Symbol(
    "v", unit="m/s", title="northward wind component"
)
w = wind_component_east = wind_component_eastward = Symbol(
    "w", unit="m/s", title="upward wind component"
)
u_h = horizontal_wind_speed = horizontal_wind = Symbol(
    "u_h", unit="m/s", title="horizonal wind speed"
)
Δzu_h = horizontal_wind_speed_vertical_difference = u_h.difference(along=z)
duhdz = horizontal_wind_speed_vertical_gradient = Symbol.PartialDerivative(
    u_h, z, "duhdz"
)
cov_uh_w = (
    covariance_vertical_wind_horizontal_wind
) = covariance_horizontal_wind_vertical_wind = Symbol.Covariance(
    u_h, w, "cov_uh_w"
)
u_c = cross_wind = u_cross = u_crosswind = Symbol(
    "u'", unit="m/s", title="rightwards cross-wind component"
)
v_c = head_wind = v_head = v_headwind = Symbol(
    "v'", unit="m/s", title="forward head wind component"
)
yaw = (
    γ_yaw_Earth
) = yaw_angle = bearing = bearing_angle = heading = heading_angle = Symbol(
    "γ_yaw_Earth",
    unit="radians",
    title="Yaw/Heading Angle in Earth coordinate system",
    description="yaw angle in meteorological notation, i.e. northwards is 0°, eastwards is 90°, etc.",
)

# 🌡️ Temperature
T = temperature = Symbol(
    "T",
    unit="K",
    title="temperature",
    positive=True,
)
T_ref = reference_temperature = Symbol(
    "T_ref",
    unit="K",
    title="reference temperature",
    positive=True,
)
T_d = dewpoint_temperature = dewpoint = Symbol(
    "T_d",
    unit="K",
    title="dewpoint temperature",
    description="temperature at which condensation starts",
    positive=True,
)
dTdz = (
    temperature_vertical_gradient
) = temperature_lapse_rate = Symbol.PartialDerivative(T, z)
ΔT = temperature_difference = T.difference()
Θ = θ = potential_temperature = Symbol(
    "θ",
    unit="K",
    title="potential temperature",
    description="defined as the temperature a volume of gas has after adiabatically changing its pressure to a reference pressure (typically 1000 hPa)",
    positive=True,
)
dθdz = (
    potential_temperature_gradient
) = (
    potential_temperature_gradient_vertical
) = (
    potential_temperature_vertical_gradient
) = vertical_potential_temperature_gradient = Symbol.PartialDerivative(θ, z)
θv = (
    θ_v
) = virtual_potential_temperature = potential_virtual_temperature = Symbol(
    "θ_v",
    unit="K",
    title="virtual potential temperature",
    description="the potential temperature a dry air volume would need to have to have the same density as moist air",
    positive=True,
)
dθvdz = (
    virtual_potential_temperature_gradient
) = (
    virtual_potential_temperature_gradient_vertical
) = vertical_virtual_potential_temperature_gradient = Symbol.PartialDerivative(
    θv, z, "dθvdz"
)
Δzθ_v = (
    virtual_potential_temperature_vertical_difference
) = potential_virtual_temperature_vertical_difference = θv.difference(along=z)
T_v = Tv = virtual_temperature = Symbol("T_v", unit="K", positive=True)
T_c0 = (
    temperature_celsius_offset
) = celsius_offset = zero_celsius_in_kelvin = Symbol(
    "T_c0",
    title="Celsius scale offset",
    description="zero degrees Celsius in Kelvin",
    quantity=273.15 * units.kelvin,
    positive=True,
)
K_turb_mass = (
    K_eddy_mass
) = (
    turbulent_exchange_coefficient_for_mass
) = eddy_diffusivity_for_mass = Symbol(
    "K_turb_mass",
    unit="m²/s",
    title="turbulent exchange coefficient for mass",
    description="aka. eddy diffusivity for mass (e.g. trace gases like CO₂ or water vapour). Factor relating spatial concentration gradient with mass flux.",
)

# 🔨 Pressure
p = pressure = Symbol("p", title="pressure", unit="Pa", positive=True)
p_ref = reference_pressure = Symbol(
    "p_ref",
    unit="Pa",
    quantity=units("1000 hPa").to("Pa"),
    description="reference pressure",
    positive=True,
)
Δp = pressure_difference = p.difference()
e = e_w = p_w = water_vapour_pressure = Symbol(
    "e_w",
    unit="Pa",
    title="water vapour pressure",
    description="partial pressure of water vapour in a gas mixture",
    positive=True,
)
e_s = e_sat = saturation_water_vapour_pressure = Symbol(
    "e_s", unit="Pa", title="saturation water vapour pressure", positive=True
)

# 🏋️ Density
rho = ρ = density = mass_density = Symbol(
    "ρ",
    unit="kg/m³",
    title="density",
    description="mass density, i.e. mass per volume",
    positive=True,
)
dρdz = (
    density_gradient
) = (
    density_gradient_vertical
) = vertical_density_gradient = Symbol.PartialDerivative(ρ, z)

# 💨 Gas
ρ_Tgas = gas_mass_density = trace_gas_mass_density = Symbol(
    "ρ_Tgas",
    unit="kg/m³",
    title="(trace) gas mass density",
    description="e.g. mass of CO₂ per unit volume",
    positive=True,
)
Δzρ_Tgas = (
    gas_mass_density_difference
) = trace_gas_mass_density_difference = ρ_Tgas.difference(along=z)
dρTgasdz = trace_gas_mass_density_vertical_gradient = Symbol.PartialDerivative(
    ρ_Tgas, z, "dρTgasdz"
)
X_Tgas = trace_gas_particle_ratio = trace_gas_molar_fraction = Symbol(
    "X_Tgas",
    title="trace gas molar fraction",
    description="ratio of trace gas particle count over total particle count in gas mixture",
    positive=True,
    bounds=[0, 1],
)
X_Tgases = trace_gases_particle_ratio = trace_gases_molar_fraction = Symbol(
    "X_Tgases",
    title="trace gases molar fraction",
    description="ratio of all trace gases (e.g. CO₂, H₂O) particle count over total particle count in gas mixture",
    positive=True,
    bounds=[0, 1],
)
r_Tgas = trace_gas_molar_mixing_ratio = Symbol(
    "r_Tgas",
    title="trace gas molar mixing ratio",
    description="ratio of trace gas particle count over remaining particle count in mixture",
    positive=True,
    bounds=[0, 1],
)
r_dry_Tgas = trace_gas_dry_molar_mixing_ratio = Symbol(
    "r_Tgas",
    title="trace gas dry molar mixing ratio",
    description="ratio of trace gas particle count over dry air (i.e. without trace gases such as CO₂ or H₂O) particle count in mixture",
    positive=True,
    bounds=[0, 1],
)

# 💦 Humidity
rho_abs = (
    abs_hum
) = rho_w = ρ_w = absolute_humidity = water_vapour_mass_density = Symbol(
    "ρ_w",
    unit="kg/m³",
    title="water vapour mass density",
    description="mass density of water vapour, also known as absolute humidity",
    positive=True,
)
q = specific_humidity = Symbol("q", unit="1", positive=True)
r = mixing_ratio = Symbol(
    "r",
    title="water vapour mass mixing ratio",
    description="ratio of water vapour mass (density) over dry air mass (density)",
    unit="1",
    positive=True,  # TODO
)
m_w = mass_water_vapour = water_vapour_mass = Symbol(
    "m_w", unit="kg", title="water vapour mass", positive=True
)
RH = rh = relative_humidity = Symbol(
    "RH",
    title="relative humidity",
    description="water vapour pressure fraction of saturation water vapour pressure",
    positive=True,
)

# 💨 Gas Constants
R = gas_constant = gas_constant_universal = Symbol(
    "R",
    title="universal gas constant",
    quantity=k_B.quantity * N_A.quantity,
    positive=True,
)
R_s = gas_constant_specific = specific_gas_constant = Symbol(
    "R_s", title="specific gas constant", unit="J / (K*kg)", positive=True
)
R_dry = R_d = R_dryair = gas_constant_dry_air = Symbol(
    "R_dry",
    title="dry air gas constant",
    description="specific gas constant of dry air",
    quantity=R.quantity / M_dry.quantity,
    positive=True,
)
R_h2o = R_w = gas_constant_h2o = gas_constant_water_vapour = Symbol(
    "R_h2o",
    title="water vapour gas constant",
    description="specific gas constant of water vapour",
    quantity=R.quantity / M_h2o.quantity,
    positive=True,
)
R_co2 = gas_constant_co2 = Symbol(
    "R_co2",
    title="CO2 gas constant",
    description="specific gas constant of carbon dioxide",
    quantity=R.quantity / M_co2.quantity,
    positive=True,
)

# ☕ heat capacities
c_p = specific_isobaric_heat_capacity = Symbol(
    "c_p",
    title="specific isobaric heat capacity",
    description="heat capacity per unit mass under constant pressure",
    unit="J/kg/K",
    positive=True,
)
c_p_dryair = c_p_dry = specific_isobaric_heat_capacity_dry_air = Symbol(
    "c_p_dryair",
    latex=r"c_{\mathrm{p}_\mathrm{dry air}}",
    title="specific isobaric heat capacity of dry air",
    description="heat capacity of dry air per unit mass under constant pressure",
    quantity=units("1005 J/kg/K"),
    positive=True,
)

# ♨️  Radiation
σ_SB = (
    sigma_stefanboltzmann
) = boltzmann_constant = stefan_boltzmann_constant = Symbol(
    "σ_SB",
    title="Stefan-Boltzmann constant",
    # Taken from https://en.wikipedia.org/wiki/Stefan%E2%80%93Boltzmann_constant
    quantity=5.67037441918442945397099673188923087584012297029130e-8
    * units("W/m^2 / K^4"),
    positive=True,
)
I = irradiance = radiation = Symbol(
    "I", title="irradiance", unit="W/m²", positive=True
)
T_surf = temperature_surface = surface_temperature = Symbol(
    "T_surf", unit="K", title="surface temperature", positive=True
)
T_amb = temperature_ambient = ambient_temperature = Symbol(
    "T_amb", unit="K", title="ambient temperature", positive=True
)
T_surf_adj = (
    temperature_surface_adjusted
) = adjusted_surface_temperature = Symbol(
    "T_surf_adj", unit="K", title="adjusted surface temperature", positive=True
)
ε = epsilon = Symbol("ε", title="emissivity", bounds=[0, 1], positive=True)
ε_1 = epsilon_1 = emissivity_1 = Symbol(
    "ε_1", title="emissivity №1", bounds=[0, 1], positive=True
)
ε_2 = epsilon_2 = emissivity_2 = Symbol(
    "ε_2", title="emissivity №2", bounds=[0, 1], positive=True
)

# 🔢 Parametrisation parameters
A_magnus = Symbol(
    "A_magnus",
    quantity=units.Quantity(6.112, "hPa"),
    title="Magnus formula parameter A",
    description="for saturation water vapour pressure parametrisation",
    positive=True,
)
B_magnus_w = Symbol(
    "B_magnus_w",
    quantity=units.Quantity(17.62, "dimensionless"),
    title="Magnus formula parameter B (over water)",
    description="for saturation water vapour pressure parametrisation",
    positive=True,
)
C_magnus_w = Symbol(
    "C_magnus_w",
    quantity=units.Quantity(243.12, "°C").to("K"),
    title="Magnus formula parameter C (over water)",
    description="for saturation water vapour pressure parametrisation",
    positive=True,
)
B_magnus_i = Symbol(
    "B_magnus_i",
    quantity=units.Quantity(22.46, "dimensionless"),
    title="Magnus formula parameter B (over ice)",
    description="for saturation water vapour pressure parametrisation",
    positive=True,
)
C_magnus_i = Symbol(
    "C_magnus_i",
    quantity=units.Quantity(272.62, "°C").to("K"),
    title="Magnus formula parameter C (over ice)",
    description="for saturation water vapour pressure parametrisation",
    positive=True,
)

# Turbulence
κ = kappa = von_karman = von_karman_constant = Symbol(
    "κ", title="Von Kármán constant", value=0.4, positive=True
)
F_H = heat_flux = sensible_heat_flux = Symbol(
    "F_H", title="sensible heat flux", unit="W/m²"
)
F_L = latent_heat_flux = Symbol("F_L", title="latent heat flux", unit="W/m²")
F_M = momentum_flux = Symbol("F_M", title="momentum flux", unit="N/m²")
F_mass = mass_flux = flux_mass = Symbol(
    "F_mass",
    unit="kg/m²/s",
    title="mass flux",
    description="e.g. for trace gases like CO₂ or water vapour, for example through eddy diffusion",
)
u_star = friction_velocity = Symbol(
    "u_star", title="friction velocity", unit="m/s", positive=True, latex="u_*"
)
L_MO = monin_obukov_length = Symbol(
    "L_MO", title="Monin-Obukov length", unit="m"
)
ζ_MO = zeta = monin_obukov_stability_parameter = Symbol(
    "ζ_MO", title="Monin-Obukov stability parameter (dimensionless height)"
)
Φ_MO = monin_obukov_stability_function = Symbol(
    "Φ_MO", title="Monin-Obukov stability function"
)
Φ_MO_M = monin_obukov_stability_function = Symbol(
    "Φ_MO_M", title="Monin-Obukov stability function for momentum"
)
Φ_MO_H = monin_obukov_stability_function = Symbol(
    "Φ_MO_H", title="Monin-Obukov stability function for heat"
)
Φ_MO_W = monin_obukov_stability_function = Symbol(
    "Φ_MO_W", title="Monin-Obukov stability function for water vapour"
)
cov_Θv_w = (
    cov_θv_w
) = (
    covariance_virtual_potential_temperature_vertical_wind
) = (
    covariance_vertical_wind_virtual_potential_temperature_vertical
) = Symbol.Covariance(θ_v, w, "cov_θv_w")
N_BV = (
    brund_vaisala
) = brund_väisälä = brunt_vaisala_frequency = brunt_väisälä_frequency = Symbol(
    "N_BV",
    unit="Hz",
    title="Brunt-Väisälä frequency",
    description="oscillation frequency of a vertically displaced parcel in a statically stable environment",
)
Ri = richardson_number = RN = Symbol("Ri", title="Richardson number")
Ri_b = bulk_richardson_number = BRN = Symbol(
    "Ri_b", title="bulk Richardson number"
)
Ri_g = gradient_richardson_number = GRN = Symbol(
    "Ri_g", title="gradient Richardson number"
)
Ri_f = flux_richardson_number = FRN = Symbol(
    "Ri_f", title="flux Richardson number"
)
Re = reynolds_number = reynoldsnr = reynolds_nr = Symbol(
    "Re", title="Reynolds number", positive=True
)
L_char = length_scale = characteristic_length = Symbol(
    "L_char",
    title="characteristic length scale",
    unit="m",
    description="e.g. pipe diameter for a pipe flow",
    positive=True,
)
U_char = flow_speed_scale = characteristic_flow_speed = Symbol(
    "U_char", title="characteristic flow speed", unit="m/s", positive=True
)
ν = nu = kinematic_viscosity = Symbol(
    # This is a nu, not a v!
    "ν",
    title="kinematic viscosity",
    unit="m²/s",
    positive=True,
)
µ = mu = dynamic_viscosity = Symbol(
    # can't use µ directly here, inconsistent string representation 🤷
    "mu",
    title="dynamic viscosity",
    unit="Pa*s",
    positive=True,
)


# 👀 Generate lookup tables
# 📣 All symbols must be defined ABOVE this! ☝️
LOCALS = locals().copy()
NAMES = collections.defaultdict(set)
BY_NAME = dict()
for _k, _v in LOCALS.items():
    if isinstance(_v, Symbol):
        NAMES[_v].add(_k)
        BY_NAME[_k] = _v
del LOCALS, _k, _v
for symbol, _names in NAMES.items():
    if str(symbol) not in _names and str(symbol).isidentifier():
        warnings.warn(
            f"Symbol {symbol} has a string representation unlike "
            f"its variable name in parmesan.symbols. "
            f"You should not see this warning as an end-user of PARMESAN. "
            f"If you're currently working on PARMESAN, assign the symbol {symbol} "
            f"also to a variable named identically ({symbol})",
            ParmesanWarning,
        )
SHORTNAME = {s: min(n, key=len) for s, n in NAMES.items()}
FULLNAME = {s: max(n, key=len) for s, n in NAMES.items()}


# 📝 Make a pretty list of symbols for the documentation
def _symbol_entry(symbol):
    names = NAMES.get(symbol, set())
    title = (
        (symbol.title or "")
        or max(names, key=len).replace("_", " ")  # longest alias
        or (symbol.description or "")
    ).title() or str(symbol)
    unitfmt = (
        "1" if symbol.unit == units.dimensionless else f"{symbol.unit:L~}"
    )
    vfmt = ""
    if symbol.value is not None:
        vfmt = (
            f":math:`{symbol.quantity:L~}`"
            if f"{symbol.unit:L~}"
            else f"{symbol.quantity}"
        )
    if vfmt:
        vfmt = f"= {vfmt}"
    result = textwrap.dedent(
        rf"""
    {title}
    {'-' * len(title)}

    :math:`{latexprinter.doprint(symbol)}`   :math:`\left[{unitfmt}\right]`  {vfmt}

    """
    )
    if symbol.description:
        result += textwrap.dedent(
            rf"""
    - {symbol.description}
    """
        )
    if names:
        result += textwrap.dedent(
            rf"""
    - aliases: {' , '.join(('``'+a+'``' for a in sorted(names,key=len)))}
    """
        )
    return result


def formatted_list_of_equation_functions(_locals):
    r'''
    Create a rst-formatted list of equations for use in module
    ``__doc__``-strings.

    Args:
        _locals (dict): the result of ``locals().copy()`` in that module

    Usage:


    .. code-block:: python

        # in the module you'd like to see a list of equations:
        __doc__ = f"""

        List of equations
        -----------------

        {formatted_list_of_equation_functions(locals().copy())}

        """

    '''
    _equation_functions = {
        k: v for k, v in _locals.items() if hasattr(v, "equation")
    }
    return f"\n\n".join(
        [
            f":any:`{name}`  →  :math:`{latexprinter.doprint(fun.equation)}`"
            for name, fun in sorted(_equation_functions.items())
        ]
    )


__doc__ = (
    r"""
In this module, all :mod:`sympy` symbols used in :mod:`parmesan`'s functions
are declared. This is how you access them:

.. code-block:: python

    # Import all symbols at once (easiest)
    from parmesan.symbols import *
    rho * R_s * T

    # You can work with them like normal Sympy symbols:
    import sympy
    sympy.pprint(rho * R_s * T) # pretty-printing
    # Rₛ⋅T⋅ρ

    # Define equations, e.g. the ideal gas law:
    ideal_gas_law = sympy.Eq(p, rho * R_s * T)
    sympy.pprint(ideal_gas_law)
    # p = Rₛ⋅T⋅ρ

    # We can make the ideal gas law for water vapour by substituting:
    ideal_gas_law_h2o = ideal_gas_law.subs({R_s:R_h2o,p:e, rho:rho_w})
    sympy.pprint(ideal_gas_law_h2o)
    # e = Rₕ₂ₒ⋅T⋅ρ_w

    # similarly, differentiating, integrating, etc. is also possible,
    # see the Sympy docs for reference.
"""
    + rf"""

List of Symbols
+++++++++++++++

{(2*chr(10)).join([_symbol_entry(symbol) for symbol, names in sorted(NAMES.items(), key=lambda s: getattr(s[0],'title',None) or str(s[0]))])}

API Documentation
+++++++++++++++++
"""
)


def maximum_error_equation(
    eq,
    variables=None,
    relative=False,
    replace_relative_error=True,
    error_format="Δ{}_max",
    rel_error_format="Δ{}_max_rel",
    simplify=False,
    return_function=False,
):
    """
    Given an equation, turn it into an equation for maximum absolute or
    relative error estimation.

    Args:
        variables (sequence of symbols, optional): variables to consider
        relative (bool, optional): whether to make a relative error equation
            instead of absolute error
        replace_relative_error (bool, optional): whether to replace relative
            error terms with a relative error variable
        error_format, rel_error_format (str or callable, optional): formatters
            for error symbols. Either :any:`str.format` string or callable that
            will be given the variable symbol as argument.
        simplify (bool, optional): if ``False``, tries to let the coefficients
            of the individual input variable's error terms stand out. If
            ``False``, try to make the expression as compact as possible. Note
            that this can get very slow.
        return_function (bool, optional): whether to also return a
            :any:`sympy.lambdify`ed function to calculate the error.

    Returns:
        sympy.Eq  : maximum error equation
        sympy.Eq, callable  : if ``return_function`` is True

    .. note::

        The :any:`from_sympy` decorator automatically applies this function.

    """
    # TODO: make use of PARMESAN's Symbol() features for custom LaTeX
    error_formatter = (
        error_format.format if isinstance(error_format, str) else error_format
    )
    rel_error_formatter = (
        rel_error_format.format
        if isinstance(rel_error_format, str)
        else rel_error_format
    )
    if (n := len(eq.lhs.free_symbols)) != 1:
        raise ValueError(
            f"The left-hand side ({eq.lhs!r}) doesn't have exactly 1 free symbols but {n} (eq.lhs.free_symbols)."
        )
    errorterms = []
    variables = variables or eq.rhs.free_symbols
    error_variables = []

    def is_one(x):
        return (x := x.doit()) == 1 or re.fullmatch(r"1(\.0+)?", f"{x}")

    for x in variables:
        Δx = Symbol(
            error_formatter(x), unit=getattr(x, "unit", None), positive=True
        )
        error_variables.append(Δx)
        term = sympy.Abs(sympy.diff(eq.rhs, x)) * Δx
        if relative:
            Δx_rel = Symbol(rel_error_formatter(x), positive=True)
            error_variables.append(Δx_rel)
            Δx_rel_eq = sympy.Eq(Δx_rel, Δx / x)
            term /= eq.rhs  # divide by original formula
            coeff = sympy.UnevaluatedExpr(term.coeff(Δx_rel_eq.rhs))
            # coeff can be 0 if extraction doesn't work
            if (res := (coeff * Δx_rel_eq.rhs).doit()) == term:
                Δx_rel_sym = (
                    Δx_rel_eq.lhs if replace_relative_error else Δx_rel_eq.rhs
                )
                term = (
                    Δx_rel_sym
                    if is_one(coeff)
                    else Δx_rel_sym * sympy.UnevaluatedExpr(coeff)
                )
        else:
            coeff = sympy.UnevaluatedExpr(term.coeff(Δx))
            if (coeff * Δx).doit() == term:
                term = (
                    Δx if is_one(coeff) else Δx * sympy.UnevaluatedExpr(coeff)
                )
            else:
                term = Δx * sympy.UnevaluatedExpr(coeff)
        errorterms.append(sympy.UnevaluatedExpr(term))

    Δy = Symbol(
        error_formatter(eq.lhs),
        unit=getattr(eq.lhs, "unit", None),
        positive=True,
    )
    if relative:
        if replace_relative_error:
            Δy = Symbol(rel_error_formatter(eq.lhs), positive=True)
        else:
            Δy /= sympy.UnevaluatedExpr(eq.rhs)
    error_eq = sympy.Eq(Δy, sum(errorterms))
    if simplify:
        error_eq = error_eq.simplify()
    ret = error_eq
    if return_function:
        error_eq = error_eq.doit()
        variables = set(list(variables) + error_variables).intersection(
            error_eq.rhs.free_symbols
        )
        func = sympy.lambdify(sorted(variables, key=str), error_eq.rhs)
        ret = (ret, func)
    return ret


# Set of tuples (functions decorated with :any:`from_sympy`.
EQUATIONS = set()


def get_function(
    result, inputs=None, generate=True, progress=None, console=None
):
    """
    Try to find or create a function that calculates ``result`` from a set of
    ``inputs``.

    .. note::

        Currently, only rearranging existing equations is implemented. In a
        future version of PARMESAN, combining different equations might be
        implemented.

    Args:
        result (sympy.Symbol): the resulting symbol for the target equation
        inputs (sequence of sympy.Symbol, optional): the available inputs.
            If unspecified, will return functions that return the ``result``
            independently of inputs.
        generate (bool, optional): whether to generate new equations from
            existing ones. No chaining is performed (yet), just rearranging of
            single equations. Defaults to ``True``.

    Yields:
        callable : a :any:`from_sympy`-decorated function returning the desired
            ``result`` and taking (at least) the ``inputs`` as arguments. More
            direct matches are yielded first.
    """
    result_ = set([result])
    inputs = inputs or set()
    try:
        inputs_ = set(inputs)
    except TypeError:
        inputs_ = set([inputs])
    console = console or Console(stderr=True)
    yielded = set()

    with progress or Progress(console=console, transient=True) as progress:

        def direct_match(eq):
            if (
                eq.lhs.free_symbols == result_
                and eq.rhs.free_symbols == inputs_
            ):
                return function

        def direct_reverse_match(f):
            return (
                eq.rhs.free_symbols == result_
                and eq.lhs.free_symbols == inputs_
            )

        def incomplete_match(f):
            # at least all inputs in right hand side
            return (
                eq.lhs.free_symbols == result_
                and not inputs_ - eq.rhs.free_symbols
            )

        def incomplete_reverse_match(f):
            # at least all inputs in left hand side
            return (
                eq.rhs.free_symbols == result_
                and not inputs_ - eq.lhs.free_symbols
            )

        def unordered_match(f):
            # all symbols somehow in the equation
            return result_.union(inputs_) == eq.free_symbols

        def incomplete_unordered_match(f):
            # all symbols somehow in the equation
            return not result_.union(inputs_) - eq.free_symbols

        for function, matcher in progress.track(
            list(
                itertools.product(
                    sorted(
                        EQUATIONS, key=lambda f: str(getattr(f, "__name__", f))
                    ),
                    [
                        direct_match,
                        unordered_match,
                        direct_reverse_match,
                        incomplete_match,
                        incomplete_reverse_match,
                        incomplete_unordered_match,
                    ],
                )
            )
        ):
            if (eq := getattr(function, "equation", None)) is None:
                continue
            if function in yielded:
                continue
            if re.search(
                r"rearranged_for.*_solution_\d+",
                str(getattr(function, "__name__", "")),
            ):
                continue
            if not matcher(eq):
                continue
            if eq.lhs.free_symbols == result_:
                yield function
                yielded.add(function)
            elif generate:
                try:
                    solutions = sympy.solve(eq, result)
                except Exception as e:
                    console.log(f"{e!r}")
                    continue
                for i, solution in enumerate(solutions, start=1):
                    fnew = from_sympy(result=result)(lambda: solution)
                    fnew.__name__ = f"{function.__name__}_rearranged_for_{result}_solution_{i}"
                    yield fnew
                    yielded.add(fnew)


def from_sympy(
    _dummy=None,
    paramdoc=None,
    defaults=None,
    result=None,
    bounds_override=None,
    units_override=None,
    rearrange_from=None,
    record=True,
    simplify=False,
    generate_error_eq=True,
    check_units=True,
):
    """
    This decorator can be applied to a function that takes *no* arguments and
    returns a sympy expression or equation. The resulting function will...

    - have an ``equation`` attribute containing a
      :any:`sympy.core.relational.Equality`. This equation relates the
      ``result`` to the expression returned from the function. If no ``result``
      was given, a corresponding symbol from :py:mod:`parmesan.symbols` with
      prefix match to the decorated function's name is searched. An error is
      raised if none is found.
    - have a ``maximum_error`` attribute which is in turn a
      @from_sympy-decorated function that is the :any:`maximum_error_equation`
    - have default arguments set according to ``defaults``
    - accept arguments according to all matching symbol aliases in
      :py:mod:`parmesan` (e.g. both ``T`` and ``temperature`` for
      ``parmesan.symbols.T``), prioritizing longer aliases
    - have asserted that the equations sides have equal units
    - automatically have :any:`bounds.ensure` and :any:`units.ensure` applied
      according to the metadata of used :py:mod:`parmesan.symbols` in the
      expression
    - have its docstring updated with:
        - parameter aliases and descriptions (override it with ``paramdoc``),
          including units and bounds
        - a LaTeX representation of the equation
        - a collapsible section with the auto-generated source code


    Args:
        _dummy (optional): don't use this argument, it's just to catch
            invalid usage of this decorator.
        paramdoc (mapping of sympy.Symbol to str,optional): parameter
            description string to use for a given symbol. Can also in include
            the (auto-deduced) ``result`` symbol.
        defaults (mapping of sympy.Symbol to e.g. :any:`pint.Quantity`):
            defaults to set on the resulting function's arguments
        result (sympy.Symbol, optional): the resulting symbol (name) from
            :py:mod:`parmesan.symbols` to display in the equation. The default
            tries to guess it from the decorated function's name.
        bounds_override (dict, optional): override for :any:`bounds.ensure`
        units_override (dict, optional): override for :any:`units.ensure`
        rearrange_from (``@from_sympy``-decorated function or sympy.Equation):
            whether to ignore the decorated function and rearrange the given
            equation to obtain ``result``.
        generate_error_eq (bool, optional): whether to generate a maximum error
            equation with :any:`maximum_error_equation`
        record (bool, optional): whether to add the resulting function to
            :py:data:`parmesan.symbols.EQUATIONS` for later lookup.
        simplify (bool, optional): whether to simplify
        check_units (bool, optional): whether to assert that units of both sides
            of the equation match. This is done by first trying to execute the
            function with NaN values and the correct units. If that fails
            (which it does if there's exponents in the equation - nan exponents
            can't cancel out later...), it's retried with 1 as value (can also
            fail due to other reasons). If units don't check out, a
            :any:`ParmesanWarning` is raised. Set ``check_units=False`` to skip
            the units check. You can also set the environment variable
            ``PARMESAN_SKIP_UNITS_CHECK=yes`` to disable this across PARMESAN.

    Example:

    .. code-block:: python

        from parmesan.symbols import *
        @from_sympy()
        def pressure_gas_law():
            return rho * R_d * T

        # The result is a function with convenience and safety nets

        from parmesan.units import units

        # You can use all available symbol aliases (see parmesan.symbols)
        pressure_gas_law(density=1, temperature=300)
        # 86130.48292285814 <Unit('pascal')>

        # As above, it auto-converts to correct units if not given (rho here)
        pressure_gas_law(rho=1, T=units.Quantity(10,"°C"))
        # 81292.82079869093 <Unit('pascal')>

        # It catches wrong bounds (negative density!?)
        pressure_gas_law(rho=-1,T=300)
        # OutOfBoundsWarning: ... input values out of bounds ...

        # It complains about wrong units before evaluation
        pressure_gas_law(rho=1,T=10*units.watt)
        # ValueError: ... could not be converted ...

        # It works with pandas DataFrames
        df = pd.DataFrame(dict(rho=[1,1.1,1.4],T=[10,8,15]))
        pressure_gas_law(rho=df["rho"], T=df["T"])
        # array([2871.01609743, 2526.49416574, 6029.1338046 ]) <Unit('pascal')>

        # Even if there's units in the DataFrame!
        pressure_gas_law(rho=df["rho"], T=df["T"].astype("pint[°C]"))
        # <PintArray>
        # [81292.82079869093, 88790.47933712574, 115819.66038636731]
        # Length: 3, dtype: pint[Pa]
    """
    defaults = defaults or dict()
    paramdoc = paramdoc or dict()
    bounds_override = bounds_override or dict()
    units_override = units_override or dict()
    if hasattr(_dummy, "__call__"):
        raise ValueError(
            f"You probably forgot the parentheses to call @Equation.from_sympy(). "
            f"You should never see this error as a PARMESAN user."
        )

    def decorator(decorated_fun):
        result_symbol = None
        if result is False:
            pass
        elif isinstance(result, sympy.Symbol):
            result_symbol = result
        elif result in NAMES:
            result_symbol = result
        elif result_symbol := BY_NAME.get(result):
            pass
        elif matches := {
            (name, symbol)
            for name, symbol in BY_NAME.items()
            if decorated_fun.__name__.startswith(name)
        }:
            result_symbol = max(matches, key=lambda x: len(x[0]))[1]
        else:
            raise ValueError(
                f"Can't guess result argument while decorating {decorated_fun.__name__} with from_sympy() "
                f"(no symbol name from parmesan.symbols starts with {decorated_fun.__name__!r}), "
                f"please provide a symbol from parmesan.symbols or just False to from_sympy(result=...). "
                f"You should never see this as an end-user of PARMESAN.",
            )

        def solve_eq_for_result(eq, fromtext=""):
            if not (hasattr(eq, "lhs") and hasattr(eq, "rhs")):
                raise ValueError(
                    f"given value {eq!r} ({fromtext}) is neither an "
                    f"@from_sympy-decorated function with "
                    f"an equation attribute nor a sympy.Equation."
                )
            try:
                solutions = sympy.solve(eq, result_symbol)
            except Exception as e:
                raise Exception(
                    f"Can't solve equation {equation} "
                    f"({fromtext}) for {result_symbol = }: {e!r}"
                ) from e
            if len(solutions) != 1:
                raise ValueError(
                    f"Solving equation {eq} "
                    f"({fromtext}) for {result_symbol = } yields "
                    f"{len(solutions)} solutions: ({solutions}). "
                    f"Exactly one solution is needed. "
                    f"Consider picking one and making a @from_sympy-decorated "
                    f"wrapper function that returns it."
                )
            return sympy.Eq(result_symbol, next(iter(solutions)))

        expression = decorated_fun()
        if rearrange_from is not None:
            equation = getattr(rearrange_from, "equation", rearrange_from)
            equation = solve_eq_for_result(
                equation, fromtext=f"from {rearrange_from = }"
            )
        elif hasattr(expression, "lhs") and hasattr(expression, "rhs"):
            equation = solve_eq_for_result(
                expression, fromtext=f"result of {decorated_fun.__name__}"
            )
        else:
            equation = sympy.Eq(result_symbol, expression)

        if simplify:
            equation = equation.simplify()

        lambdified_symbols = {str(s): s for s in equation.rhs.free_symbols}
        _nothing = object()  # own 'None' that can't occur in defaults
        # mapping between symbol and its (default) value
        lambdified_symbols_defaults = {
            s: defaults.get(
                s,
                (
                    s.quantity
                    if getattr(s, "value", _nothing) not in (None, _nothing)
                    else _nothing
                ),
            )
            for s in equation.rhs.free_symbols
        }
        # put the symbols with defaults last so we can later add defaults
        # to the function signature
        lambdified_symbols_order = sorted(
            lambdified_symbols_defaults,
            # symbols with defaults last (because we can only set defaults via
            # __defaults__ to those), otherwise sort by name
            key=lambda x: (
                lambdified_symbols_defaults[x] is not _nothing,
                str(x),
            ),
        )
        # turn the expression into a Python function
        lambdified = sympy.lambdify(
            lambdified_symbols_order,
            equation.rhs,
        )
        # add defaults to function signature
        lambdified.__defaults__ = tuple(
            lambdified_symbols_defaults[s]
            for s in lambdified_symbols_order
            if lambdified_symbols_defaults.get(s, _nothing) is not _nothing
        )
        # auto-generated source code for docstring
        lambdified.__doc__ = decorated_fun.__doc__
        lambdified.__name__ = decorated_fun.__name__
        lambdified_source = inspect.getsource(lambdified).replace(
            "_lambdifygenerated", decorated_fun.__name__
        )
        lambdified_signature = inspect.signature(lambdified)

        # units check before we do anything else!
        check_units_ = check_units  # must use different name otherwise error
        if (
            str(os.environ.get("PARMESAN_SKIP_UNITS_CHECK", "")).lower()
            in ("yes y 1 true".split())
        ) or (
            # e.g. sympy.Piecewise becomes np.select, which dies with units, so can't test
            # TODO: use lambdify(..., modules=[{'Piecewise': custom_np_select_for_units},'numpy'])
            # to pass in a function that eats units
            units_override.get("_operate_without_units")
        ):
            check_units_ = False
        units_check_note = ""
        if check_units_:
            _result_unit = getattr(result_symbol, "unit", units.dimensionless)
            _result_units = []
            for dummyvalue in (np.nan, 1, np.array([1]), np.array([np.nan])):
                if any(
                    u.is_compatible_with(_result_unit) for u in _result_units
                ):
                    break
                kw = dict()
                for (name, param), symbol in zip(
                    lambdified_signature.parameters.items(),
                    lambdified_symbols_order,
                ):
                    unit = getattr(symbol, "unit", units.dimensionless)
                    kw[name] = units.Quantity(dummyvalue, unit)
                with contextlib.suppress(Exception):
                    _nanresult = None
                    _nanresult = lambdified(**kw)
                if _nanresult:
                    _result_units.append(
                        getattr(_nanresult, "u", units.dimensionless)
                    )
            if not any(
                u.is_compatible_with(_result_unit) for u in _result_units
            ):
                units_check_note = (
                    f"⚠️  The units-check for this equation failed. "
                    f"This does not necessarily mean the units don't check out, though, "
                    f"it might be a false negative. Just double-check before using this."
                )

                warnings.warn(
                    f"@from_sympy of {decorated_fun.__name__}: "
                    f"The right-hand side of {equation} yields units like {_result_units}, "
                    f"which are incompatible with the target resulting unit {_result_unit}. "
                    f"Check your symbol units or set check_units=False.",
                    ParmesanWarning,
                )

        # Auto-apply @units.ensure() and @bounds.ensure()
        def symbol_get_bounds(symbol):
            b = None
            if symbol.is_positive:
                b = (0, None)
            elif symbol.is_positive is False:
                b = (None, 0)
            if _b := getattr(symbol, "bounds", None):
                b = _b
            return b

        units_ensure_kwargs = dict(_update_docstring=False)
        for k, v in units_override.copy().items():
            if k.startswith("_"):  # unconditionally pass _-args
                units_ensure_kwargs[k] = units_override.pop(k)
        bounds_ensure_kwargs = dict(_update_docstring=False)
        for name, param in lambdified_signature.parameters.items():
            if symbol := lambdified_symbols.get(name):
                if (unit := getattr(symbol, "unit", None)) is not None:
                    units_ensure_kwargs[name] = unit
                if (b := symbol_get_bounds(symbol)) is not None:
                    bounds_ensure_kwargs[name] = b
                # overrides
                if name in units_override:
                    units_ensure_kwargs[name] = units_override.pop(name)
                if name in bounds_override:
                    bounds_ensure_kwargs[name] = bounds_override.pop(name)
        if units_override:
            warnings.warn(
                f"@from_sympy: {decorated_fun.__name__}: Ignoring {units_override = }. "
                f"Note that alias matching is not yet implemented for it, so consider "
                f"Specifying the overrides in terms of str(symbol):'unit' instead of an alias.",
                ParmesanWarning,
            )
        if bounds_override:
            warnings.warn(
                f"@from_sympy: {decorated_fun.__name__}: Ignoring {bounds_override = }. "
                f"Note that alias matching is not yet implemented for it, so consider "
                f"Specifying the overrides in terms of str(symbol):bounds instead of an alias.",
                ParmesanWarning,
            )
        lambdified = bounds.ensure(
            symbol_get_bounds(result_symbol),
            **bounds_ensure_kwargs,
        )(lambdified)
        lambdified = units.ensure(
            getattr(result_symbol, "unit", None),
            **units_ensure_kwargs,
        )(lambdified)

        @functools.wraps(lambdified)
        def multiarg_wrapper(*args, **given_kwargs):
            """
            This wrapper allows passing arguments with all synonyms in
            parmesan.symbols as arguments, e.g. both ``T`` and
            ``temperature`` for temperature.
            """
            if args:
                argsstr = ", ".join(
                    "{p}={v}".format(
                        p=p,
                        v="..."
                        if len(f"{v!r}".splitlines()) > 1
                        else f"{v!r}",
                    )
                    for p, v in zip(
                        (
                            p
                            for n, p in lambdified_signature.parameters.items()
                            if p.kind is p.POSITIONAL_OR_KEYWORD
                            and p.default is p.empty
                        ),
                        args,
                    )
                )
                raise ParmesanError(
                    f"""@from_sympy-decorated functions in PARMESAN """
                    f"""can't handle positional arguments {args!r}. """
                    f"""It's anyway better to be explicit than implicit, so """
                    f"""please specify the proper keyword argument names, e.g. """
                    f"""{decorated_fun.__name__}({argsstr})"""
                )
            kwargs = {}  # kwargs eventually given to lambdified function

            for (name, param), symbol in zip(
                lambdified_signature.parameters.items(),
                lambdified_symbols_order,
            ):
                kwargs_options = {}  # kwargs_options[name] = value
                if param.default is not inspect.Parameter.empty:
                    # default parameter in function definition
                    # (set by us via __defaults__ above)
                    kwargs_options[""] = param.default
                kwargs_options.update(
                    {
                        n: given_kwargs.pop(n)
                        for n in list(NAMES.get(symbol, [])) + [str(symbol)]
                        if n in given_kwargs
                    }
                )
                used_name = None
                for n, value in sorted(
                    kwargs_options.items(),
                    key=lambda x: len(x[0]),
                    reverse=True,
                ):
                    if not n:
                        continue
                    if name in kwargs:
                        warnings.warn(
                            f"{decorated_fun.__name__}: "
                            f"Ignoring argument {n}={value!r}, "
                            f"prioritizing {used_name}={kwargs[name]!r}",
                            ParmesanWarning,
                        )
                    else:
                        used_name = n
                        kwargs[name] = value
            for n, v in given_kwargs.items():
                warnings.warn(
                    f"{decorated_fun.__name__}: Ignoring argument {n}={v!r}",
                    ParmesanWarning,
                )
            return lambdified(**kwargs)

        # remember the aliases that are possible for each argument, for
        # FunctionCollection to pick up on it
        multiarg_wrapper._arg_aliases = tuple(
            NAMES.get(symbol, set())
            for (name, param), symbol in zip(
                lambdified_signature.parameters.items(),
                lambdified_symbols_order,
            )
        )

        # Build parameter documentation
        def get_symbol_doc(symbol):
            if d := paramdoc.get(symbol):
                return d
            meta = [
                # ugh, duplication 🫤, no walrus := 🦭 possible here
                getattr(symbol, a)
                for a in "title description".split()
                if getattr(symbol, a, "")
            ] or [max(aliases, key=len).replace("_", " ")]
            return ". ".join([f"{s}" for s in meta if s])

        argdoc = []

        def unitfmt(s):
            with contextlib.suppress(AttributeError):
                return r":math:`\left[{}\right]`".format(f"{s.unit:L~}" or "1")
            return ""

        for (name, param), symbol in zip(
            lambdified_signature.parameters.items(),
            lambdified_symbols_order,
        ):
            aliases = sorted(
                set([name] + list(NAMES.get(symbol, []))), key=len
            )
            aliaslist = " , ".join(f"``{a}``" for a in aliases if a != name)
            aliaslist = f"(or {aliaslist})" if aliaslist else ""
            argdoc.append(
                f":param {name}: {aliaslist} {get_symbol_doc(symbol)}"
            )
            argtypes = [f":math:`{latexprinter.doprint(symbol)}`"]
            if param.default is not param.empty:
                try:
                    vstr = (
                        f":math:`{param.default:L~}`"
                        # :math:`` doesn't render with only floats in sphinx 🤷
                        if f"{param.default.u:L~}"
                        else f"{param.default}"
                    )
                except Exception:
                    vstr = f"{param.default}"
                argtypes[-1] += f" = {vstr}"
            else:
                with contextlib.suppress(AttributeError):
                    argtypes[-1] += r" :math:`\left[{}\right]`".format(
                        f"{symbol.unit:L~}" or "1"
                    )
            if _bounds := symbol_get_bounds(symbol):
                argtypes.append(bounds.bounds_formatted(_bounds))
            if param.default is not param.empty:
                argtypes.append("optional")
            if argtypes:
                argdoc.append(f":type {name}: {' , '.join(argtypes)}")

        multiarg_wrapper.__doc__ = add_to_docstring(
            multiarg_wrapper.__doc__,
            f"""

        .. math::

            {latexprinter.doprint(equation)}

        Args (note that these arguments are **keyword-only**, i.e. you need to specify ``param=...``, not just ``...``):

{textwrap.indent(chr(10).join(argdoc).strip(),2*'    ')}

        :return: :math:`{latexprinter.doprint(result_symbol)}` {unitfmt(result_symbol)} - {get_symbol_doc(result_symbol)}

        This function was generated by :any:`from_sympy` from the above expression of :py:mod:`parmesan.symbols`.
        You can acess the underlying equation via ``{decorated_fun.__name__}.equation``.

        {units_check_note}

        .. collapse::  🖱️ Click <b>here</b> to show auto-generated source code

            .. code-block:: python

{textwrap.indent(lambdified_source.strip(),4*'    ')}
        """,
        )

        # remember the equation as attribute of the returned function
        # It's not as easy to return a class here (units and bounds
        # decorator would need to support it, __call__ weirdness, etc.)
        # But this seems to work and also bubbles up through the other
        # decorators
        multiarg_wrapper.equation = equation

        if generate_error_eq and str(
            os.environ.get("PARMESAN_SKIP_ERROR_ANALYSIS", "")
        ).lower() not in ("yes y 1 true".split()):
            time_before = time.perf_counter()
            # what defaults? relative=True?
            maximum_error_equation_kwargs = dict(relative=True)
            maxerror_eq = maximum_error_equation(
                equation,
                variables=[
                    s
                    for s in lambdified_symbols_order
                    if lambdified_symbols_defaults.get(s) is _nothing
                ],
                **maximum_error_equation_kwargs,
            )
            multiarg_wrapper.maximum_error = from_sympy(
                result=maxerror_eq.lhs,
                defaults=defaults,
                generate_error_eq=False,
                check_units=check_units_,
            )(lambda: maxerror_eq.rhs)
            kwargs_str = ", ".join(
                f"{k}={v!r}" for k, v in maximum_error_equation_kwargs.items()
            )
            note = ""
            if (ops := sympy.count_ops(maxerror_eq)) > 50:
                note = (
                    f"⚠️  This equation has {ops} operations. "
                    f"You can try :any:`sympy.simplify.simplify` (``{decorated_fun.__name__}.maximum_error.equation``) "
                    f"to tame it."
                )
            multiarg_wrapper.__doc__ = add_to_docstring(
                multiarg_wrapper.__doc__,
                rf"""

        .. collapse::  🖱️ Click <b>here</b> to show maximum error estimation equation

            Generated with :any:`maximum_error_equation` (``{kwargs_str}``)

            You can access this equation via ``{decorated_fun.__name__}.maximum_error.equation`` and the executable Python function via ``{decorated_fun.__name__}.maximum_error``.

            .. math::

                {latexprinter.doprint(maxerror_eq)}

            {note}

        """,
            )
            if (seconds := (time.perf_counter() - time_before)) > 1:
                warnings.warn(
                    f"@from_sympy() decorator: "
                    f"Maximum error analysis for {decorated_fun.__name__} took {seconds} seconds. "
                    f"If you're seeing this as a user and it affects you negatively, consider "
                    f"opening an issue on GitLab (https://gitlab.com/tue-umphy/software/parmesan). "
                    f"If you've just added the new function {decorated_fun.__name__}, consider setting "
                    f"@from_sympy(generate_error_eq=False) to skip error analysis for it.",
                    ParmesanWarning,
                )

        if record:
            EQUATIONS.add(multiarg_wrapper)
        return multiarg_wrapper

    return decorator


def substitute_equations(expression, equations):
    """
    Apply equations to an expression.

    Args:
        expression: sympy expression to substitute values in
        equations (sequence of sympy.Equation or from_sympy-decorated function): list of equations to apply
    """

    def is_equation(eq):
        return hasattr(eq, "lhs") and hasattr(eq, "rhs")

    for eq in equations:
        # if eq is no equation but its .equation attribute is, use that
        if not is_equation(eq) and is_equation(
            eq_ := getattr(eq, "equation", None)
        ):
            eq = eq_
        expression = expression.subs(eq.lhs, eq.rhs)
    return expression
