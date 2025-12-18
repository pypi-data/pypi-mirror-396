# system modules
import itertools
import unittest

# internal modules
import parmesan
from parmesan.units import units, transfer
from parmesan.stability import (
    brunt_vaisala_frequency_from_potential_temperature,
    bulk_richardson_number,
    gradient_richardson_number,
)

# external modules
import numpy as np
import metpy.calc
from metpy.units import units as unitMet


class StabilityTest(unittest.TestCase):
    def test_brunt_vaisala_similar_to_metpy(self):
        def C(x):
            return units.Quantity(x, "1 / s")

        for T, h in itertools.product(
            units.Quantity(
                np.array(
                    [[0.1, 0.2, 0.3], [10, 20, 30], [-6, 0, 6], [-60, 0, 60]]
                ),
                "celsius",
            ).to("kelvin"),
            np.array([[1, 2, 3], [10, 20, 30], [100, 200, 300]]) * units.m,
        ):
            with self.subTest(T=T, h=h):
                np.testing.assert_array_almost_equal(
                    brunt_vaisala_frequency_from_potential_temperature(
                        potential_temperature=T,
                        potential_temperature_vertical_gradient=transfer(
                            metpy.calc.first_derivative(T, axis=0, x=h)
                        ),
                    )
                    .to_base_units()
                    .m,
                    transfer(
                        metpy.calc.brunt_vaisala_frequency(
                            height=transfer(h, metpy.units.units),
                            potential_temperature=transfer(
                                T, metpy.units.units
                            ),
                        )
                    )
                    .to_base_units()
                    .m,
                    decimal=3,
                )

    def test_gradient_richardson_number_similar_to_metpy(self):
        def C(x):
            return units.Quantity(x, " ")

        for T, u, h in itertools.product(
            units.Quantity(
                np.array([[1, 2, 3], [10, 20, 30], [-6, 0, 6], [5, 0, -5]]),
                "celsius",
            ).to("kelvin"),
            unitMet.Quantity(
                [[0, 0, 0], [1, 2, 3], [10, 20, 30], [30, 20, 10]], "m / s"
            ),
            np.array([[1, 2, 3], [10, 20, 30], [100, 200, 300]]) * units.m,
        ):
            with self.subTest(T=T, u=u, h=h):
                vptvg = units.Quantity(
                    metpy.calc.first_derivative(T, axis=0, x=h).magnitude,
                    metpy.calc.first_derivative(T, axis=0, x=h).units,
                )
                np.testing.assert_array_almost_equal(
                    gradient_richardson_number(
                        virtual_temperature=T,
                        dθvdz=vptvg,
                        duhdz=transfer(
                            metpy.calc.first_derivative(
                                transfer(u), axis=0, x=h
                            )
                        ),
                    )
                    .to_base_units()
                    .m,
                    transfer(
                        metpy.calc.gradient_richardson_number(
                            height=transfer(h, metpy.units.units),
                            potential_temperature=transfer(
                                T, metpy.units.units
                            ),
                            u=transfer(u, metpy.units.units),
                            v=unitMet.Quantity([0, 0, 0], "m/s"),
                            vertical_dim=0,
                        )
                    )
                    .to_base_units()
                    .m,
                    decimal=2,
                )

    def test_richardson_number_similar_to_metpy(self):
        def C(x):
            return units.Quantity(x, " ")

        for T, u, h in itertools.product(
            units.Quantity(
                np.array([[1, 2, 3], [1, 4, 6], [-1, 0, 1], [5, 0, -5]]),
                "celsius",
            ).to("kelvin"),
            unitMet.Quantity(
                [[0, 0, 0], [1, 2, 3], [10, 20, 30], [30, 20, 10]], "m / s"
            ),
            np.array([[0.1, 0.2, 0.3], [0.01, 0.02, 0.03]]) * units.m,
        ):
            with self.subTest(T=T, u=u, h=h):
                vptv = transfer(T[-1] - T[0])
                self.assertAlmostEqual(
                    bulk_richardson_number(
                        virtual_temperature=transfer(T[1]),
                        virtual_potential_temperature_vertical_difference=vptv,
                        Δzu_h=transfer(u[-1] - u[0]),
                        Δz=transfer(h[-1] - h[0]),
                    ),
                    transfer(
                        metpy.calc.gradient_richardson_number(
                            height=transfer(h, metpy.units.units),
                            potential_temperature=transfer(
                                T, metpy.units.units
                            ),
                            u=transfer(u, metpy.units.units),
                            v=transfer(
                                unitMet.Quantity([0, 0, 0], "m/s"),
                                metpy.units.units,
                            ),
                            vertical_dim=0,
                        )[1]
                    ),
                    delta=units("0.01"),
                )
