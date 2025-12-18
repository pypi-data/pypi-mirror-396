# system modules
import unittest
import warnings
import itertools

# internal modules
from parmesan.units import units
from parmesan import clouds

# external modules
import numpy as np


class LCLTest(unittest.TestCase):
    def test_lcl_plausibility(self):
        self.assertAlmostEqual(
            clouds.lifted_condensation_level_espy(
                temperature=units.Quantity(20, "°C"),
                dewpoint_temperature=units.Quantity(15, "°C"),
            ),
            units("650m"),
            delta=units("50m"),
        )
