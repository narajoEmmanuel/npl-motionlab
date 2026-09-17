from pathlib import Path

from fastapi.testclient import TestClient

from motionlab.api.app import AppContext, _frame_snapshot, create_app
from motionlab.api.completion import register_completion_routes
from motionlab.sessions.database import (
    SessionDatabase,
    create_session,
    initialize_frames,
    register_video,
    store_automatic_landmark,
)


def _client(tmp_path: Path):
    workspace = tmp_path / "workspace"
    app = create_app(workspace_root=workspace)
    register_completion_routes(
        app,
        context=AppContext(workspace),
        frame_snapshot=_frame_snapshot,
    )
    return TestClient(app), workspace


def _seed(workspace: Path):
    session_id = "session_" + "c" * 32
    db = workspace / "sessions" / session_id / "session.db"
    with SessionDatabase(db) as connection:
        create_session(connection, selected_side="right", session_id=session_id, label="Completion")
        register_video(
            connection,
            session_id=session_id,
            source_path=workspace / "source.mp4",
            sha256="a" * 64,
            decoded_width_px=640,
            decoded_height_px=480,
            fps=30.0,
            frame_count=2,
            duration_s=2 / 30,
        )
        initialize_frames(connection, session_id=session_id, frame_count=2, fps=30.0)
        for frame in (0, 1):
            for role, point in {
                "shoulder": (0, -2),
                "hip": (0, 0),
                "knee": (0, 1),
                "ankle": (0, 2),
                "toe": (1, 2),
            }.items():
                store_automatic_landmark(
                    connection,
                    session_id=session_id,
                    frame_index=frame,
                    role=role,
                    x_px=point[0] + frame,
                    y_px=point[1],
                )
        connection.execute("UPDATE sessions SET status = 'analyzed' WHERE id = ?", (session_id,))
    return session_id


def test_bulk_frames_returns_ordered_effective_results(tmp_path):
    client, workspace = _client(tmp_path)
    session_id = _seed(workspace)
    response = client.get(f"/api/v1/sessions/{session_id}/frames")
    assert response.status_code == 200
    rows = response.json()
    assert [row["frame_index"] for row in rows] == [0, 1]
    assert rows[0]["measurements"]["projected_knee_flexion"]["valid"] is True


def test_export_endpoint_creates_local_artifacts_without_overlay(tmp_path):
    client, workspace = _client(tmp_path)
    session_id = _seed(workspace)
    response = client.post(
        f"/api/v1/sessions/{session_id}/exports",
        json={"include_overlay_mp4": False},
    )
    assert response.status_code == 201
    body = response.json()
    assert set(body["artifacts"]) == {
        "measurements_csv",
        "landmarks_csv",
        "session_json",
        "figure_png",
    }
    assert all(Path(path).is_file() for path in body["artifacts"].values())

    db = workspace / "sessions" / session_id / "session.db"
    with SessionDatabase(db) as connection:
        count = connection.execute(
            "SELECT COUNT(*) AS n FROM artifacts WHERE session_id = ?", (session_id,)
        ).fetchone()["n"]
    assert count == 4
