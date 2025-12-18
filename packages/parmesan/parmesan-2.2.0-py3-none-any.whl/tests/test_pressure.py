# system modules
import itertools
import unittest

import parmesan
from parmesan.units import units, transfer
from parmesan.gas.pressure import (
    extrapolate_barometric_pressure_to_height_constant_temperature,
)

# external modules
import numpy as np
import metpy.calc


class PressureTest(unittest.TestCase):
    def test_barometric_pressure_similar_to_metpy(self):
        def C(x):
            return units.Quantity(x, "Pa")

        # The following variables are constants for a standard atmosphere
        # NOAA1976 National Oceanic and Atmospheric Administration, National Aeronautics and Space Administration,
        # and U. S. Air Force, 1976: U. S. Standard Atmosphere 1976, U.S. Government Printing Office, Washington, DC.

        t0 = units.Quantity(288.0, "kelvin")
        p0 = units.Quantity(1013.25, "hPa")
        # gamma = units.Quantity(6.5, 'K/km')

        # values taken off random Stüve diagram https://tinyurl.com/ychzwrv7
        for Alt in units.Quantity(
            np.array([-50, -10, 0, 10, 60, 80, 90]), "m"
        ):
            with self.subTest(
                Alt=Alt, ref_T=t0, ref_P=p0, ref_Alt=units.Quantity(0, "m")
            ):
                self.assertAlmostEqual(
                    extrapolate_barometric_pressure_to_height_constant_temperature(
                        z=Alt,
                        T_ref=t0,
                        p_ref=p0,
                        z_ref=units.Quantity(0, "m"),
                    ).to(
                        "hPa"
                    ),
                    transfer(
                        metpy.calc.height_to_pressure_std(
                            height=transfer(Alt, metpy.units.units)
                        )
                    ),
                    delta=units("1 Pa"),
                )
