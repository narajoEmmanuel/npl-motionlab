"""Review services for MotionLab Interactive.

Manual corrections never overwrite automatic landmark or automatic measurement
records. This module provides append/audit-compatible undo and a separate cache
for reviewed frame measurements derived from effective landmarks.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from motionlab.measurements import DEFINITIONS, definitions_for_landmark, evaluate_measurement
from motionlab.sessions.database import get_effective_landmark

REVIEW_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reviewed_measurement_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    measurement_name TEXT NOT NULL,
    value_deg REAL,
    valid INTEGER NOT NULL CHECK (valid IN (0, 1)),
    invalid_reason TEXT,
    definition_version TEXT NOT NULL,
    input_revision TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    UNIQUE (frame_id, measurement_name, definition_version)
);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_review_schema(connection: sqlite3.Connection) -> None:
    """Create additive post-I1 review storage without changing Core evidence."""
    connection.executescript(REVIEW_SCHEMA_SQL)


def _frame_id(connection: sqlite3.Connection, session_id: str, frame_index: int) -> int:
    row = connection.execute(
        "SELECT id FROM frames WHERE session_id = ? AND frame_index = ?",
        (session_id, frame_index),
    ).fetchone()
    if row is None:
        raise KeyError(f"frame {frame_index} does not exist in session {session_id}")
    return int(row["id"])


def effective_landmark_map(
    connection: sqlite3.Connection, *, session_id: str, frame_index: int
) -> dict[str, tuple[float, float]]:
    """Return finite effective semantic positions available for one frame."""
    values: dict[str, tuple[float, float]] = {}
    for role in ("shoulder", "hip", "knee", "ankle", "toe"):
        point = get_effective_landmark(
            connection, session_id=session_id, frame_index=frame_index, role=role
        )
        if point is not None:
            values[role] = (point.x_px, point.y_px)
    return values


def recalculate_reviewed_measurements(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    frame_index: int,
    changed_role: str,
) -> tuple[str, ...]:
    """Recalculate only definitions affected by one edited landmark.

    Results are stored separately from immutable automatic ``measurement_results``.
    ``input_revision`` records the active correction ids used by the frame so a
    cached reviewed value is traceable to effective landmark state.
    """
    ensure_review_schema(connection)
    frame_id = _frame_id(connection, session_id, frame_index)
    landmarks = effective_landmark_map(
        connection, session_id=session_id, frame_index=frame_index
    )
    active = connection.execute(
        """
        SELECT role, id FROM manual_corrections
        WHERE frame_id = ? AND is_active = 1 ORDER BY role
        """,
        (frame_id,),
    ).fetchall()
    revision = ";".join(f"{row['role']}:{row['id']}" for row in active) or "automatic"

    names: list[str] = []
    for definition in definitions_for_landmark(changed_role):
        result = evaluate_measurement(definition.name, landmarks)
        connection.execute(
            """
            INSERT INTO reviewed_measurement_results(
                frame_id, measurement_name, value_deg, valid, invalid_reason,
                definition_version, input_revision, created_at_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(frame_id, measurement_name, definition_version)
            DO UPDATE SET value_deg = excluded.value_deg,
                          valid = excluded.valid,
                          invalid_reason = excluded.invalid_reason,
                          input_revision = excluded.input_revision,
                          created_at_utc = excluded.created_at_utc
            """,
            (
                frame_id,
                definition.name,
                result.value_deg,
                int(result.valid),
                result.invalid_reason,
                definition.version,
                revision,
                _utc_now(),
            ),
        )
        names.append(definition.name)
    return tuple(names)


def undo_manual_correction(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    frame_index: int,
    role: str,
) -> bool:
    """Undo the latest active correction, restoring the prior correction if any."""
    frame_id = _frame_id(connection, session_id, frame_index)
    current = connection.execute(
        """
        SELECT id FROM manual_corrections
        WHERE frame_id = ? AND role = ? AND is_active = 1
        """,
        (frame_id, role),
    ).fetchone()
    if current is None:
        return False

    connection.execute(
        "UPDATE manual_corrections SET is_active = 0 WHERE id = ?",
        (int(current["id"]),),
    )
    previous = connection.execute(
        """
        SELECT id FROM manual_corrections
        WHERE frame_id = ? AND role = ? AND id < ?
        ORDER BY id DESC LIMIT 1
        """,
        (frame_id, role, int(current["id"])),
    ).fetchone()
    if previous is not None:
        connection.execute(
            "UPDATE manual_corrections SET is_active = 1 WHERE id = ?",
            (int(previous["id"]),),
        )
    return True
