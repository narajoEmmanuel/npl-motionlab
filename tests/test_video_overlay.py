"""Synthetic-only tests for the post-Core video visualization."""

import json

import cv2
import numpy as np
import pandas as pd
import pytest

from motionlab.video_overlay import main, render_angle_overlay


@pytest.fixture
def inputs(tmp_path):
    source = tmp_path / "synthetic.avi"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"MJPG"), 10, (320, 240))
    if not writer.isOpened():
        pytest.skip("Synthetic MJPG encoder unavailable.")
    for index in range(4):
        writer.write(np.full((240, 320, 3), index * 30, dtype=np.uint8))
    writer.release()
    rows = pd.DataFrame({
        "sports2d_frame": [0, 1, 2, 3], "side": ["right"] * 4,
        "hip_x_px": [60, np.nan, 60, 60], "hip_y_px": [60, np.nan, 60, 60],
        "knee_x_px": [120] * 4, "knee_y_px": [120] * 4,
        "ankle_x_px": [180] * 4, "ankle_y_px": [160] * 4,
        # Deliberately unrelated to point geometry: render this CSV value only.
        "projected_flexion_deg": [123.4, np.nan, np.nan, 57.8],
        "valid_geometry": [True, False, False, True],
        "invalid_reason": ["", "missing_landmark", "degenerate_geometry", ""],
    })
    csv = tmp_path / "knee_flexion.csv"
    rows.to_csv(csv, index=False, na_rep="NaN")
    return source, csv


def test_cli_renders_csv_angles_and_invalid_status_without_invalid_lines(inputs, tmp_path, monkeypatch):
    source, csv = inputs
    texts, lines = [], []
    original_text, original_line = cv2.putText, cv2.line
    def record_text(frame, text, *args):
        texts.append(text)
        return original_text(frame, text, *args)
    def record_line(frame, start, end, *args):
        lines.append((start, end))
        return original_line(frame, start, end, *args)
    monkeypatch.setattr(cv2, "putText", record_text)
    monkeypatch.setattr(cv2, "line", record_line)
    output = tmp_path / "new" / "overlay.mp4"
    assert main([str(source), str(csv), str(output)]) == 0
    assert "Projected flexion: 123.4 deg" in texts
    assert "Projected flexion: 57.8 deg" in texts
    assert texts.count("Projected flexion: invalid") == 2
    assert any("missing_landmark" in text for text in texts)
    assert any("degenerate_geometry" in text for text in texts)
    assert len(lines) == 4  # Two segments on each valid frame, none on invalid frames.
    capture = cv2.VideoCapture(str(output))
    values = []
    try:
        assert capture.get(cv2.CAP_PROP_FPS) == pytest.approx(10)
        while True:
            decoded, frame = capture.read()
            if not decoded:
                break
            assert frame.shape[:2] == (240, 320)
            values.append(float(frame[220, 300].mean()))
    finally:
        capture.release()
    assert len(values) == 4 and values == sorted(values)
    with pytest.raises(FileExistsError):
        render_angle_overlay(source, csv, output)


@pytest.mark.parametrize("defect", ["column", "frame_order", "invalid_angle", "valid_point", "side"])
def test_bad_csv_rejected_before_output(inputs, tmp_path, defect):
    source, csv = inputs
    rows = pd.read_csv(csv)
    if defect == "column":
        rows = rows.drop(columns="knee_x_px")
    elif defect == "frame_order":
        rows.loc[0, "sports2d_frame"] = 1
    elif defect == "invalid_angle":
        rows.loc[1, "projected_flexion_deg"] = 0
    elif defect == "valid_point":
        rows.loc[0, "hip_x_px"] = np.nan
    else:
        rows.loc[0, "side"] = "left"
    rows.to_csv(csv, index=False)
    with pytest.raises(ValueError):
        render_angle_overlay(source, csv, tmp_path / "rejected.mp4")
    assert not (tmp_path / "rejected.mp4").exists()


@pytest.mark.parametrize("count", [3, 5])
def test_decoded_frame_mismatch_leaves_no_final_or_partial_video(inputs, tmp_path, monkeypatch, count):
    source, csv = inputs
    rows = pd.read_csv(csv)
    if count == 3:
        rows = rows.iloc[:3]
    else:
        rows = pd.concat([rows, rows.iloc[[3]]], ignore_index=True)
        rows.loc[4, "sports2d_frame"] = 4
    rows.to_csv(csv, index=False)
    original_capture = cv2.VideoCapture
    class UnknownFrameCount:
        def __init__(self, path):
            self.capture = original_capture(path)
        def get(self, prop):
            return 0 if prop == cv2.CAP_PROP_FRAME_COUNT else self.capture.get(prop)
        def __getattr__(self, name):
            return getattr(self.capture, name)
    monkeypatch.setattr(cv2, "VideoCapture", UnknownFrameCount)
    with pytest.raises(ValueError, match="frame count mismatch"):
        render_angle_overlay(source, csv, tmp_path / "failed" / "overlay.mp4")
    assert not list((tmp_path / "failed").glob("*.mp4"))


def test_wrong_source_provenance_rejected(inputs, tmp_path):
    source, csv = inputs
    (tmp_path / "provenance.json").write_text(json.dumps({
        "schema_version": "motionlab.angle-pipeline.v1",
        "source_metadata": {"source_filename": source.name, "sha256": "wrong"},
    }))
    with pytest.raises(ValueError, match="does not match"):
        render_angle_overlay(source, csv, tmp_path / "overlay.mp4")
