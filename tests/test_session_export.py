import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from motionlab.session_export import export_session_bundle
from motionlab.sessions.database import (
    SessionDatabase,
    add_manual_correction,
    create_session,
    initialize_frames,
    register_video,
    store_automatic_landmark,
)


def _build_session(tmp_path: Path):
    db_path = tmp_path / "session.db"
    session_id = "session_" + "e" * 32
    with SessionDatabase(db_path) as connection:
        create_session(connection, selected_side="right", session_id=session_id, label="Synthetic export")
        register_video(
            connection,
            session_id=session_id,
            source_path=tmp_path / "source.mp4",
            sha256="a" * 64,
            decoded_width_px=640,
            decoded_height_px=480,
            fps=30.0,
            frame_count=2,
            duration_s=2 / 30,
        )
        initialize_frames(connection, session_id=session_id, frame_count=2, fps=30.0)
        points = {
            "shoulder": (0.0, -2.0),
            "hip": (0.0, 0.0),
            "knee": (0.0, 1.0),
            "ankle": (0.0, 2.0),
            "toe": (1.0, 2.0),
        }
        for frame in (0, 1):
            for role, (x, y) in points.items():
                store_automatic_landmark(
                    connection,
                    session_id=session_id,
                    frame_index=frame,
                    role=role,
                    x_px=x + frame,
                    y_px=y,
                )
        add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=0.5,
            y_px=0.0,
            note="synthetic",
        )
    return db_path, session_id


def test_export_bundle_writes_reviewed_effective_artifacts(tmp_path):
    db_path, session_id = _build_session(tmp_path)
    export_dir = tmp_path / "export"
    with SessionDatabase(db_path) as connection:
        outputs = export_session_bundle(
            connection,
            session_id=session_id,
            output_dir=export_dir,
            include_overlay_mp4=False,
        )

    assert set(outputs) == {
        "measurements_csv",
        "landmarks_csv",
        "session_json",
        "figure_png",
    }
    assert all(path.is_file() for path in outputs.values())

    payload = json.loads(outputs["session_json"].read_text(encoding="utf-8"))
    assert payload["schema_version"] == "motionlab.interactive-export.v1"
    assert len(payload["frames"]) == 2
    hip = payload["frames"][0]["landmarks"]["hip"]
    assert hip["source_state"] == "manual_corrected"
    assert hip["x_px"] == 0.5
    assert hip["automatic_x_px"] == 0.0
    assert payload["frames"][0]["measurements"]["projected_knee_flexion"]["source_state"] == "manual_corrected"
    assert payload["frames"][0]["measurements"]["projected_shank_foot_angle"]["source_state"] == "automatic"


def test_export_refuses_overwrite(tmp_path):
    db_path, session_id = _build_session(tmp_path)
    export_dir = tmp_path / "export"
    with SessionDatabase(db_path) as connection:
        export_session_bundle(
            connection,
            session_id=session_id,
            output_dir=export_dir,
            include_overlay_mp4=False,
        )
        try:
            export_session_bundle(
                connection,
                session_id=session_id,
                output_dir=export_dir,
                include_overlay_mp4=False,
            )
        except FileExistsError:
            pass
        else:
            raise AssertionError("second export must refuse overwrite")


def test_failed_overlay_leaves_no_partial_bundle(tmp_path):
    db_path, session_id = _build_session(tmp_path)
    output = tmp_path / "failed"
    with SessionDatabase(db_path) as connection:
        with pytest.raises(FileNotFoundError):
            export_session_bundle(connection, session_id=session_id, output_dir=output)
    assert not output.exists()
    assert not list(tmp_path.glob(".export-*"))


def test_overlay_preserves_decoded_dimensions_and_frames(tmp_path):
    db_path, session_id = _build_session(tmp_path)
    writer = cv2.VideoWriter(str(tmp_path / "source.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 30, (640, 480))
    assert writer.isOpened()
    for _ in range(2):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
    writer.release()
    with SessionDatabase(db_path) as connection:
        outputs = export_session_bundle(connection, session_id=session_id, output_dir=tmp_path / "complete")
    capture = cv2.VideoCapture(str(outputs["overlay_mp4"]))
    frames = []
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frames.append(frame)
    finally:
        capture.release()
    assert len(frames) == 2
    assert all(frame.shape == (480, 640, 3) for frame in frames)
    assert frames[0][:105].max() > 100


@pytest.mark.parametrize("source_frames", [1, 3])
def test_source_frame_mismatch_does_not_publish_partial_export(tmp_path, source_frames):
    db_path, session_id = _build_session(tmp_path)
    writer = cv2.VideoWriter(str(tmp_path / "source.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 30, (640, 480))
    assert writer.isOpened()
    for _ in range(source_frames):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
    writer.release()
    output = tmp_path / "mismatch"
    with SessionDatabase(db_path) as connection:
        with pytest.raises(ValueError, match="source"):
            export_session_bundle(connection, session_id=session_id, output_dir=output)
    assert not output.exists()
    assert not list(tmp_path.glob(".export-*"))
