from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from motionlab.sports2d_adapter import (
    projected_knee_flexion_from_sports2d,
    read_sports2d_pixel_trc,
)


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
