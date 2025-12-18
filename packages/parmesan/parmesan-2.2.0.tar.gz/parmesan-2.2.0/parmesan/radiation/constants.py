# system modules
import warnings

# internal modules
from parmesan.symbols import stefan_boltzmann_constant

# external modules

__doc__ = """

.. note::

    .. deprecated:: 2.0

        This module is deprecated. Use values from :mod:`parmesan.symbols` instead.

"""

warnings.warn(
    f"""
The parmesan.radiation.constants module is deprecated. Use values from :mod:`parmesan.symbols` instead.
""".strip()
)

STEFAN_BOLTZMANN_CONSTANT = stefan_boltzmann_constant.quantity
