import sqlite3

import pytest

from motionlab.sessions import (
    SCHEMA_VERSION,
    SessionDatabase,
    add_manual_correction,
    create_session,
    get_effective_landmark,
    initialize_frames,
    register_video,
    reset_manual_correction,
    store_automatic_landmark,
)


def test_session_database_initializes_schema(tmp_path):
    db_path = tmp_path / "session.db"

    with SessionDatabase(db_path) as connection:
        version = connection.execute(
            "SELECT value FROM schema_meta WHERE key = 'schema_version'"
        ).fetchone()["value"]
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert db_path.exists()
    assert int(version) == SCHEMA_VERSION
    assert {
        "sessions",
        "videos",
        "frames",
        "automatic_landmarks",
        "manual_corrections",
        "measurement_results",
        "events",
        "artifacts",
        "provenance",
    }.issubset(tables)


def test_session_schema_initialization_is_idempotent(tmp_path):
    db_path = tmp_path / "session.db"

    with SessionDatabase(db_path):
        pass
    with SessionDatabase(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) AS n FROM schema_meta").fetchone()["n"] == 1


def test_create_session_validates_side(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        with pytest.raises(ValueError, match="selected_side"):
            create_session(connection, selected_side="center")


def test_register_video_stores_reference_not_binary(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right", label="T01")
        video_id = register_video(
            connection,
            session_id=session_id,
            source_path=tmp_path / "source" / "trial.mov",
            sha256="a" * 64,
            decoded_width_px=3840,
            decoded_height_px=2160,
            fps=30.0,
            frame_count=70,
            duration_s=70 / 30,
        )
        row = connection.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()

    assert row["source_filename"] == "trial.mov"
    assert row["source_path"].endswith("trial.mov")
    assert row["sha256"] == "a" * 64
    assert row["decoded_width_px"] == 3840
    assert row["decoded_height_px"] == 2160
    assert row["frame_count"] == 70


def test_register_video_rejects_bad_hash(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        with pytest.raises(ValueError, match="sha256"):
            register_video(
                connection,
                session_id=session_id,
                source_path="trial.mov",
                sha256="not-a-hash",
                decoded_width_px=1920,
                decoded_height_px=1080,
                fps=30,
                frame_count=10,
                duration_s=1,
            )


def test_initialize_frames_uses_zero_based_time_order(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        initialize_frames(connection, session_id=session_id, frame_count=3, fps=25.0)
        rows = connection.execute(
            "SELECT frame_index, time_s FROM frames WHERE session_id = ? ORDER BY frame_index",
            (session_id,),
        ).fetchall()

    assert [(row["frame_index"], row["time_s"]) for row in rows] == [
        (0, 0.0),
        (1, 0.04),
        (2, 0.08),
    ]


def test_frames_cannot_be_initialized_twice(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        initialize_frames(connection, session_id=session_id, frame_count=2, fps=30)
        with pytest.raises(ValueError, match="already initialized"):
            initialize_frames(connection, session_id=session_id, frame_count=2, fps=30)


def test_automatic_landmark_is_immutable(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        initialize_frames(connection, session_id=session_id, frame_count=1, fps=30)
        store_automatic_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="knee",
            x_px=100,
            y_px=200,
            confidence=0.9,
        )

        with pytest.raises(sqlite3.IntegrityError):
            store_automatic_landmark(
                connection,
                session_id=session_id,
                frame_index=0,
                role="knee",
                x_px=101,
                y_px=201,
                confidence=0.8,
            )


def test_manual_correction_takes_effect_without_overwriting_auto(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        initialize_frames(connection, session_id=session_id, frame_count=1, fps=30)
        store_automatic_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="knee",
            x_px=100,
            y_px=200,
        )
        correction_id = add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="knee",
            x_px=110,
            y_px=205,
        )
        effective = get_effective_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="knee",
        )
        automatic = connection.execute(
            "SELECT x_px, y_px FROM automatic_landmarks"
        ).fetchone()

    assert effective is not None
    assert effective.source_state == "manual_corrected"
    assert effective.x_px == 110
    assert effective.y_px == 205
    assert effective.automatic_x_px == 100
    assert effective.automatic_y_px == 200
    assert effective.correction_id == correction_id
    assert (automatic["x_px"], automatic["y_px"]) == (100, 200)


def test_new_manual_correction_preserves_history(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        initialize_frames(connection, session_id=session_id, frame_count=1, fps=30)
        store_automatic_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=50,
            y_px=60,
        )
        first = add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=52,
            y_px=61,
        )
        second = add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
            x_px=53,
            y_px=62,
        )
        rows = connection.execute(
            "SELECT id, is_active FROM manual_corrections ORDER BY id"
        ).fetchall()
        effective = get_effective_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="hip",
        )

    assert [(row["id"], row["is_active"]) for row in rows] == [(first, 0), (second, 1)]
    assert effective is not None
    assert effective.x_px == 53
    assert effective.y_px == 62
    assert effective.correction_id == second


def test_reset_manual_correction_restores_automatic_point(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="left")
        initialize_frames(connection, session_id=session_id, frame_count=1, fps=30)
        store_automatic_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="ankle",
            x_px=300,
            y_px=400,
        )
        add_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="ankle",
            x_px=305,
            y_px=402,
        )

        assert reset_manual_correction(
            connection,
            session_id=session_id,
            frame_index=0,
            role="ankle",
        )
        effective = get_effective_landmark(
            connection,
            session_id=session_id,
            frame_index=0,
            role="ankle",
        )
        history = connection.execute(
            "SELECT COUNT(*) AS n, SUM(is_active) AS active FROM manual_corrections"
        ).fetchone()

    assert effective is not None
    assert effective.source_state == "automatic"
    assert (effective.x_px, effective.y_px) == (300, 400)
    assert history["n"] == 1
    assert history["active"] == 0


def test_correction_requires_automatic_landmark(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        initialize_frames(connection, session_id=session_id, frame_count=1, fps=30)
        with pytest.raises(ValueError, match="no automatic source point"):
            add_manual_correction(
                connection,
                session_id=session_id,
                frame_index=0,
                role="toe",
                x_px=1,
                y_px=2,
            )


def test_effective_landmark_returns_none_when_auto_point_missing(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        session_id = create_session(connection, selected_side="right")
        initialize_frames(connection, session_id=session_id, frame_count=1, fps=30)
        assert (
            get_effective_landmark(
                connection,
                session_id=session_id,
                frame_index=0,
                role="shoulder",
            )
            is None
        )


def test_foreign_keys_are_enabled(tmp_path):
    with SessionDatabase(tmp_path / "session.db") as connection:
        enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        assert enabled == 1
        with pytest.raises(sqlite3.IntegrityError):
            register_video(
                connection,
                session_id="missing",
                source_path="trial.mov",
                sha256="b" * 64,
                decoded_width_px=1920,
                decoded_height_px=1080,
                fps=30,
                frame_count=10,
                duration_s=1,
            )
