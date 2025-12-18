# system modules
import warnings

# internal modules
from parmesan.errors import ParmesanWarning
from parmesan.units import units
from parmesan import bounds
from parmesan import vector
from parmesan.utils.function import FunctionCollection
from parmesan.symbols import *

# external modules
import sympy
import numpy as np


@units.ensure("radians", u="m/s", v="m/s")
@bounds.ensure((0, 2 * np.pi))
def wind_direction(u, v):
    """
    Calculate the meteorological wind direction from the wind vector
    components. This direction is the angle from the positive axis of ordinates
    ("y-axis" / the north direction) to the inverted tip of the wind vector in
    clockwise direction.

    See `Wind Direction <../notebooks/wind-direction.ipynb>`_ for a visual
    representation.

    Args:
        u : latitudinal wind vector component (positive when wind goes *to the
            north*)
        v : longitudinal wind vector component (positive when wind goes *to the
            east*)

    Returns:
        the meteorological wind direction angle (wind **from** North=0°, wind
        **from** East=90°, etc.) in radians
    """
    meteorological_wind_definition = dict(
        inverted=True, clockwise=True, math_origin=False
    )
    angle = vector.angle(
        x=u,
        y=v,
        inverted=True,
        clockwise=True,
        math_origin=False,
    )
    # determine zero-wind conditions (where angle isn't well-defined)
    zerowind = (u == 0) & (v == 0)
    n_zerowind = np.sum(zerowind)
    if n_zerowind:
        warnings.warn(
            "{} zero-wind values were masked".format(n_zerowind),
            category=ParmesanWarning,
        )
        # mask zero-wind conditions in the output with nan
        angle = np.where(zerowind, np.nan, angle)
    return angle


@units.ensure("m/s", speed="m/s", direction="radians")
def wind_component_eastward(speed, direction):
    """
    Calculate the eastward wind component from wind speed and direction.

    Args:
        speed: the absolute wind speed
        direction: the meteorological wind direction (0° means wind coming from
            the north, 90° means wind coming from the east, etc...)

    Returns:
        the eastward wind component
    """
    return speed * np.cos(
        vector.to_mathematical_angle(
            direction,
            inverted=True,
            clockwise=True,
            math_origin=False,
        )
    )


@units.ensure("m/s", speed="m/s", direction="radians")
def wind_component_northward(speed, direction):
    """
    Calculate the northward wind component from wind speed and direction.

    Args:
        speed: the absolute wind speed
        direction: the meteorological wind direction (0° means wind coming from
            the north, 90° means wind coming from the east, etc...)

    Returns:
        the northward wind component
    """
    return speed * np.sin(
        vector.to_mathematical_angle(
            direction,
            inverted=True,
            clockwise=True,
            math_origin=False,
        )
    )


@units.ensure("radians", direction="radians")
@bounds.ensure((0, 2 * np.pi))
def yamartino_average(direction):
    """
    Calculate the average wind direction with the Yamartino algorithm.

    Args:
        direction: the meteorological wind direction
    """
    sin_average = np.mean(np.sin(direction))
    cos_average = np.mean(np.cos(direction))
    epsilon = np.sqrt(1 - (sin_average**2 + cos_average**2))
    direction_average = np.arctan2(sin_average, cos_average)
    return vector.normalize_angle(direction_average)


@units.ensure("radians", direction="radians")
def yamartino_stdev(direction):
    r"""
    Calculate wind direction standard deviation with the Yamartino algorithm.

    Args:
        direction: the meteorological wind direction
    """
    sin_average = np.mean(np.sin(direction))
    cos_average = np.mean(np.cos(direction))
    epsilon = np.sqrt(1 - (sin_average**2 + cos_average**2))
    direction_stdev = np.arcsin(epsilon) * (
        1 + (2 / np.sqrt(3) - 1) * epsilon**3
    )
    return direction_stdev


@from_sympy()
def head_wind_component():
    return u * sympy.sin(yaw) + v * sympy.cos(yaw)


@from_sympy()
def cross_wind_component():
    return u * sympy.cos(yaw) + v * sympy.sin(yaw)


@from_sympy(defaults={d: units("0 m")})
def wind_speed_logarithmic_wind_profile():
    """
    wind speed according to logarithmic wind profile (Stull, 1988, https://doi.org/10.1007/978-94-009-3027-8)
    """
    return friction_velocity / von_karman_constant * sympy.log((z - d) / z_0)
