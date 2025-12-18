# system modules
import unittest

# internal modules
import parmesan
from parmesan.units import units

# external modules
import pandas as pd


class ExplicitUnitModeTest(unittest.TestCase):
    def setUp(self):
        parmesan.units.mode.state = "implicit"

    def tearDown(self):
        parmesan.units.mode.state = "implicit"

    def test_explicit_units_mode(self):
        @units.ensure(
            "Pa",
            temperature="kelvin",
            density=units.kg / units.meter**3,
            gas_constant="J / ( kg * kelvin )",
        )
        def calculate_pressure(
            temperature, density, gas_constant, useless=None
        ):
            return density * gas_constant * temperature

        self.assertEqual(
            1033.2 * units.hPa,
            calculate_pressure(300, 1.2, 287, useless=dict).to("hPa"),
        )

        # invalid units raise an error
        with self.assertRaises(ValueError):
            calculate_pressure(300 * units.pascal, 1.2, 287)

        # With explicit unit mode enabled, all arguments need to have a unit
        with parmesan.units.mode("explicit"):
            with self.assertRaises(ValueError):
                calculate_pressure(300, 1.2, 287).to("hPa")
            self.assertEqual(
                1033.2 * units.hPa,
                calculate_pressure(
                    300 * units.kelvin,
                    1.2 * units.kg / units.meter**3,
                    units.Quantity(287, "J/(kg*K)"),
                ),
            )

        with parmesan.units.mode("implicit"):
            self.assertEqual(
                1033.2 * units.hPa,
                calculate_pressure(300, 1.2, 287).to("hPa"),
            )
            self.assertEqual(
                1033.2 * units.hPa,
                calculate_pressure(
                    300 * units.kelvin,
                    1.2 * units.kg / units.meter**3,
                    units.Quantity(287, "J/(kg*K)"),
                ),
            )

        parmesan.units.mode.state = "implicit"
        self.assertEqual(
            1033.2 * units.hPa,
            calculate_pressure(300, 1.2, 287).to("hPa"),
        )
        self.assertEqual(
            1033.2 * units.hPa,
            calculate_pressure(
                300 * units.kelvin,
                1.2 * units.kg / units.meter**3,
                units.Quantity(287, "J/(kg*K)"),
            ),
        )

        parmesan.units.mode.state = "explicit"
        with self.assertRaises(ValueError):
            self.assertEqual(
                1033.2 * units.hPa,
                calculate_pressure(300, 1.2, 287).to("hPa"),
            )
        self.assertEqual(
            1033.2 * units.hPa,
            calculate_pressure(
                300 * units.kelvin,
                1.2 * units.kg / units.meter**3,
                units.Quantity(287, "J/(kg*K)"),
            ),
        )

        with parmesan.units.mode(None):
            self.assertEqual(
                1033.2e2,
                calculate_pressure(300, 1.2, 287),
            )

    def test_pint_array(self):
        df = pd.DataFrame(
            dict(
                temperature=pd.Series([25, 30.2, 45], dtype="pint[°C]"),
                pressure=[990, 995, 1000.1],
            )
        )
        df["pressure"] = df["pressure"].astype("pint[hPa]")
        df["Tpot"] = parmesan.gas.temperature.potential_temperature(
            temperature=df["temperature"], pressure=df["pressure"]
        )
        with self.assertRaises(ValueError):
            parmesan.gas.temperature.potential_temperature(
                temperature=df["temperature"], pressure=df["temperature"]
            )
