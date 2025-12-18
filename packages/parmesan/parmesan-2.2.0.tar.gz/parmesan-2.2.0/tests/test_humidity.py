# system modules
import itertools
import unittest

# internal modules
from parmesan.units import units
from parmesan.gas import humidity

# external modules
import numpy as np


class HumidityTest(unittest.TestCase):
    def test_specific_humidity_via_densities(self):
        self.assertEqual(
            humidity.specific_humidity_via_densities(
                absolute_humidity=5 * units("g/m^3"),
                density=1 * units("kg/m^3"),
            ),
            0.005,
        )

    def test_specific_humidity_via_masses(self):
        self.assertEqual(
            humidity.specific_humidity_via_masses(
                water_vapour_mass=10 * units.gram,
                total_mass=1 * units.kg,
            ),
            0.01,
        )

    def test_relative_humidity_via_dewpoint(self):
        self.assertEqual(
            humidity.relative_humidity_via_dewpoint(
                dewpoint_temperature=300, temperature=300
            ),
            100 * units("percent"),
        )
        # The following values were taken from
        # https://wettermast.uni-hamburg.de/, 04.01.2020 13:00 CET
        self.assertAlmostEqual(
            humidity.relative_humidity_via_dewpoint(
                dewpoint_temperature=units.Quantity(1.1, "celsius"),
                temperature=units.Quantity(2.8, "celsius"),
            ),
            89 * units("percent"),
            places=2,
        )

    def test_magnus_round_trip(self):
        self.assertEqual(
            300 * units.kelvin,
            humidity.temperature_from_e_magnus_over_water(
                humidity.saturation_water_vapour_pressure_over_water_magnus(
                    T=300 * units.kelvin
                )
            ),
        )

    def test_dewpoint_at_full_relative_humidity(self):
        for temperature in units.Quantity(np.arange(0, 30, 5), "celsius"):
            with self.subTest(temperature=temperature):
                self.assertAlmostEqual(
                    humidity.dewpoint_from_relative_humidity(
                        relative_humidity=100 * units.percent,
                        temperature=temperature,
                    ),
                    temperature,
                )

    def test_dewpoint_at_relative_humidity_roundtrip(self):
        for temperature, relative_humidity in itertools.product(
            units.Quantity(np.arange(5, 30, 5), "celsius"),
            np.arange(10, 101, 10) * units.percent,
        ):
            with self.subTest(
                temperature=temperature, relative_humidity=relative_humidity
            ):
                dewpoint = humidity.dewpoint_from_relative_humidity(
                    temperature=temperature,
                    relative_humidity=relative_humidity,
                )
                RH = humidity.relative_humidity_via_dewpoint(
                    dewpoint_temperature=dewpoint, temperature=temperature
                )
                self.assertAlmostEqual(
                    relative_humidity.to("fraction"),
                    RH.to("fraction"),
                    places=1,
                )

    def test_absolute_humidity_from_dewpoint(self):
        self.assertAlmostEqual(
            humidity.absolute_humidity_from_dewpoint(
                dewpoint_temperature=units.Quantity(20, "°C")
            ),
            units("17 g/m³"),
            places=1,
        )
