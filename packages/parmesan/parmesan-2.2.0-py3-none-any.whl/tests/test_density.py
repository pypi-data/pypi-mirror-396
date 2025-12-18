# system modules
import itertools
import unittest

# internal modules
import parmesan
from parmesan.units import units, transfer
from parmesan.gas.density import (
    density,
    density_dry_air,
    density_humid_air_absolute_humidity,
)

# external modules
import numpy as np
import metpy.calc


class DensityTest(unittest.TestCase):
    def test_no_pressure_no_density(self):
        self.assertEqual(
            density_dry_air(
                temperature=units("300 K"), pressure=units("0 hPa")
            ),
            units("0 kg/m³"),
        )

    def test_normal_conditions(self):
        self.assertAlmostEqual(
            density_dry_air(
                temperature=units.Quantity(20, "°C"),
                pressure=units("1023 hPa"),
            ),
            units("1.21 kg/m³"),
            places=1,
        )

    def test_dry_humidity(self):
        self.assertAlmostEqual(
            density_dry_air(
                temperature=units.Quantity(20, "°C"),
                pressure=units("1023 hPa"),
            ),
            density_humid_air_absolute_humidity(
                temperature=units.Quantity(20, "°C"),
                pressure=units("1023 hPa"),
                absolute_humidity=units("0 g/m³"),
            ),
        )

    def test_humidity_makes_less_dense(self):
        state = dict(
            temperature=units.Quantity(20, "°C"), pressure=units("1023 hPa")
        )
        for abshum in np.array([1, 10, 100]) * units("g/m³"):
            with self.subTest(absolute_humidity=abshum):
                self.assertLess(
                    density_humid_air_absolute_humidity(
                        absolute_humidity=abshum, **state
                    ),
                    density_dry_air(**state),
                )

    def test_density_similar_to_metpy(self):
        def C(x):
            return units.Quantity(x, "kg / m^3")

        # values taken off random Stüve diagram https://tinyurl.com/ychzwrv7
        for T, p, q in itertools.product(
            units.Quantity(np.array([-60, -10, 0, 10, 60]), "°C"),
            np.array([100, 200, 500, 1000, 1100]) * units.hPa,
            units.Quantity(np.array([0, 0.001, 0.01, 0.05, 0.1]), "Kg/Kg"),
        ):
            with self.subTest(T=T, p=p, q=q):
                self.assertAlmostEqual(
                    density(
                        pressure=p,
                        temperature=T,
                        mixing_ratio=q,
                    ),
                    transfer(
                        metpy.calc.density(
                            pressure=transfer(p, metpy.units.units),
                            temperature=transfer(T, metpy.units.units),
                            mixing_ratio=transfer(q, metpy.units.units),
                        )
                    ),
                    delta=units("0.01 kg/m^3"),
                )
