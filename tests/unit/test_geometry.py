"""Unit tests for MotionLab two-dimensional geometry."""

import math

import numpy as np
import pytest

from motionlab.geometry import (
    angle_between_vectors_deg,
    angle_from_points_deg,
)


@pytest.mark.parametrize(
    ("expected_angle", "point_c"),
    [
        (30.0, (math.sqrt(3.0) / 2.0, 0.5)),
        (45.0, (math.sqrt(2.0) / 2.0, math.sqrt(2.0) / 2.0)),
        (60.0, (0.5, math.sqrt(3.0) / 2.0)),
        (90.0, (0.0, 1.0)),
        (120.0, (-0.5, math.sqrt(3.0) / 2.0)),
        (180.0, (-1.0, 0.0)),
    ],
)
def test_angle_from_points_recovers_known_angles(
    expected_angle: float,
    point_c: tuple[float, float],
) -> None:
    """Recover analytically known included angles."""
    point_a = (1.0, 0.0)
    vertex_b = (0.0, 0.0)

    computed = angle_from_points_deg(point_a, vertex_b, point_c)

    assert computed == pytest.approx(expected_angle, abs=1e-12)


@pytest.mark.parametrize(
    ("u", "v"),
    [
        ((0.0, 0.0), (1.0, 0.0)),
        ((1.0, 0.0), (0.0, 0.0)),
    ],
)
def test_angle_between_vectors_rejects_zero_length_vectors(
    u: tuple[float, float],
    v: tuple[float, float],
) -> None:
    """Reject vectors whose direction is mathematically undefined."""
    with pytest.raises(ValueError, match="zero-length vector"):
        angle_between_vectors_deg(u, v)


@pytest.mark.parametrize(
    ("a", "b", "c"),
    [
        ((1.0, 1.0), (1.0, 1.0), (2.0, 1.0)),
        ((0.0, 1.0), (1.0, 1.0), (1.0, 1.0)),
    ],
)
def test_angle_from_points_rejects_coincident_vertex_points(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> None:
    """Reject a geometry where either segment has zero length."""
    with pytest.raises(ValueError, match="zero-length vector"):
        angle_from_points_deg(a, b, c)


def test_angle_between_vectors_rejects_non_2d_input() -> None:
    """Reject input outside the module's explicitly two-dimensional scope."""
    with pytest.raises(ValueError, match="exactly two coordinates"):
        angle_between_vectors_deg((1.0, 2.0, 3.0), (1.0, 0.0))


@pytest.mark.parametrize(
    "invalid_vector",
    [
        (1.0, np.nan),
        (np.inf, 1.0),
        (-np.inf, 1.0),
    ],
)
def test_angle_between_vectors_rejects_non_finite_coordinates(
    invalid_vector: tuple[float, float],
) -> None:
    """Reject NaN and infinite coordinate values."""
    with pytest.raises(ValueError, match="finite values"):
        angle_between_vectors_deg(invalid_vector, (1.0, 0.0))


def test_angle_from_points_is_translation_invariant() -> None:
    """A common translation of all points must preserve the angle."""
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 0.0])
    c = np.array([0.5, math.sqrt(3.0) / 2.0])
    translation = np.array([100.0, 250.0])

    baseline = angle_from_points_deg(a, b, c)
    translated = angle_from_points_deg(
        a + translation,
        b + translation,
        c + translation,
    )

    assert translated == pytest.approx(baseline, abs=1e-12)


def test_angle_from_points_is_invariant_to_positive_uniform_scale() -> None:
    """Positive uniform scaling must preserve the included angle."""
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 0.0])
    c = np.array([0.5, math.sqrt(3.0) / 2.0])
    scale = 7.5

    baseline = angle_from_points_deg(a, b, c)
    scaled = angle_from_points_deg(a * scale, b * scale, c * scale)

    assert scaled == pytest.approx(baseline, abs=1e-12)


def test_angle_between_vectors_is_symmetric() -> None:
    """Unsigned included angle must be unchanged when vector order is swapped."""
    u = np.array([1.0, 0.0])
    v = np.array([0.5, math.sqrt(3.0) / 2.0])

    angle_uv = angle_between_vectors_deg(u, v)
    angle_vu = angle_between_vectors_deg(v, u)

    assert angle_uv == pytest.approx(angle_vu, abs=1e-12)


def test_angle_preserves_small_nonzero_angle_near_zero() -> None:
    """Preserve angular information near the zero-degree boundary."""
    epsilon = 1e-8
    expected = math.degrees(math.atan(epsilon))

    computed = angle_between_vectors_deg(
        (1.0, 0.0),
        (1.0, epsilon),
    )

    assert computed == pytest.approx(expected, abs=1e-15)
    assert computed > 0.0


def test_angle_preserves_small_offset_from_180_degrees() -> None:
    """Preserve angular information near the 180-degree boundary."""
    epsilon = 1e-8
    expected = 180.0 - math.degrees(math.atan(epsilon))

    computed = angle_between_vectors_deg(
        (1.0, 0.0),
        (-1.0, epsilon),
    )

    assert computed == pytest.approx(expected, abs=1e-12)
    assert computed < 180.0


def test_angle_handles_extremely_small_nonzero_vectors() -> None:
    """Avoid norm underflow for valid nonzero two-dimensional vectors."""
    computed = angle_between_vectors_deg(
        (1e-300, 0.0),
        (0.0, 1e-300),
    )

    assert computed == pytest.approx(90.0, abs=1e-12)


def test_angle_handles_extremely_large_finite_vectors() -> None:
    """Avoid intermediate overflow for large finite vector magnitudes."""
    computed = angle_between_vectors_deg(
        (1e300, 0.0),
        (0.0, 1e300),
    )

    assert computed == pytest.approx(90.0, abs=1e-12)
