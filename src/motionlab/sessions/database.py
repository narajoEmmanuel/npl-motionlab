"""SQLite persistence for MotionLab Interactive sessions.

I1 establishes the local session data model only. It does not implement new
measurement formulas, the API layer, or the UI.
"""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

SCHEMA_VERSION = 1
LANDMARK_ROLES = frozenset({"shoulder", "hip", "knee", "ankle", "toe"})
SIDES = frozenset({"left", "right"})


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    label TEXT,
    selected_side TEXT NOT NULL CHECK (selected_side IN ('left', 'right')),
    status TEXT NOT NULL DEFAULT 'created',
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE REFERENCES sessions(id) ON DELETE CASCADE,
    source_path TEXT NOT NULL,
    source_filename TEXT NOT NULL,
    sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
    decoded_width_px INTEGER NOT NULL CHECK (decoded_width_px > 0),
    decoded_height_px INTEGER NOT NULL CHECK (decoded_height_px > 0),
    fps REAL NOT NULL CHECK (fps > 0),
    frame_count INTEGER NOT NULL CHECK (frame_count > 0),
    duration_s REAL NOT NULL CHECK (duration_s >= 0),
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    frame_index INTEGER NOT NULL CHECK (frame_index >= 0),
    time_s REAL NOT NULL CHECK (time_s >= 0),
    UNIQUE (session_id, frame_index)
);

CREATE TABLE IF NOT EXISTS automatic_landmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('shoulder', 'hip', 'knee', 'ankle', 'toe')),
    x_px REAL NOT NULL,
    y_px REAL NOT NULL,
    confidence REAL,
    source TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE (frame_id, role)
);

CREATE TABLE IF NOT EXISTS manual_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('shoulder', 'hip', 'knee', 'ankle', 'toe')),
    x_px REAL NOT NULL,
    y_px REAL NOT NULL,
    note TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at_utc TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_manual_correction
ON manual_corrections(frame_id, role)
WHERE is_active = 1;

CREATE TABLE IF NOT EXISTS measurement_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    measurement_name TEXT NOT NULL,
    value_deg REAL,
    valid INTEGER NOT NULL CHECK (valid IN (0, 1)),
    invalid_reason TEXT,
    source_state TEXT NOT NULL CHECK (source_state IN ('automatic', 'manual_corrected')),
    definition_version TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE (frame_id, measurement_name, definition_version)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    event_name TEXT NOT NULL,
    frame_id INTEGER REFERENCES frames(id) ON DELETE SET NULL,
    payload_json TEXT,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    sha256 TEXT,
    created_at_utc TEXT NOT NULL,
    UNIQUE (session_id, relative_path)
);

CREATE TABLE IF NOT EXISTS provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE (session_id, key)
);
"""


@dataclass(frozen=True)
class EffectiveLandmark:
    frame_index: int
    role: str
    x_px: float
    y_px: float
    source_state: Literal["automatic", "manual_corrected"]
    automatic_x_px: float
    automatic_y_px: float
    correction_id: int | None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _validate_side(side: str) -> None:
    if side not in SIDES:
        raise ValueError(f"selected_side must be one of {sorted(SIDES)}")


def _validate_role(role: str) -> None:
    if role not in LANDMARK_ROLES:
        raise ValueError(f"role must be one of {sorted(LANDMARK_ROLES)}")


class SessionDatabase:
    """Context manager for one local MotionLab `session.db` file."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.connection: sqlite3.Connection | None = None

    def __enter__(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_SQL)
        connection.execute(
            "INSERT OR IGNORE INTO schema_meta(key, value) VALUES ('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        existing = connection.execute(
            "SELECT value FROM schema_meta WHERE key = 'schema_version'"
        ).fetchone()
        if existing is None or int(existing["value"]) != SCHEMA_VERSION:
            connection.close()
            raise RuntimeError("Unsupported MotionLab session schema version.")
        connection.commit()
        self.connection = connection
        return connection

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.connection is None:
            return
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.close()
        self.connection = None


def create_session(
    connection: sqlite3.Connection,
    *,
    selected_side: str,
    label: str | None = None,
    session_id: str | None = None,
) -> str:
    """Create one session record and return its stable identifier."""

    _validate_side(selected_side)
    session_id = session_id or _new_id("session")
    connection.execute(
        """
        INSERT INTO sessions(id, label, selected_side, status, created_at_utc)
        VALUES (?, ?, ?, 'created', ?)
        """,
        (session_id, label, selected_side, _utc_now()),
    )
    return session_id


def register_video(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    source_path: str | Path,
    sha256: str,
    decoded_width_px: int,
    decoded_height_px: int,
    fps: float,
    frame_count: int,
    duration_s: float,
) -> str:
    """Register source-video identity and decoded metadata for one session.

    I1 stores a path/reference plus identity metadata. It intentionally does not
    copy or embed the source video.
    """

    if len(sha256) != 64:
        raise ValueError("sha256 must be a 64-character hexadecimal digest string")
    try:
        int(sha256, 16)
    except ValueError as exc:
        raise ValueError("sha256 must contain only hexadecimal characters") from exc
    if decoded_width_px <= 0 or decoded_height_px <= 0:
        raise ValueError("decoded dimensions must be positive")
    if fps <= 0 or frame_count <= 0 or duration_s < 0:
        raise ValueError("fps/frame_count must be positive and duration_s non-negative")

    path = Path(source_path)
    video_id = _new_id("video")
    connection.execute(
        """
        INSERT INTO videos(
            id, session_id, source_path, source_filename, sha256,
            decoded_width_px, decoded_height_px, fps, frame_count, duration_s,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            video_id,
            session_id,
            str(path),
            path.name,
            sha256.lower(),
            decoded_width_px,
            decoded_height_px,
            fps,
            frame_count,
            duration_s,
            _utc_now(),
        ),
    )
    return video_id


def initialize_frames(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    frame_count: int,
    fps: float,
) -> None:
    """Create deterministic zero-based frame rows for a session exactly once."""

    if frame_count <= 0 or fps <= 0:
        raise ValueError("frame_count and fps must be positive")
    existing = connection.execute(
        "SELECT COUNT(*) AS n FROM frames WHERE session_id = ?", (session_id,)
    ).fetchone()["n"]
    if existing:
        raise ValueError("frames are already initialized for this session")
    connection.executemany(
        "INSERT INTO frames(session_id, frame_index, time_s) VALUES (?, ?, ?)",
        ((session_id, index, index / fps) for index in range(frame_count)),
    )


def _frame_id(connection: sqlite3.Connection, session_id: str, frame_index: int) -> int:
    row = connection.execute(
        "SELECT id FROM frames WHERE session_id = ? AND frame_index = ?",
        (session_id, frame_index),
    ).fetchone()
    if row is None:
        raise KeyError(f"frame {frame_index} does not exist in session {session_id}")
    return int(row["id"])


def store_automatic_landmark(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    frame_index: int,
    role: str,
    x_px: float,
    y_px: float,
    confidence: float | None = None,
    source: str = "sports2d",
) -> int:
    """Store immutable automatic landmark evidence.

    Re-inserting the same semantic role for the same frame is rejected by the
    database rather than silently overwriting the original automatic point.
    """

    _validate_role(role)
    frame_id = _frame_id(connection, session_id, frame_index)
    cursor = connection.execute(
        """
        INSERT INTO automatic_landmarks(
            frame_id, role, x_px, y_px, confidence, source, created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (frame_id, role, float(x_px), float(y_px), confidence, source, _utc_now()),
    )
    return int(cursor.lastrowid)


def add_manual_correction(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    frame_index: int,
    role: str,
    x_px: float,
    y_px: float,
    note: str | None = None,
) -> int:
    """Append a correction while retaining complete previous correction history."""

    _validate_role(role)
    frame_id = _frame_id(connection, session_id, frame_index)
    automatic = connection.execute(
        "SELECT id FROM automatic_landmarks WHERE frame_id = ? AND role = ?",
        (frame_id, role),
    ).fetchone()
    if automatic is None:
        raise ValueError("cannot correct a landmark that has no automatic source point")

    connection.execute(
        "UPDATE manual_corrections SET is_active = 0 WHERE frame_id = ? AND role = ? AND is_active = 1",
        (frame_id, role),
    )
    cursor = connection.execute(
        """
        INSERT INTO manual_corrections(
            frame_id, role, x_px, y_px, note, is_active, created_at_utc
        ) VALUES (?, ?, ?, ?, ?, 1, ?)
        """,
        (frame_id, role, float(x_px), float(y_px), note, _utc_now()),
    )
    return int(cursor.lastrowid)


def reset_manual_correction(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    frame_index: int,
    role: str,
) -> bool:
    """Deactivate the current correction and fall back to the automatic point."""

    _validate_role(role)
    frame_id = _frame_id(connection, session_id, frame_index)
    cursor = connection.execute(
        "UPDATE manual_corrections SET is_active = 0 WHERE frame_id = ? AND role = ? AND is_active = 1",
        (frame_id, role),
    )
    return cursor.rowcount > 0


def get_effective_landmark(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    frame_index: int,
    role: str,
) -> EffectiveLandmark | None:
    """Return manual position when active, otherwise the immutable automatic point."""

    _validate_role(role)
    frame_id = _frame_id(connection, session_id, frame_index)
    automatic = connection.execute(
        """
        SELECT x_px, y_px
        FROM automatic_landmarks
        WHERE frame_id = ? AND role = ?
        """,
        (frame_id, role),
    ).fetchone()
    if automatic is None:
        return None

    manual = connection.execute(
        """
        SELECT id, x_px, y_px
        FROM manual_corrections
        WHERE frame_id = ? AND role = ? AND is_active = 1
        """,
        (frame_id, role),
    ).fetchone()

    if manual is None:
        return EffectiveLandmark(
            frame_index=frame_index,
            role=role,
            x_px=float(automatic["x_px"]),
            y_px=float(automatic["y_px"]),
            source_state="automatic",
            automatic_x_px=float(automatic["x_px"]),
            automatic_y_px=float(automatic["y_px"]),
            correction_id=None,
        )

    return EffectiveLandmark(
        frame_index=frame_index,
        role=role,
        x_px=float(manual["x_px"]),
        y_px=float(manual["y_px"]),
        source_state="manual_corrected",
        automatic_x_px=float(automatic["x_px"]),
        automatic_y_px=float(automatic["y_px"]),
        correction_id=int(manual["id"]),
    )
