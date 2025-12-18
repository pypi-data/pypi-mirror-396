# system modules
import unittest
import warnings
import itertools

# internal modules
from parmesan.units import units
from parmesan.gas.conversion import (
    trace_gas_mass_density_from_particle_ratio,
    trace_gas_particle_ratio_from_mass_density,
)
from parmesan.gas.temperature import potential_temperature
from parmesan.gas import constants
from parmesan.errors import ParmesanWarning

from parmesan.utils import (
    all_argument_combinations,
    single_argument_combinations,
)

# external modules
import numpy as np


class MassDensityToFromParticleRatio(unittest.TestCase):
    def test_round_trip(self):
        meteorology = {
            "pressure": 1000 * units.hPa,
            "temperature": units.Quantity(23, "celsius"),
            "R_s": constants.GAS_CONSTANT_CO2,
        }
        for particle_ratio in np.linspace(0, 1, 10):
            mass_density = trace_gas_mass_density_from_particle_ratio(
                trace_gas_particle_ratio=particle_ratio, **meteorology
            )
            self.assertAlmostEqual(
                particle_ratio,
                trace_gas_particle_ratio_from_mass_density(
                    trace_gas_mass_density=mass_density, **meteorology
                ),
                places=5,
            )

    def test_plausibility_known_volume(self):
        meteorology = {
            "temperature": units.Quantity(20, units.celsius),
            "pressure": 1000 * units.hPa,
        }
        # plausibility calculation with a known volume
        for co2_ppm in (0, 400, 1000, 10000, 1000000):
            with self.subTest(co2_ppm=co2_ppm):
                particles_in_cubic_meter = (
                    meteorology["pressure"]
                    * (1 * units.meter**3)
                    / constants.BOLTZMANN_CONSTANT
                    / meteorology["temperature"].to("kelvin")
                ).to("dimensionless")
                co2_particles_in_cubic_meter = (
                    co2_ppm * units.ppm * particles_in_cubic_meter
                )
                co2_mass = (
                    co2_particles_in_cubic_meter / constants.AVOGADRO_CONSTANT
                ) * constants.MOLAR_MASS_CO2
                self.assertAlmostEqual(
                    co2_mass / units.meter**3,
                    trace_gas_mass_density_from_particle_ratio(
                        trace_gas_particle_ratio=co2_ppm * units.ppm,
                        specific_gas_constant=constants.GAS_CONSTANT_CO2,
                        **meteorology,
                    ),
                )


class PotentialTemperatureTest(unittest.TestCase):
    def test_no_change_at_reference_pressure(self):
        for kwargs in all_argument_combinations(
            {
                "temperature": [
                    units.Quantity(24, "celsius"),
                    290,
                    np.array([200, 300, 400]),
                ],
                "reference_pressure": [
                    1000 * units.hPa,
                    200000,
                    np.array([1000000, 200000, 300000]),
                ],
            }
        ):
            with self.subTest(**kwargs):
                self.assertTrue(
                    np.allclose(
                        potential_temperature(
                            pressure=kwargs["reference_pressure"], **kwargs
                        ),
                        kwargs["temperature"]
                        if hasattr(kwargs["temperature"], "units")
                        else units.Quantity(kwargs["temperature"], "kelvin"),
                    ),
                    msg="Potential temperature at reference "
                    "pressure should stay the same!",
                )

    def test_plausibility(self):
        dpdz = (
            -(1.1 * units.kg / units.meter**3) * constants.EARTH_ACCELERATION
        )
        height = 1500 * units.meter
        pressure = 1000 * units.hPa + height * dpdz
        temperature = 290 * units.kelvin
        self.assertAlmostEqual(
            potential_temperature(temperature=temperature, pressure=pressure),
            temperature + (1 * units.kelvin / (100 * units.meter)) * height,
            places=1,
        )
