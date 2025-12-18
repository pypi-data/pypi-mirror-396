# system modules
import unittest

# internal modules
from parmesan.units import units
from parmesan import radiation
from parmesan.symbols import stefan_boltzmann_constant

# external modules
import numpy as np


class RadiationTest(unittest.TestCase):
    def test_blackbody_radiation(self):
        self.assertAlmostEqual(
            radiation.blackbody_radiation(T_surf=1 * units.kelvin),
            stefan_boltzmann_constant.quantity * units("kelvin ^ 4"),
        )

    def test_emissivity_adjustment_no_change(self):
        self.assertAlmostEqual(
            radiation.adjust_radiation_temperature_to_other_emissivity(
                surface_temperature=(T := units.Quantity(30, "celsius")),
                emissivity_1=1,
                emissivity_2=1,
                ambient_temperature=0,
            ),
            T,
        )
