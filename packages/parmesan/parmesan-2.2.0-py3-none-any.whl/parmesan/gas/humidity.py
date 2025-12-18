# system modules
import warnings

# internal modules
from parmesan.errors import ParmesanWarning
from parmesan.units import units
from parmesan import bounds
from parmesan import utils
from parmesan.gas import laws
from parmesan.utils.function import FunctionCollection
from parmesan.symbols import *

# external modules
import pint
import numpy as np
import sympy

water_vapour_pressure = FunctionCollection()
"""
Collection of functions to calculate water vapour pressure
"""


@water_vapour_pressure.register
@from_sympy()
def water_vapour_pressure_via_gas_law():
    # substitute gas law for water vapour
    return laws.gas_law_meteorology.equation.subs({ρ: ρ_w, p: e, R_s: R_h2o})
    # e = Rₕ₂ₒ⋅T⋅ρ_w


absolute_humidity = FunctionCollection()
r"""
Collection of functions to calculate absolute humidity :math:`\rho_\mathrm{w}`
"""


@absolute_humidity.register
@from_sympy(rearrange_from=water_vapour_pressure_via_gas_law)
def absolute_humidity_from_water_vapour_pressure():
    pass


@absolute_humidity.register
@units.ensure(
    "kg / m^3",
    relative_humidity="ratio",
    temperature="kelvin",
)
@bounds.ensure(
    (0, None),
    relative_humidity=(0, 1),
    temperature=(0, None),
)
def absolute_humidity_from_relative_humidity(relative_humidity, temperature):
    r"""
    Like :func:`absolute_humidity_from_water_vapour_pressure`, but use
    :func:`water_vapour_pressure_over_water_magnus` to calculate the water
    vapour pressure :math:`e` from relative humidity :math:`RH`:

    .. math::

        \rho_\mathrm{w} = \frac{RH \cdot e_\mathrm{s,Magnus}\left(T\right)}
            {R_\mathrm{H_2O} \cdot T}
    """
    return absolute_humidity_from_water_vapour_pressure(
        water_vapour_pressure=water_vapour_pressure_over_water_magnus(
            relative_humidity=relative_humidity, temperature=temperature
        ),
        temperature=temperature,
    )


@absolute_humidity.register
@units.ensure(
    "kg / m^3",
    dewpoint_temperature="kelvin",
)
@bounds.ensure(
    (0, None),
    dewpoint_temperature=(0, None),
)
def absolute_humidity_from_dewpoint(dewpoint_temperature):
    r"""
    Calculate the absolute humidity :math:`\rho_\mathrm{w}` from the dewpoint
    temperature :math:`T_\mathrm{d}` like
    :func:`absolute_humidity_from_water_vapour_pressure` using
    :func:`saturation_water_vapour_pressure_over_water_magnus`:

    .. math::

        \rho_\mathrm{w} = \frac
            {e_\mathrm{s,Magnus}\left(T_\mathrm{d}\right)}
            {R_\mathrm{H_2O} \cdot T_\mathrm{d}}
    """
    return absolute_humidity_from_water_vapour_pressure(
        water_vapour_pressure=(
            saturation_water_vapour_pressure_over_water_magnus(
                temperature=dewpoint_temperature
            )
        ),
        temperature=dewpoint_temperature,
    )


specific_humidity = FunctionCollection()
"""
Collection of functions to calculate specific humidity :math:`q`
"""


@specific_humidity.register
@from_sympy()
def specific_humidity_via_densities():
    """
    https://de.wikipedia.org/wiki/Luftfeuchtigkeit#Spezifische_Luftfeuchtigkeit
    """
    return ρ_w / ρ


@specific_humidity.register
@from_sympy()
def specific_humidity_via_masses():
    """
    https://de.wikipedia.org/wiki/Luftfeuchtigkeit#Spezifische_Luftfeuchtigkeit
    """
    return m_w / m_tot


@specific_humidity.register
@from_sympy()
def specific_humidity_via_pressures():
    ratio = M_h2o / M_dry
    return (ratio * e_w) / (pressure - (1 - ratio) * e_w)


@specific_humidity.register
@units.ensure(
    "ratio",
    relative_humidity="fraction",
    temperature="kelvin",
    pressure="Pa",
)
@bounds.ensure(
    (0, 1),
    relative_humidity=(0, 1),
    pressure=(0, None),
    temperature=(0, None),
)
def specific_humidity_via_relative_humidity(
    relative_humidity, pressure, temperature
):
    r"""
    Like :func:`specific_humidity_via_pressures` but calculate the water vapour
    pressure from the relative humidity via
    :func:`water_vapour_pressure_over_water_magnus`.

    https://de.wikipedia.org/wiki/Luftfeuchtigkeit#Spezifische_Luftfeuchtigkeit
    """
    return specific_humidity_via_pressures(
        water_vapour_pressure=water_vapour_pressure_over_water_magnus(
            relative_humidity=relative_humidity,
            temperature=temperature,
        ),
        pressure=pressure,
    )


mixing_ratio = FunctionCollection()
"""
Collection of functions to calculate the mixing ratio
"""


@mixing_ratio.register
@from_sympy()
def mixing_ratio_via_densities():
    """
    https://de.wikipedia.org/wiki/Luftfeuchtigkeit#Mischungsverh%C3%A4ltnis
    """
    return ρ_w / (ρ - ρ_w)


@mixing_ratio.register
@from_sympy()
def mixing_ratio_via_masses():
    """
    https://de.wikipedia.org/wiki/Luftfeuchtigkeit#Mischungsverh%C3%A4ltnis
    """
    return m_w / (m_tot - m_w)


@mixing_ratio.register
@from_sympy()
def mixing_ratio_via_pressures():
    r"""
    https://de.wikipedia.org/wiki/Luftfeuchtigkeit#Mischungsverh%C3%A4ltnis
    """
    return M_h2o / M_dry * e / (p - e)


@mixing_ratio.register
@units.ensure(
    "ratio",
    relative_humidity="fraction",
    pressure="Pa",
    temperature="K",
)
@bounds.ensure(
    (0, 1),
    relative_humidity=(0, 1),
    pressure=(0, None),
    temperature=(0, None),
)
def mixing_ratio_via_relative_humidity(
    relative_humidity, pressure, temperature
):
    r"""
    Like :func:`mixing_ratio_via_pressures` but use
    :func:`water_vapour_pressure_over_water_magnus` to calculate the water
    vapor pressure from the relative humidity.
    """
    return mixing_ratio_via_pressures(
        water_vapour_pressure=water_vapour_pressure_over_water_magnus(
            relative_humidity=relative_humidity, temperature=temperature
        ),
        pressure=pressure,
    )


saturation_water_vapour_pressure = FunctionCollection()
"""
Collection of functions to calculate the saturation water vapour pressure
"""

magnus_overrides = dict(
    bounds_override={
        str(T): (
            round(units.Quantity(-45, "celsius").to("kelvin").m, 2),
            round(units.Quantity(60, "celsius").to("kelvin").m, 2),
        )
    }
)


@saturation_water_vapour_pressure.register
@from_sympy(**magnus_overrides)
def saturation_water_vapour_pressure_over_water_magnus():
    """
    Water vapour saturation pressure over flat water according to the
    Magnus-formula

    - https://de.wikipedia.org/wiki/S%C3%A4ttigungsdampfdruck
    - WMO's `Guide to Meteorological Instruments and Methods of
      Observation <https://www.weather.gov/media/epz/mesonet/CWOP-WMO8.pdf>`_
    """
    # temperature comes as Kelvin but the formula expects °C 🙄
    T_ = T - T_c0
    return A_magnus * sympy.exp(
        ((B_magnus_w * T_) / ((C_magnus_w - T_c0) + T_))
    )


@saturation_water_vapour_pressure.register
@from_sympy(
    bounds_override={
        str(T): (
            round(units.Quantity(-65, "celsius").to("kelvin").m, 2),
            round(units.Quantity(0, "celsius").to("kelvin").m, 2),
        )
    }
)
def saturation_water_vapour_pressure_over_ice_magnus():
    """
    Water vapour saturation pressure over flat ice according to the
    Magnus-formula

    - https://de.wikipedia.org/wiki/S%C3%A4ttigungsdampfdruck
    - WMO's `Guide to Meteorological Instruments and Methods of
      Observation <https://www.weather.gov/media/epz/mesonet/CWOP-WMO8.pdf>`_
    """
    # temperature comes as Kelvin but the formula expects °C 🙄
    T_ = T - T_c0
    return A_magnus * sympy.exp(
        ((B_magnus_i * T_) / ((C_magnus_i - T_c0) + T_))
    )


@units.ensure(
    "kelvin",
    water_vapour_pressure="Pa",
)
@bounds.ensure(
    (
        round(units.Quantity(-45, "celsius").to("kelvin").m, 2),
        round(units.Quantity(60, "celsius").to("kelvin").m, 2),
    ),
    water_vapour_pressure=(0, None),
)
def temperature_from_e_magnus_over_water(
    water_vapour_pressure,
):
    """
    Inversion of :func:`saturation_water_vapour_pressure_over_water_magnus`

    - see WMO's `Guide to Meteorological Instruments and Methods of
      Observation <https://www.weather.gov/media/epz/mesonet/CWOP-WMO8.pdf>`_

    .. note::

        This implementation neglects the pressure and temperature dependent
        ``f(p)`` parameter mentioned in the WMO docs.

    """
    # can't use sympy.solve(saturation_water_vapour_pressure_over_water_magnus.equation,T)
    water_vapour_pressure = (
        (
            water_vapour_pressure
            if hasattr(water_vapour_pressure, "to")
            else (water_vapour_pressure * units.Pa)
        )
        .to("Pa")
        .magnitude
    )
    d = np.log(water_vapour_pressure / 611.2)
    return units.Quantity((243.12 * d / (17.62 - d)), "celsius").to("kelvin")


@water_vapour_pressure.register
@from_sympy(**magnus_overrides)
def water_vapour_pressure_over_water_magnus():
    return RH * saturation_water_vapour_pressure_over_water_magnus.equation.rhs


relative_humidity = FunctionCollection()
"""
Collection of functions to calculate relative humidity
"""


@relative_humidity.register
@from_sympy(**magnus_overrides)
def relative_humidity_via_water_vapour_pressure():
    return e / saturation_water_vapour_pressure_over_water_magnus.equation.rhs


@relative_humidity.register
@from_sympy(**magnus_overrides)
def relative_humidity_via_dewpoint():
    r"""
    Calculate relative humidity :math:`RH` from dewpoint temperature
    :math:`T_\mathrm{d}` and temperature :math:`T`:

    .. math::

        RH = \frac{T}{T_\mathrm{d}} \cdot
            \frac{e_\mathrm{s,Magnus}\left(T_\mathrm{d}\right)}
                 {e_\mathrm{s,Magnus}\left(T\right)}
    """
    e_s = saturation_water_vapour_pressure_over_water_magnus.equation.rhs
    return (T / T_d) * (e_s.subs(T, T_d) / e_s)


dewpoint = FunctionCollection()
"""
Collection of functions to calculate the dew point
"""


@dewpoint.register
@units.ensure(
    "kelvin",
    temperature="kelvin",
    relative_humidity="fraction",
)
@bounds.ensure(
    (0, None),
    temperature=(0, None),
    relative_humidity=(0, 1),
)
def dewpoint_from_relative_humidity(relative_humidity, temperature):
    r"""
    Calculate the dew point :math:`T_\mathrm{d}` from relative humidity
    :math:`RH` and temperature :math:`T`:

    .. math::

        T_\mathrm{d} = \frac
            {B\left[\mathrm{ln}\left(RH\right) + \frac{A \cdot T}{B+T}\right]}
            {A - \mathrm{ln}\left(RH\right) - \frac{A\cdot T}{B+T}}


    From `Lawrence (2005) <https://doi.org/10.1175/BAMS-86-2-225>`_ (parameter
    A seems to be missing a leading ``1`` there)

    .. warning::

        This doesn't seem to be a perfect inversion of
        :func:`relative_humidity_via_dewpoint`, round-tripping doesn't yield
        the exact same result (c.f. the tests).

        Neither `WolframAlpha
        <https://www.wolframalpha.com/input/?i=solve+exp%28%28bD%29%2F%28c%2BD%29%29%2FD+%3D+R+*+exp%28%28bT%29%2F%28c%2BT%29%29%2FT+for+real+D%2Cb%3D17.62>`_
        nor `SymPyGamma
        <https://sympygamma.com/input/?i=solve%28a*exp%28%28b*T%29%2F%28c%2BT%29%29%2FT+-+X%2CT%29>`_
        seem to be able to invert the equation analytically.

        If you need to calculate the dewpoint temperature from relative
        humidity more precisely, consider inverting
        :func:`relative_humidity_via_dewpoint` numerically and use/implement a
        more precise approximation than
        :func:`saturation_water_vapour_pressure_over_water_magnus`.
    """
    # get temperature magnitude in °C
    temperature = (
        (
            temperature
            if hasattr(temperature, "to")
            else (temperature * units.kelvin)
        )
        .to("celsius")
        .magnitude
    )
    A = 17.625
    B = 243.04
    frac = (A * temperature) / (B + temperature)
    log = np.log(relative_humidity.magnitude)
    dewpoint = (B * (log + frac)) / (A - log - frac)
    return units.Quantity(dewpoint, "celsius").to("kelvin")


__doc__ = rf"""
Equations
+++++++++

{formatted_list_of_equation_functions(locals().copy())}

API Documentation
+++++++++++++++++
"""
