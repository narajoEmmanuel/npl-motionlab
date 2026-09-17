import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from motionlab.api.app import create_app
from motionlab.sessions.database import (
    SessionDatabase,
    create_session,
    initialize_frames,
    register_video,
    store_automatic_landmark,
)
from motionlab.video_metadata import VideoMetadata


SHA = "a" * 64


def _fake_metadata(source: Path, *, frames: int = 2, fps: float = 30.0) -> VideoMetadata:
    return VideoMetadata(
        schema_version="motionlab.video-metadata.v1",
        source_filename=source.name,
        sha256=SHA,
        file_size_bytes=123,
        container_suffix=source.suffix,
        decoded_width_px=640,
        decoded_height_px=480,
        frame_count_reported=frames,
        nominal_fps_reported=fps,
        duration_seconds_derived=frames / fps,
        codec_fourcc="mp4v",
        capture_backend="synthetic",
        backend_orientation_degrees=0,
        orientation_note="synthetic",
        timing_note="synthetic",
    )


def _client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(workspace_root=tmp_path / "workspace"))


def _create_db(workspace: Path, session_id: str = "session_" + "1" * 32) -> Path:
    db = workspace / "sessions" / session_id / "session.db"
    with SessionDatabase(db) as connection:
        create_session(connection, selected_side="right", session_id=session_id, label="Synthetic")
        register_video(
            connection,
            session_id=session_id,
            source_path="synthetic.mp4",
            sha256=SHA,
            decoded_width_px=640,
            decoded_height_px=480,
            fps=30.0,
            frame_count=2,
            duration_s=2 / 30,
        )
        initialize_frames(connection, session_id=session_id, frame_count=2, fps=30.0)
    return db


def test_health_and_measurement_definitions(tmp_path):
    client = _client(tmp_path)
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    response = client.get("/api/v1/measurements")
    assert response.status_code == 200
    definitions = {item["name"]: item for item in response.json()}
    assert definitions["projected_knee_flexion"]["dependencies"] == ["hip", "knee", "ankle"]
    assert definitions["projected_shank_foot_angle"]["dependencies"] == ["knee", "ankle", "toe"]
    assert definitions["projected_trunk_inclination"]["dependencies"] == ["hip", "shoulder"]


def test_create_session_inspects_source_and_creates_private_db(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"not-real-video")
    monkeypatch.setattr("motionlab.api.app.inspect_video", lambda path: _fake_metadata(source))
    client = _client(tmp_path)

    response = client.post(
        "/api/v1/sessions",
        json={"source_path": str(source), "selected_side": "right", "label": "Trial A"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["selected_side"] == "right"
    assert body["video"]["source_filename"] == "source.mp4"
    assert body["counts"]["frames"] == 2
    assert (tmp_path / "workspace" / "sessions" / body["id"] / "session.db").is_file()


def test_missing_session_is_404(tmp_path):
    client = _client(tmp_path)
    response = client.get("/api/v1/sessions/session_" + "2" * 32)
    assert response.status_code == 404


def test_frame_snapshot_exposes_effective_landmarks_and_measurements(tmp_path):
    workspace = tmp_path / "workspace"
    session_id = "session_" + "1" * 32
    db = _create_db(workspace, session_id)
    with SessionDatabase(db) as connection:
        points = {
            "shoulder": (0.0, -2.0),
            "hip": (0.0, 0.0),
            "knee": (0.0, 1.0),
            "ankle": (0.0, 2.0),
            "toe": (1.0, 2.0),
        }
        for role, (x, y) in points.items():
            store_automatic_landmark(
                connection,
                session_id=session_id,
                frame_index=0,
                role=role,
                x_px=x,
                y_px=y,
            )

    client = _client(tmp_path)
    response = client.get(f"/api/v1/sessions/{session_id}/frames/0")
    assert response.status_code == 200
    body = response.json()
    assert body["landmarks"]["hip"]["source_state"] == "automatic"
    assert body["measurements"]["projected_knee_flexion"]["value_deg"] == pytest.approx(0.0)
    assert body["measurements"]["projected_shank_foot_angle"]["value_deg"] == pytest.approx(90.0)
    assert body["measurements"]["projected_trunk_inclination"]["value_deg"] == pytest.approx(0.0)


def test_manual_correction_and_reset_preserve_automatic_point(tmp_path):
    workspace = tmp_path / "workspace"
    session_id = "session_" + "1" * 32
    db = _create_db(workspace, session_id)
    with SessionDatabase(db) as connection:
        for role, point in {
            "shoulder": (0, -2), "hip": (0, 0), "knee": (0, 1), "ankle": (0, 2), "toe": (1, 2)
        }.items():
            store_automatic_landmark(
                connection, session_id=session_id, frame_index=0, role=role,
                x_px=point[0], y_px=point[1]
            )

    client = _client(tmp_path)
    corrected = client.post(
        f"/api/v1/sessions/{session_id}/frames/0/landmarks/hip/corrections",
        json={"x_px": 1.0, "y_px": 0.0, "note": "synthetic edit"},
    )
    assert corrected.status_code == 200
    hip = corrected.json()["landmarks"]["hip"]
    assert hip["source_state"] == "manual_corrected"
    assert hip["x_px"] == 1.0
    assert hip["automatic_x_px"] == 0.0

    reset = client.delete(
        f"/api/v1/sessions/{session_id}/frames/0/landmarks/hip/correction"
    )
    assert reset.status_code == 200
    hip = reset.json()["landmarks"]["hip"]
    assert hip["source_state"] == "automatic"
    assert hip["x_px"] == 0.0


def _write_trc(path: Path) -> None:
    markers = ["RShoulder", "RHip", "RKnee", "RAnkle", "RBigToe"]
    header = "Frame#\tTime\t" + "\t\t\t".join(markers)
    axes = "\t\t" + "\t".join(
        coordinate for _ in markers for coordinate in ("X", "Y", "Z")
    )
    rows = []
    frames = [
        [(0, -2), (0, 0), (0, 1), (0, 2), (1, 2)],
        [(0, -2), (0, 0), (1, 1), (1, 2), (2, 2)],
    ]
    for index, points in enumerate(frames):
        fields = [str(index), str(index / 30)]
        for x, y in points:
            fields.extend([str(x), str(y), "0"])
        rows.append("\t".join(fields))
    path.write_text("Synthetic TRC\n" + header + "\n" + axes + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_analysis_import_validates_provenance_and_populates_results(tmp_path):
    workspace = tmp_path / "workspace"
    session_id = "session_" + "1" * 32
    _create_db(workspace, session_id)
    trc = tmp_path / "synthetic_px_person00.trc"
    _write_trc(trc)
    provenance = tmp_path / "provenance.json"
    provenance.write_text(
        json.dumps(
            {
                "contract_version": 1,
                "source_video_name": "synthetic.mp4",
                "source_video_sha256": SHA,
                "sports2d_version": "0.8.34",
                "pose2sim_version": "0.10.49",
                "pose_model": "Body_with_feet",
                "pose_mode": "balanced",
                "config_overrides": {
                    "px_to_meters_conversion": {"to_meters": False},
                    "post-processing": {
                        "interpolate": False,
                        "reject_outliers": False,
                        "filter": False,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    client = _client(tmp_path)
    response = client.post(
        f"/api/v1/sessions/{session_id}/analysis/import",
        json={"trc_path": str(trc), "engine_provenance_path": str(provenance)},
    )
    assert response.status_code == 200
    imported = response.json()["imported"]
    assert imported == {"frames": 2, "automatic_landmarks": 10, "measurement_results": 6}

    session = client.get(f"/api/v1/sessions/{session_id}").json()
    assert session["status"] == "analyzed"
    assert session["counts"]["automatic_landmarks"] == 10
    assert session["counts"]["measurement_results"] == 6

    frame = client.get(f"/api/v1/sessions/{session_id}/frames/0").json()
    assert frame["landmarks"]["toe"]["x_px"] == 1.0
    assert frame["measurements"]["projected_trunk_inclination"]["valid"] is True


def test_analysis_import_rejects_wrong_source_identity(tmp_path):
    workspace = tmp_path / "workspace"
    session_id = "session_" + "1" * 32
    _create_db(workspace, session_id)
    trc = tmp_path / "synthetic_px_person00.trc"
    _write_trc(trc)
    provenance = tmp_path / "provenance.json"
    provenance.write_text(
        json.dumps(
            {
                "contract_version": 1,
                "source_video_name": "wrong.mp4",
                "source_video_sha256": SHA,
                "sports2d_version": "0.8.34",
                "pose2sim_version": "0.10.49",
                "pose_model": "Body_with_feet",
                "pose_mode": "balanced",
                "config_overrides": {
                    "px_to_meters_conversion": {"to_meters": False},
                    "post-processing": {"interpolate": False, "reject_outliers": False, "filter": False},
                },
            }
        ),
        encoding="utf-8",
    )
    client = _client(tmp_path)
    response = client.post(
        f"/api/v1/sessions/{session_id}/analysis/import",
        json={"trc_path": str(trc), "engine_provenance_path": str(provenance)},
    )
    assert response.status_code == 422
    assert "source_video_name" in response.json()["detail"]
