from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from motionlab.sports2d_adapter import (
    SPORTS2D_BODY_WITH_FEET_LANDMARKS,
    SPORTS2D_BODY_WITH_FEET_INTERACTIVE_LANDMARKS,
    semantic_landmarks_from_sports2d,
    projected_knee_flexion_from_sports2d,
    read_sports2d_pixel_trc,
)
from motionlab.measurements.definitions import evaluate_measurement


@pytest.fixture
def interactive_trc(tmp_path):
    # Invented pixels, deliberately different for each marker and each side.
    markers = [f"{prefix}{name}" for prefix in ("R", "L")
               for name in ("Shoulder", "Hip", "Knee", "Ankle", "BigToe", "SmallToe", "Heel")]
    header = "Frame#\tTime\t" + "\t".join(marker + "\t\t" for marker in markers)
    axes = "\t\t" + "\t".join(f"X{i}\tY{i}\tZ{i}" for i in range(1, len(markers) + 1))
    rows = ["\t".join([str(frame), str(frame / 30)] +
            [str(value) for i in range(len(markers)) for value in (101.25 + 17 * i + frame, 203.5 + 11 * i, 0)])
            for frame in (2, 1)]
    path = tmp_path / "synthetic_px_person00.trc"
    path.write_text("\n".join([header, axes, *rows]) + "\n", encoding="utf-8")
    return read_sports2d_pixel_trc(path)


@pytest.mark.parametrize("side,prefix", [("right", "R"), ("left", "L")])
def test_interactive_mapping_preserves_pixels_and_core_contract(interactive_trc, side, prefix):
    mapping = SPORTS2D_BODY_WITH_FEET_INTERACTIVE_LANDMARKS[side]
    assert mapping == {"shoulder": prefix + "Shoulder", "hip": prefix + "Hip",
                       "knee": prefix + "Knee", "ankle": prefix + "Ankle", "toe": prefix + "BigToe"}
    assert SPORTS2D_BODY_WITH_FEET_LANDMARKS[side] == {
        "hip": prefix + "Hip", "knee": prefix + "Knee", "ankle": prefix + "Ankle"}
    result = semantic_landmarks_from_sports2d(interactive_trc, side=side)
    assert result.sports2d_frame.tolist() == [2, 1]
    assert result.side.tolist() == [side, side]
    for role, marker in mapping.items():
        for axis in ("x", "y"):
            assert result[f"{role}_{axis}_px"].tolist() == interactive_trc[f"{marker}_{axis}_px"].tolist()
    core = projected_knee_flexion_from_sports2d(interactive_trc, side=side)
    for role in ("hip", "knee", "ankle"):
        for axis in ("x", "y"):
            assert core[f"{role}_{axis}_px"].tolist() == result[f"{role}_{axis}_px"].tolist()


@pytest.mark.parametrize("side,prefix", [("right", "R"), ("left", "L")])
@pytest.mark.parametrize("marker", ["Shoulder", "BigToe"])
def test_missing_interactive_column_is_explicit_and_knee_still_works(interactive_trc, side, prefix, marker):
    data = interactive_trc.drop(columns=[prefix + marker + "_x_px"])
    with pytest.raises(ValueError, match=prefix + marker + "_x_px"):
        semantic_landmarks_from_sports2d(data, side=side)
    assert projected_knee_flexion_from_sports2d(data, side=side).valid_geometry.all()


@pytest.mark.parametrize("side,prefix", [("right", "R"), ("left", "L")])
@pytest.mark.parametrize("role,marker,definition", [
    ("shoulder", "Shoulder", "projected_trunk_inclination"),
    ("toe", "BigToe", "projected_shank_foot_angle"),
])
def test_missing_interactive_coordinate_remains_explicit(interactive_trc, side, prefix, role, marker, definition):
    interactive_trc.loc[0, prefix + marker + "_x_px"] = np.nan
    row = semantic_landmarks_from_sports2d(interactive_trc, side=side).iloc[0]
    assert np.isnan(row[role + "_x_px"])
    points = {name: (row[name + "_x_px"], row[name + "_y_px"])
              for name in ("shoulder", "hip", "knee", "ankle", "toe")}
    result = evaluate_measurement(definition, points)
    assert not result.valid
    assert result.invalid_reason == "missing_landmark"


def test_interactive_mapping_rejects_unsupported_side(interactive_trc):
    with pytest.raises(ValueError, match="side must be"):
        semantic_landmarks_from_sports2d(interactive_trc, side="both")


def _write_fixture(path: Path) -> None:
    path.write_text(
        "PathFileType\t4\t(X/Y/Z)\tfixture.trc\n"
        "DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n"
        "30\t30\t4\t6\tpx\t30\t0\t4\n"
        "Frame#\tTime\tRHip\t\t\tRKnee\t\t\tRAnkle\t\t\tLHip\t\t\tLKnee\t\t\tLAnkle\t\t\t\n"
        "\t\tX1\tY1\tZ1\tX2\tY2\tZ2\tX3\tY3\tZ3\tX4\tY4\tZ4\tX5\tY5\tZ5\tX6\tY6\tZ6\n"
        "1\t0.0\t1\t0\t0\t0\t0\t0\t0\t1\t0\t-1\t0\t0\t0\t0\t0\t0\t-1\t0\n"
        "2\t0.033333\t1\t0\t0\t0\t0\t0\t-1\t0\t0\t-1\t0\t0\t0\t0\t0\t0\t1\t0\n"
        "3\t0.066667\t1\t0\t0\t0\t0\t0\t\t\t0\t-1\t0\t0\t0\t0\t0\t0\t1\t0\n"
        "4\t0.100000\t0\t0\t0\t0\t0\t0\t0\t1\t0\t-1\t0\t0\t0\t0\t0\t0\t1\t0\n",
        encoding="utf-8",
    )


def test_read_trc_preserves_frame_order_and_pixel_coordinates(tmp_path: Path) -> None:
    path = tmp_path / "fixture_px_person00.trc"
    _write_fixture(path)

    data = read_sports2d_pixel_trc(path)

    assert data["sports2d_frame"].tolist() == [1, 2, 3, 4]
    assert data["RHip_x_px"].tolist() == [1.0, 1.0, 1.0, 0.0]
    assert data.loc[0, "RAnkle_y_px"] == 1.0
    assert np.isnan(data.loc[2, "RAnkle_x_px"])


def test_right_side_uses_motionlab_geometry_and_preserves_invalid_rows(tmp_path: Path) -> None:
    path = tmp_path / "fixture_px_person00.trc"
    _write_fixture(path)
    data = read_sports2d_pixel_trc(path)

    result = projected_knee_flexion_from_sports2d(data, side="right")

    assert result.loc[0, "included_angle_deg"] == pytest.approx(90.0)
    assert result.loc[0, "projected_flexion_deg"] == pytest.approx(90.0)
    assert result.loc[1, "included_angle_deg"] == pytest.approx(180.0)
    assert result.loc[1, "projected_flexion_deg"] == pytest.approx(0.0)
    assert not bool(result.loc[2, "valid_geometry"])
    assert result.loc[2, "invalid_reason"] == "missing_landmark"
    assert np.isnan(result.loc[2, "projected_flexion_deg"])
    assert not bool(result.loc[3, "valid_geometry"])
    assert result.loc[3, "invalid_reason"] == "degenerate_geometry"


def test_left_side_mapping_is_explicit(tmp_path: Path) -> None:
    path = tmp_path / "fixture_px_person00.trc"
    _write_fixture(path)
    data = read_sports2d_pixel_trc(path)

    result = projected_knee_flexion_from_sports2d(data.iloc[[0]], side="left")

    assert result.loc[0, "hip_x_px"] == -1.0
    assert result.loc[0, "ankle_x_px"] == 0.0
    assert result.loc[0, "ankle_y_px"] == -1.0
    assert result.loc[0, "projected_flexion_deg"] == pytest.approx(90.0)


def test_missing_required_landmark_columns_are_rejected() -> None:
    data = pd.DataFrame({"sports2d_frame": [1], "sports2d_time_s": [0.0]})

    with pytest.raises(ValueError, match="missing required columns"):
        projected_knee_flexion_from_sports2d(data, side="right")


def test_trc_without_marker_header_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.trc"
    path.write_text("not a trc\n", encoding="utf-8")

    with pytest.raises(ValueError, match="marker header"):
        read_sports2d_pixel_trc(path)
