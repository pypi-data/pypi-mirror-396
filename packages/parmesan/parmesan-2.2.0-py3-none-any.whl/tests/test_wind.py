# system modules
import unittest

# internal modules
import parmesan
from parmesan.units import units
from parmesan import wind

# external modules
import numpy as np


class WindTest(unittest.TestCase):
    def test_wind_direction(self):
        np.testing.assert_allclose(
            wind.wind_direction(
                u=(0, 1, 1, 0, -1),
                v=(1, 1, 0, -1, 0),
            )
            .to("degree")
            .m,
            (180, 225, 270, 0, 90),
        )

    def test_zero_wind_results_in_nan(self):
        with self.assertWarns(parmesan.errors.ParmesanWarning):
            self.assertTrue(np.isnan(wind.wind_direction(u=0, v=0)))
            np.testing.assert_allclose(
                wind.wind_direction(u=[0, 0, 0], v=[0, 0, 0]).m,
                [np.nan, np.nan, np.nan],
            )

    def test_wind_direction_round_trip(self):
        for angle in np.arange(-180, 361, 10):
            with self.subTest(angle=angle):
                self.assertAlmostEqual(
                    parmesan.vector.normalize_angle(
                        wind.wind_direction(
                            u=wind.wind_component_eastward(
                                speed=1, direction=angle * units.degree
                            ),
                            v=wind.wind_component_northward(
                                speed=1, direction=angle * units.degree
                            ),
                        )
                    ),
                    parmesan.vector.normalize_angle(angle * units.degree),
                )

    def test_yamartino_wind_average(self):
        self.assertAlmostEqual(
            wind.yamartino_average(
                direction=np.array([359, 1]) * units.degree
            ).to("degree"),
            360 * units.degree,
        )

    def test_yamartino_wind_stdv(self):
        self.assertAlmostEqual(
            wind.yamartino_stdev(direction=np.array([5.04, 5.13, 5.11, 5.0])),
            0.0524,
            places=4,
        )

    def test_head_wind_cross_wind(self):
        np.testing.assert_allclose(
            wind.head_wind_component(
                yaw=np.arange(0, 2 * np.pi, 0.5 * np.pi),
                u=(1, 1, 1, 1),
                v=(0, 0, 0, 0),
            )
            .to("m/s")
            .m,
            (0, 1, 0, -1),
            atol=1e-15,
        )
        np.testing.assert_allclose(
            wind.cross_wind_component(
                yaw=np.arange(0, 2 * np.pi, 0.5 * np.pi),
                u=(1, 1, 1, 1),
                v=(0, 0, 0, 0),
            )
            .to("m/s")
            .m,
            (1, 0, -1, 0),
            atol=1e-15,
        )
