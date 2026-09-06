"""Two-dimensional geometric operations used by MotionLab.

This module contains generic geometry only. It does not define anatomical
joint angles or biomechanical movement conventions.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def _as_finite_2d_array(value: ArrayLike, *, name: str) -> np.ndarray:
    """Convert an input to a finite NumPy float array with shape (2,)."""
    array = np.asarray(value, dtype=float)

    if array.shape != (2,):
        raise ValueError(
            f"{name} must contain exactly two coordinates; "
            f"received shape {array.shape}."
        )

    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values.")

    return array


def _vector_norm_2d(vector: np.ndarray) -> float:
    """Return a numerically robust Euclidean norm for a 2D vector."""
    return float(np.hypot(vector[0], vector[1]))


def angle_between_vectors_deg(u: ArrayLike, v: ArrayLike) -> float:
    """Return the unsigned included angle between two 2D vectors in degrees.

    Parameters
    ----------
    u, v:
        Two-dimensional vectors.

    Returns
    -------
    float
        Included geometric angle in the range [0, 180] degrees.

    Raises
    ------
    ValueError
        If an input is not a finite 2D vector or either vector has zero
        magnitude.

    Notes
    -----
    The vectors are normalized and the included angle is calculated using

        atan2(|det(u_hat, v_hat)|, u_hat dot v_hat)

    where ``u_hat`` and ``v_hat`` are unit vectors. This formulation retains
    the unsigned angle convention while providing better numerical behavior
    near 0 and 180 degrees than an arccos-only formulation.
    """
    u_array = _as_finite_2d_array(u, name="u")
    v_array = _as_finite_2d_array(v, name="v")

    u_norm = _vector_norm_2d(u_array)
    v_norm = _vector_norm_2d(v_array)

    if u_norm == 0.0 or v_norm == 0.0:
        raise ValueError("Angle is undefined for a zero-length vector.")

    u_unit = u_array / u_norm
    v_unit = v_array / v_norm

    determinant = float(
        u_unit[0] * v_unit[1] - u_unit[1] * v_unit[0]
    )
    dot_product = float(np.dot(u_unit, v_unit))

    angle_radians = np.arctan2(abs(determinant), dot_product)
    angle_degrees = np.degrees(angle_radians)

    return float(angle_degrees)


def angle_from_points_deg(
    a: ArrayLike,
    b: ArrayLike,
    c: ArrayLike,
) -> float:
    """Return the unsigned 2D angle ABC, with B as the vertex, in degrees."""
    a_array = _as_finite_2d_array(a, name="a")
    b_array = _as_finite_2d_array(b, name="b")
    c_array = _as_finite_2d_array(c, name="c")

    u = a_array - b_array
    v = c_array - b_array

    return angle_between_vectors_deg(u, v)
