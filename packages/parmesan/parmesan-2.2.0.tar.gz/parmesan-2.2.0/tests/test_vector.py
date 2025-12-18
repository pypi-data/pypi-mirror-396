# system modules
import unittest

# internal modules
import parmesan
from parmesan.units import units
from parmesan import vector
from parmesan.utils import ignore_warnings

# external modules
import numpy as np
import pint


class RotationMatrixTest(unittest.TestCase):
    @ignore_warnings(pint.UnitStrippedWarning)
    def test_rotation(self):
        x = [0, 1, 0, -1]
        y = [1, 0, -1, 0]
        for angle, (x_rot, y_rot) in {
            90 * units.degree: ([-1, 0, 1, 0], [0, 1, 0, -1]),
            -45
            * units.degree: (
                [0.707, 0.707, -0.707, -0.707],
                [0.707, -0.707, -0.707, 0.707],
            ),
        }.items():
            mat = vector.rotation_matrix(angle)
            x_r, y_r = mat @ np.array([x, y])
            np.testing.assert_allclose(x_r, x_rot, atol=1e-2)
            np.testing.assert_allclose(y_r, y_rot, atol=1e-2)


class AngleTest(unittest.TestCase):
    def test_normalize_angle(self):
        for angle, normalized in {
            -360 * units.degree: 0 * units.degree,
            -270 * units.degree: 90 * units.degree,
            -3 * np.pi * units.radians: 180 * units.degree,
            90 * units.degree: 90 * units.degree,
            181.12 * units.degree: 181.12 * units.degree,
            -99 * units.degree: (360 - 99) * units.degree,
            -1111 * units.degree: 329 * units.degree,
        }.items():
            self.assertAlmostEqual(
                vector.normalize_angle(angle=angle), normalized
            )

    def test_to_mathematical_angle(self):
        for (given_angle, params), mathematical_angle in {
            (0 * units.degree, (False, False, False)): 90 * units.degree,
            (0 * units.degree, (False, False, True)): 0 * units.degree,
            (0 * units.degree, (False, True, False)): 90 * units.degree,
            (0 * units.degree, (False, True, True)): 0 * units.degree,
            (0 * units.degree, (True, False, False)): 270 * units.degree,
            (0 * units.degree, (True, False, True)): 180 * units.degree,
            (0 * units.degree, (True, True, False)): 270 * units.degree,
            (0 * units.degree, (True, True, True)): 180 * units.degree,
            (45 * units.degree, (True, False, True)): 225 * units.degree,
            (135 * units.degree, (False, True, True)): 225 * units.degree,
            (225 * units.degree, (True, False, True)): 45 * units.degree,
        }.items():
            kwargs = dict(
                zip(("inverted", "clockwise", "math_origin"), params)
            )
            with self.subTest(angle=given_angle, **kwargs):
                math_angle = vector.to_mathematical_angle(
                    given_angle, **kwargs
                )
                self.assertAlmostEqual(
                    math_angle,
                    mathematical_angle,
                )
                self.assertAlmostEqual(
                    vector.convert_mathematical_angle(math_angle, **kwargs),
                    given_angle,
                )
