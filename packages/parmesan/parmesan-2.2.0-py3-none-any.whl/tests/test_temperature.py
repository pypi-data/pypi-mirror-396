# system modules
import itertools
import unittest

# internal modules
import parmesan
from parmesan.units import units, transfer
from parmesan.gas import temperature

# external modules
import numpy as np
import metpy.calc


class TemperatureTest(unittest.TestCase):
    def test_potential_temperature_direction(self):
        for T in units.Quantity(np.arange(5, 30, 5), "celsius"):
            self.assertGreater(
                temperature.potential_temperature(
                    temperature=T, pressure=units("900 hPa")
                ),
                T,
            )
            self.assertLess(
                temperature.potential_temperature(
                    temperature=T, pressure=units("1100 hPa")
                ),
                T,
            )

    def test_virtual_potential_temperature_coarse(self):
        for T in units.Quantity(np.arange(5, 30, 5), "celsius"):
            for p in np.array([900, 1000, 1100]) * units.hPa:
                self.assertEqual(
                    temperature.virtual_potential_temperature(
                        temperature=T,
                        pressure=p,
                        specific_humidity=0,
                    ),
                    temperature.potential_temperature(
                        temperature=T,
                        pressure=p,
                    ),
                )
                self.assertGreater(
                    temperature.virtual_potential_temperature(
                        temperature=T,
                        pressure=p,
                        specific_humidity=0.1,
                    ),
                    temperature.potential_temperature(
                        temperature=T,
                        pressure=p,
                    ),
                )

    def test_potential_temperature_similar_to_metpy(self):
        def C(x):
            return units.Quantity(x, "°C")

        # values taken off random Stüve diagram https://tinyurl.com/ychzwrv7
        for T, p in itertools.product(
            units.Quantity(np.array([-60, -10, 0, 10, 60]), "°C"),
            np.array([100, 200, 500, 1000, 1100]) * units.hPa,
        ):
            with self.subTest(T=T, p=p):
                self.assertAlmostEqual(
                    temperature.potential_temperature(
                        temperature=T, pressure=p
                    ),
                    transfer(
                        metpy.calc.potential_temperature(
                            temperature=transfer(T, metpy.units.units),
                            pressure=transfer(p, metpy.units.units),
                        )
                    ),
                    delta=units("0.07 K"),
                )

    def test_virtual_temperature_same_without_humidity(self):
        for T in units.Quantity(np.arange(5, 30, 5), "celsius"):
            with self.subTest(T=T):
                self.assertAlmostEqual(
                    temperature.virtual_temperature(
                        temperature=T,
                        pressure=units("1000 hPa"),
                        relative_humidity=0,
                    ),
                    T,
                    places=3,
                )
            self.assertEqual(
                temperature.virtual_temperature(
                    temperature=T,
                    mixing_ratio=0,
                ),
                T,
            )
            self.assertEqual(
                temperature.virtual_temperature(
                    temperature=T,
                    specific_humidity=0,
                ),
                T,
            )
            self.assertEqual(
                temperature.virtual_temperature(
                    temperature=T,
                    pressure=units("1000 hPa"),
                    water_vapour_pressure=units("0 hPa"),
                ),
                T,
            )

    def test_virtual_temperature_is_larger(self):
        for T, percentage in itertools.product(
            units.Quantity(np.arange(5, 30, 5), "celsius"),
            np.arange(10, 101, 10) * units.percent,
        ):
            with self.subTest(temperature=T, relative_humidity=percentage):
                self.assertGreater(
                    temperature.virtual_temperature(
                        temperature=T,
                        pressure=units("1023 hPa"),
                        relative_humidity=percentage,
                    ),
                    T,
                )
            with self.subTest(temperature=T, mixing_ratio=percentage):
                self.assertGreater(
                    temperature.virtual_temperature(
                        temperature=T, mixing_ratio=percentage
                    ),
                    T,
                )

    @staticmethod
    def Tv_from_mixing_ratio_rule_of_thumb_608(temperature, mixing_ratio):
        """
        https://en.wikipedia.org/w/index.php?title=Virtual_temperature&oldid=1099169099#Variations
        """
        return temperature.to("kelvin") * (1 + 0.608 * mixing_ratio)

    @staticmethod
    def Tv_from_mixing_ratio_rule_of_thumb_celsius(temperature, mixing_ratio):
        """
        https://en.wikipedia.org/w/index.php?title=Virtual_temperature&oldid=1099169099#Variations
        """
        return units.Quantity(
            temperature.to("celsius").m + mixing_ratio.to("g/kg").m / 6,
            "celsius",
        )

    def test_virtual_temperature_rule_of_thumb_608(self):
        for T, percentage in itertools.product(
            units.Quantity(np.arange(5, 30, 5), "celsius"),
            np.arange(0, 5, 1) * units.percent,
        ):
            with self.subTest(temperature=T, mixing_ratio=percentage):
                self.assertAlmostEqual(
                    temperature.virtual_temperature(
                        temperature=T, mixing_ratio=percentage
                    ).to("celsius"),
                    self.Tv_from_mixing_ratio_rule_of_thumb_608(
                        temperature=T, mixing_ratio=percentage
                    ).to("celsius"),
                    places=0,
                )

    def test_virtual_temperature_rule_of_thumb_celsius(self):
        for T, percentage in itertools.product(
            units.Quantity(np.arange(5, 30, 5), "celsius"),
            np.arange(0, 5, 1) * units.percent,
        ):
            with self.subTest(temperature=T, mixing_ratio=percentage):
                self.assertAlmostEqual(
                    temperature.virtual_temperature(
                        temperature=T, mixing_ratio=percentage
                    ).to("celsius"),
                    self.Tv_from_mixing_ratio_rule_of_thumb_celsius(
                        temperature=T, mixing_ratio=percentage
                    ).to("celsius"),
                    places=0,
                )
