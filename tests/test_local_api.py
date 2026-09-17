import importlib
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
from motionlab.review import recalculate_reviewed_measurements
from motionlab.measurements import DEFINITIONS, evaluate_measurement


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
    monkeypatch.setattr(importlib.import_module("motionlab.api.app"),
                        "inspect_video", lambda path: _fake_metadata(source))
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


@pytest.fixture
def review_session(tmp_path):
    session_id = "session_" + "1" * 32
    db = _create_db(tmp_path / "workspace", session_id)
    points = {"shoulder": (0, -2), "hip": (0, 0), "knee": (0, 1),
              "ankle": (0, 2), "toe": (1, 2)}
    client = _client(tmp_path)
    with SessionDatabase(db) as connection:
        for frame_index in (0, 1):
            for role, (x, y) in points.items():
                store_automatic_landmark(connection, session_id=session_id,
                                         frame_index=frame_index, role=role, x_px=x, y_px=y)
            frame_id = connection.execute("SELECT id FROM frames WHERE frame_index=?", (frame_index,)).fetchone()["id"]
            for name in DEFINITIONS:
                measurement = evaluate_measurement(name, points)
                connection.execute("""INSERT INTO measurement_results(
                    frame_id, measurement_name, value_deg, valid, invalid_reason,
                    source_state, definition_version, created_at_utc)
                    VALUES (?, ?, ?, 1, NULL, 'automatic', '1', 'synthetic')""",
                    (frame_id, name, measurement.value_deg))
            for role in points:
                recalculate_reviewed_measurements(connection, session_id=session_id,
                                                   frame_index=frame_index, changed_role=role)
    return client, db, f"/api/v1/sessions/{session_id}/frames/0/landmarks", points


def _evidence(db):
    with SessionDatabase(db) as connection:
        return {table: [dict(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY id")]
                for table in ("automatic_landmarks", "measurement_results", "manual_corrections", "reviewed_measurement_results")}


@pytest.mark.parametrize("role,affected", [
    ("shoulder", {"projected_trunk_inclination"}),
    ("hip", {"projected_knee_flexion", "projected_trunk_inclination"}),
    ("knee", {"projected_knee_flexion", "projected_shank_foot_angle"}),
    ("ankle", {"projected_knee_flexion", "projected_shank_foot_angle"}),
    ("toe", {"projected_shank_foot_angle"}),
])
def test_review_api_updates_only_dependent_rows_on_current_frame(review_session, role, affected):
    client, db, url, points = review_session
    before = _evidence(db)
    x, y = points[role]
    response = client.post(f"{url}/{role}/corrections", json={"x_px": x + 0.5, "y_px": y + 0.25})
    assert response.status_code == 200
    frame = response.json()
    landmark = frame["landmarks"][role]
    assert (landmark["x_px"], landmark["y_px"]) == (x + 0.5, y + 0.25)
    assert (landmark["automatic_x_px"], landmark["automatic_y_px"]) == (x, y)
    after = _evidence(db)
    assert after["automatic_landmarks"] == before["automatic_landmarks"]
    assert after["measurement_results"] == before["measurement_results"]
    frame_id = before["automatic_landmarks"][0]["frame_id"]
    for old, new in zip(before["reviewed_measurement_results"], after["reviewed_measurement_results"]):
        if old["frame_id"] == frame_id and old["measurement_name"] in affected:
            assert new["input_revision"] != old["input_revision"]
            assert new["value_deg"] == pytest.approx(frame["measurements"][new["measurement_name"]]["value_deg"])
        else:
            assert new == old
    reset = client.delete(f"{url}/{role}/correction")
    assert reset.status_code == 200
    assert (reset.json()["landmarks"][role]["x_px"], reset.json()["landmarks"][role]["y_px"]) == (x, y)
    restored = _evidence(db)
    assert restored["measurement_results"] == before["measurement_results"]
    for old, new in zip(before["reviewed_measurement_results"], restored["reviewed_measurement_results"]):
        if old["frame_id"] == frame_id and old["measurement_name"] in affected:
            assert new["input_revision"] == "automatic"
            assert new["value_deg"] == pytest.approx(old["value_deg"])
        else:
            assert new == old


def test_review_api_history_undo_returns_previous_then_automatic(review_session):
    client, db, url, _ = review_session
    before = _evidence(db)
    for x in (0.5, 1):
        assert client.post(f"{url}/hip/corrections", json={"x_px": x, "y_px": 0}).status_code == 200
    assert len(_evidence(db)["manual_corrections"]) == 2
    for expected, state in ((0.5, "manual_corrected"), (0, "automatic")):
        response = client.post(f"{url}/hip/undo")
        assert response.status_code == 200
        frame = response.json()
        assert frame["landmarks"]["hip"]["x_px"] == expected
        assert frame["landmarks"]["hip"]["source_state"] == state
        assert frame["landmarks"]["hip"]["automatic_x_px"] == 0
        evidence = _evidence(db)
        for row in evidence["reviewed_measurement_results"][:3]:
            assert row["value_deg"] == pytest.approx(frame["measurements"][row["measurement_name"]]["value_deg"])
    assert evidence["automatic_landmarks"] == before["automatic_landmarks"]
    assert evidence["measurement_results"] == before["measurement_results"]
    assert evidence["reviewed_measurement_results"][3:] == before["reviewed_measurement_results"][3:]


@pytest.mark.parametrize("operation", ["correction", "reset", "undo"])
def test_review_api_rejects_invalid_role(review_session, operation):
    client, db, url, _ = review_session
    before = _evidence(db)
    if operation == "correction":
        response = client.post(f"{url}/invalid/corrections", json={"x_px": 1, "y_px": 1})
    elif operation == "reset":
        response = client.delete(f"{url}/invalid/correction")
    else:
        response = client.post(f"{url}/invalid/undo")
    assert response.status_code == 422
    assert _evidence(db) == before


@pytest.mark.parametrize("operation", ["correction", "reset", "undo"])
def test_review_api_rolls_back_correction_and_review_writes_together(review_session, monkeypatch, operation):
    client, db, url, _ = review_session
    if operation != "correction":
        assert client.post(f"{url}/hip/corrections", json={"x_px": 1, "y_px": 0}).status_code == 200
    before = _evidence(db)
    def fail_after_writes(connection, **kwargs):
        recalculate_reviewed_measurements(connection, **kwargs)
        raise ValueError("synthetic failure after reviewed writes")
    monkeypatch.setattr(importlib.import_module("motionlab.api.app"), "recalculate_reviewed_measurements", fail_after_writes)
    if operation == "correction":
        response = client.post(f"{url}/hip/corrections", json={"x_px": 2, "y_px": 0})
    elif operation == "reset":
        response = client.delete(f"{url}/hip/correction")
    else:
        response = client.post(f"{url}/hip/undo")
    assert response.status_code == 422
    assert _evidence(db) == before
