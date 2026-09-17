import sqlite3

import pytest

from motionlab.review import (
    ensure_review_schema,
    recalculate_reviewed_measurements,
    undo_manual_correction,
)
from motionlab.sessions.database import (
    SessionDatabase,
    add_manual_correction,
    create_session,
    get_effective_landmark,
    initialize_frames,
    register_video,
    store_automatic_landmark,
)


def _session(tmp_path):
    session_id = "session_" + "a" * 32
    db = tmp_path / "session.db"
    with SessionDatabase(db) as connection:
        create_session(connection, selected_side="right", session_id=session_id)
        register_video(
            connection,
            session_id=session_id,
            source_path="synthetic.mp4",
            sha256="b" * 64,
            decoded_width_px=640,
            decoded_height_px=480,
            fps=30.0,
            frame_count=1,
            duration_s=1 / 30,
        )
        initialize_frames(connection, session_id=session_id, frame_count=1, fps=30.0)
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
                frame_index=0,
                role=role,
                x_px=point[0],
                y_px=point[1],
            )
    return db, session_id


def test_review_schema_is_additive(tmp_path):
    db, _ = _session(tmp_path)
    with SessionDatabase(db) as connection:
        ensure_review_schema(connection)
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='reviewed_measurement_results'"
        ).fetchone()
        assert table is not None


def test_recalculate_only_measurements_affected_by_landmark(tmp_path):
    db, session_id = _session(tmp_path)
    with SessionDatabase(db) as connection:
        add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=1,
            y_px=0,
        )
        names = recalculate_reviewed_measurements(
            connection,
            session_id=session_id,
            frame_index=0,
            changed_role="hip",
        )
        assert set(names) == {"projected_knee_flexion", "projected_trunk_inclination"}
        rows = connection.execute(
            "SELECT measurement_name, input_revision FROM reviewed_measurement_results ORDER BY measurement_name"
        ).fetchall()
        assert {row["measurement_name"] for row in rows} == set(names)
        assert all("hip:" in row["input_revision"] for row in rows)


def test_reviewed_results_do_not_overwrite_automatic_measurements(tmp_path):
    db, session_id = _session(tmp_path)
    with SessionDatabase(db) as connection:
        frame_id = connection.execute(
            "SELECT id FROM frames WHERE session_id = ? AND frame_index = 0", (session_id,)
        ).fetchone()["id"]
        connection.execute(
            """
            INSERT INTO measurement_results(
                frame_id, measurement_name, value_deg, valid, invalid_reason,
                source_state, definition_version, created_at_utc
            ) VALUES (?, 'projected_knee_flexion', 0, 1, NULL, 'automatic', '1', datetime('now'))
            """,
            (frame_id,),
        )
        add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=1,
            y_px=0,
        )
        recalculate_reviewed_measurements(
            connection,
            session_id=session_id,
            frame_index=0,
            changed_role="hip",
        )
        automatic = connection.execute(
            "SELECT value_deg, source_state FROM measurement_results WHERE measurement_name='projected_knee_flexion'"
        ).fetchone()
        assert automatic["value_deg"] == pytest.approx(0.0)
        assert automatic["source_state"] == "automatic"


def test_undo_restores_previous_manual_correction(tmp_path):
    db, session_id = _session(tmp_path)
    with SessionDatabase(db) as connection:
        first = add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=1,
            y_px=0,
        )
        second = add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=2,
            y_px=0,
        )
        assert second > first
        assert undo_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
        )
        point = get_effective_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
        )
        assert point is not None
        assert point.x_px == pytest.approx(1.0)
        assert point.correction_id == first


def test_undo_without_active_correction_is_false(tmp_path):
    db, session_id = _session(tmp_path)
    with SessionDatabase(db) as connection:
        assert not undo_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
        )
