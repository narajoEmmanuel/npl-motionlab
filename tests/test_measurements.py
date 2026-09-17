import math

import numpy as np
import pytest

from motionlab.measurements import (
    DEFINITIONS,
    evaluate_measurement,
    projected_knee_flexion_deg,
    projected_shank_foot_angle_deg,
    projected_trunk_inclination_deg,
)


def test_knee_flexion_straight_is_zero():
    assert projected_knee_flexion_deg((0, 0), (1, 0), (2, 0)) == pytest.approx(0.0)


def test_knee_flexion_right_angle_is_ninety():
    assert projected_knee_flexion_deg((0, 1), (0, 0), (1, 0)) == pytest.approx(90.0)


def test_shank_foot_is_unsigned_included_angle():
    assert projected_shank_foot_angle_deg((0, -1), (0, 0), (1, 0)) == pytest.approx(90.0)


def test_trunk_vertical_up_is_zero():
    assert projected_trunk_inclination_deg((10, 20), (10, 5)) == pytest.approx(0.0)


def test_trunk_horizontal_is_ninety():
    assert projected_trunk_inclination_deg((10, 20), (25, 20)) == pytest.approx(90.0)


def test_trunk_downward_is_one_eighty():
    assert projected_trunk_inclination_deg((10, 20), (10, 30)) == pytest.approx(180.0)


def test_trunk_uses_image_up_not_positive_y():
    assert projected_trunk_inclination_deg((0, 0), (1, -1)) == pytest.approx(45.0)


def test_registry_dependencies_are_explicit():
    assert DEFINITIONS["projected_knee_flexion"].dependencies == ("hip", "knee", "ankle")
    assert DEFINITIONS["projected_shank_foot_angle"].dependencies == ("knee", "ankle", "toe")
    assert DEFINITIONS["projected_trunk_inclination"].dependencies == ("hip", "shoulder")


def test_evaluate_measurement_reports_missing_landmark():
    result = evaluate_measurement(
        "projected_knee_flexion",
        {"hip": (0, 0), "knee": (1, 0)},
    )
    assert not result.valid
    assert result.value_deg is None
    assert result.invalid_reason == "missing_landmark"


def test_evaluate_measurement_reports_nonfinite_as_missing():
    result = evaluate_measurement(
        "projected_trunk_inclination",
        {"hip": (0, 0), "shoulder": (math.nan, -1)},
    )
    assert not result.valid
    assert result.invalid_reason == "missing_landmark"


def test_evaluate_measurement_reports_degenerate_geometry():
    result = evaluate_measurement(
        "projected_shank_foot_angle",
        {"knee": (0, 0), "ankle": (0, 0), "toe": (1, 0)},
    )
    assert not result.valid
    assert result.invalid_reason == "degenerate_geometry"


def test_evaluate_measurement_returns_valid_result():
    result = evaluate_measurement(
        "projected_trunk_inclination",
        {"hip": np.array([0.0, 0.0]), "shoulder": np.array([0.0, -2.0])},
    )
    assert result.valid
    assert result.value_deg == pytest.approx(0.0)
    assert result.invalid_reason is None


def test_unknown_measurement_is_rejected():
    with pytest.raises(ValueError, match="Unknown measurement definition"):
        evaluate_measurement("not-a-measurement", {})
