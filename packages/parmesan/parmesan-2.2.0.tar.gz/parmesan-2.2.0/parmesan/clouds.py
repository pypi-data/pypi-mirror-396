# system modules
import warnings

# internal modules
from parmesan.units import units
from parmesan import bounds

# external modules


@units.ensure(
    "m",
    temperature="kelvin",
    dewpoint_temperature="kelvin",
)
@bounds.ensure(
    (0, None),
    temperature=(0, None),
    dewpoint_temperature=(0, None),
)
def lifted_condensation_level_espy(temperature, dewpoint_temperature):
    r"""
    Calculate the lifted condensation level LCL :math:`z_{LCL}` (in m) from the
    temperature :math:`T`: and dew point temperature :math:`T_d` on the ground.

    .. math::
        z_{LCL} = 125 \cdot (T - T_d)

    Taken from the "approximate expression from the LCL" by James Espy at:
    https://en.wikipedia.org/wiki/Lifted_condensation_level
    """
    return 125 * units("m/K") * (temperature - dewpoint_temperature)
