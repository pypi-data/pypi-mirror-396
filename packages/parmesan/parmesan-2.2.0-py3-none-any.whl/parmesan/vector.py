# system modules

# internal modules
from parmesan.units import units
from parmesan import bounds
from parmesan.utils import ignore_warnings


# external modules
import numpy as np
import pint


@units.ensure("dimensionless", angle="radians")
@bounds.ensure((-1, 1))
@ignore_warnings(pint.UnitStrippedWarning)
def rotation_matrix(angle):
    """
    Create a rotation matrix to rotate coordinates in the mathematical
    direction (counter-clockwise).

    Example
    -------

    To rotate a vector with coordiates ``x`` and ``y`` with this matrix, stack
    ``x`` and ``y`` into a matrix as rows and multiply it to the rotation
    matrix:

    .. code-block:: python

        # vector coordinates
        x = [0,1,0,-1]
        y = [1,0,-1,0]
        # matrix multiplication
        x_rot, y_rot = rotation_matrix(45 * units.degree) @ np.array([x,y])
        x_rot
        # [-0.70710678,  0.70710678,  0.70710678, -0.70710678]
        y_rot
        # [ 0.70710678,  0.70710678, -0.70710678, -0.70710678]

    Args:
        angle: the mathematical angle to rotate

    Returns:
        2x2 :any:`numpy.ndarray`: the rotation matrix

    """
    return np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )


@units.ensure("radians", angle="radians")
@bounds.ensure((0, 2 * np.pi))
def normalize_angle(angle):
    """
    Normalize an angle to values between 0 and one full circle.

    Args:
        angle: the angle to normalize

    Returns:
        the normalized angle
    """
    return np.mod(angle, 2 * np.pi)


@units.ensure("radians", angle="radians")
@bounds.ensure((0, 2 * np.pi))
def to_mathematical_angle(angle, inverted, clockwise, math_origin):
    """
    Convert an angle to its mathematical definition

    Args:
        angle: the angle to convert
        inverted (bool): whether the given angle references the inverted vector
        clockwise (bool): whether the given angle was counted in the clockwise
            direction
        math_origin (bool): whether the given angle's reference point is the
            positive x-axis (the mathematical inverted)

    Returns:
        the angle converted to the mathematical representation
    """
    if inverted:
        angle -= np.pi
    if clockwise:
        angle *= -1
    if not math_origin:
        angle += np.pi / 2
    return normalize_angle(angle)


@units.ensure("radians", angle="radians")
@bounds.ensure((0, 2 * np.pi))
def convert_mathematical_angle(angle, inverted, clockwise, math_origin):
    """
    Convert a mathematical angle to a different representation

    Args:
        angle: the mathematical angle to convert
        inverted (bool): whether to invert the vector
        clockwise (bool): whether the output angle is to be counted in the
            clockwise direction
        math_origin (bool): whether the output angle's reference point should
            be the positive x-axis (the mathematical inverted)
    """
    if not math_origin:
        angle -= np.pi / 2  # now counter-clockwise angle from positive y-axis
    if clockwise:
        angle *= -1  # now clockwise angle from reference axis
    if inverted:
        angle += np.pi  # now angle to inverted vector
    return normalize_angle(angle)


@units.ensure("radians")
@bounds.ensure((0, 2 * np.pi))
def angle(x, y, inverted, clockwise, math_origin):
    """
    Calculate the angle of a vector

    Args:
        x,y : the coordinates
        inverted: determine the angle to the inverted vector
        clockwise: determine the angle in clockwise direction
        math_origin: determine the angle from the mathematical origin (the
            positive axis of abscissa / x-axis). If ``False`` Use the positive
            axis of ordinates (y-axis) as reference.

    Returns:
        the angle
    """
    return normalize_angle(
        convert_mathematical_angle(
            np.arctan2(y, x),
            inverted=inverted,
            clockwise=clockwise,
            math_origin=math_origin,
        )
    )
