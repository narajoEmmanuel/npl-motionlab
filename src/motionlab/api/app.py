"""Local FastAPI service for NPL MotionLab Interactive.

I3 exposes a stable loopback-oriented application boundary over the existing
session, Sports2D-adapter and measurement layers. The UI should use this service
rather than read TRC/CSV files directly.
"""

from __future__ import annotations

import json
import math
import sqlite3
import uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from motionlab.measurements import DEFINITIONS, evaluate_measurement
from motionlab.sessions.database import (
    SessionDatabase,
    add_manual_correction,
    create_session,
    get_effective_landmark,
    initialize_frames,
    register_video,
    reset_manual_correction,
    store_automatic_landmark,
)
from motionlab.sports2d_adapter import (
    read_sports2d_pixel_trc,
    semantic_landmarks_from_sports2d,
)
from motionlab.video_metadata import inspect_video

API_VERSION = "v1"
SEMANTIC_ROLES = ("shoulder", "hip", "knee", "ankle", "toe")


class SessionCreateRequest(BaseModel):
    source_path: str
    selected_side: Literal["left", "right"] = "right"
    label: str | None = None


class AnalysisImportRequest(BaseModel):
    trc_path: str
    engine_provenance_path: str


class ManualCorrectionRequest(BaseModel):
    x_px: float
    y_px: float
    note: str | None = None


class AppContext:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.sessions_root = self.workspace_root / "sessions"

    def db_path(self, session_id: str) -> Path:
        if not session_id.startswith("session_") or any(
            character not in "0123456789abcdef" for character in session_id.removeprefix("session_")
        ):
            raise KeyError("invalid session id")
        if len(session_id.removeprefix("session_")) != 32:
            raise KeyError("invalid session id")
        return self.sessions_root / session_id / "session.db"


def _http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, (FileNotFoundError, KeyError)):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (ValueError, sqlite3.IntegrityError)):
        return HTTPException(status_code=422, detail=str(exc))
    return HTTPException(status_code=500, detail="MotionLab local service error")


def _require_db(context: AppContext, session_id: str) -> Path:
    try:
        path = context.db_path(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc
    if not path.is_file():
        raise HTTPException(status_code=404, detail="session not found")
    return path


def _session_snapshot(connection: sqlite3.Connection, session_id: str) -> dict[str, object]:
    session = connection.execute(
        "SELECT id, label, selected_side, status, created_at_utc FROM sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    if session is None:
        raise KeyError("session not found")
    video = connection.execute(
        """
        SELECT source_path, source_filename, sha256, decoded_width_px,
               decoded_height_px, fps, frame_count, duration_s
        FROM videos WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    counts = {
        "frames": connection.execute(
            "SELECT COUNT(*) AS n FROM frames WHERE session_id = ?", (session_id,)
        ).fetchone()["n"],
        "automatic_landmarks": connection.execute(
            """
            SELECT COUNT(*) AS n FROM automatic_landmarks a
            JOIN frames f ON f.id = a.frame_id WHERE f.session_id = ?
            """,
            (session_id,),
        ).fetchone()["n"],
        "active_manual_corrections": connection.execute(
            """
            SELECT COUNT(*) AS n FROM manual_corrections m
            JOIN frames f ON f.id = m.frame_id
            WHERE f.session_id = ? AND m.is_active = 1
            """,
            (session_id,),
        ).fetchone()["n"],
        "measurement_results": connection.execute(
            """
            SELECT COUNT(*) AS n FROM measurement_results r
            JOIN frames f ON f.id = r.frame_id WHERE f.session_id = ?
            """,
            (session_id,),
        ).fetchone()["n"],
    }
    return {
        "id": session["id"],
        "label": session["label"],
        "selected_side": session["selected_side"],
        "status": session["status"],
        "created_at_utc": session["created_at_utc"],
        "video": dict(video) if video is not None else None,
        "counts": counts,
    }


def _frame_snapshot(
    connection: sqlite3.Connection, session_id: str, frame_index: int
) -> dict[str, object]:
    frame = connection.execute(
        "SELECT id, frame_index, time_s FROM frames WHERE session_id = ? AND frame_index = ?",
        (session_id, frame_index),
    ).fetchone()
    if frame is None:
        raise KeyError(f"frame {frame_index} not found")

    landmarks: dict[str, dict[str, object] | None] = {}
    numeric_landmarks: dict[str, tuple[float, float]] = {}
    for role in SEMANTIC_ROLES:
        effective = get_effective_landmark(
            connection, session_id=session_id, frame_index=frame_index, role=role
        )
        if effective is None:
            landmarks[role] = None
            continue
        landmarks[role] = {
            "x_px": effective.x_px,
            "y_px": effective.y_px,
            "source_state": effective.source_state,
            "automatic_x_px": effective.automatic_x_px,
            "automatic_y_px": effective.automatic_y_px,
            "correction_id": effective.correction_id,
        }
        numeric_landmarks[role] = (effective.x_px, effective.y_px)

    measurements: dict[str, dict[str, object]] = {}
    for definition in DEFINITIONS.values():
        result = evaluate_measurement(definition.name, numeric_landmarks)
        source_state = "automatic"
        if any(
            landmarks.get(role) is not None
            and landmarks[role]["source_state"] == "manual_corrected"  # type: ignore[index]
            for role in definition.dependencies
        ):
            source_state = "manual_corrected"
        measurements[definition.name] = {
            "display_name": definition.display_name,
            "definition_version": definition.version,
            "unit": definition.unit,
            "value_deg": result.value_deg,
            "valid": result.valid,
            "invalid_reason": result.invalid_reason,
            "source_state": source_state,
        }

    return {
        "frame_index": int(frame["frame_index"]),
        "time_s": float(frame["time_s"]),
        "landmarks": landmarks,
        "measurements": measurements,
    }


def _validate_engine_provenance(
    record: dict[str, object], *, source_filename: str, source_sha256: str
) -> None:
    expected = {
        "contract_version": 1,
        "source_video_name": source_filename,
        "source_video_sha256": source_sha256,
        "sports2d_version": "0.8.34",
        "pose2sim_version": "0.10.49",
        "pose_model": "Body_with_feet",
        "pose_mode": "balanced",
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise ValueError(f"engine provenance mismatch: {key}")
    config = record.get("config_overrides")
    if not isinstance(config, dict):
        raise ValueError("engine provenance is missing config_overrides")
    required = {
        ("px_to_meters_conversion", "to_meters"): False,
        ("post-processing", "interpolate"): False,
        ("post-processing", "reject_outliers"): False,
        ("post-processing", "filter"): False,
    }
    for (section, key), value in required.items():
        section_value = config.get(section)
        if not isinstance(section_value, dict) or section_value.get(key) != value:
            raise ValueError(f"engine provenance mismatch: {section}.{key}")


def _import_analysis(
    connection: sqlite3.Connection,
    *,
    session_id: str,
    trc_path: Path,
    engine_provenance_path: Path,
) -> dict[str, int]:
    session = connection.execute(
        "SELECT selected_side, status FROM sessions WHERE id = ?", (session_id,)
    ).fetchone()
    video = connection.execute(
        "SELECT source_filename, sha256, frame_count FROM videos WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if session is None or video is None:
        raise KeyError("session not found")
    if connection.execute(
        """
        SELECT COUNT(*) AS n FROM automatic_landmarks a
        JOIN frames f ON f.id = a.frame_id WHERE f.session_id = ?
        """,
        (session_id,),
    ).fetchone()["n"]:
        raise ValueError("automatic analysis has already been imported for this session")

    provenance = json.loads(engine_provenance_path.read_text(encoding="utf-8"))
    if not isinstance(provenance, dict):
        raise ValueError("engine provenance must contain a JSON object")
    _validate_engine_provenance(
        provenance,
        source_filename=str(video["source_filename"]),
        source_sha256=str(video["sha256"]),
    )

    trc = read_sports2d_pixel_trc(trc_path)
    semantic = semantic_landmarks_from_sports2d(
        trc, side=str(session["selected_side"])
    )
    if len(semantic) != int(video["frame_count"]):
        raise ValueError("Sports2D/session frame count mismatch")

    landmark_count = 0
    measurement_count = 0
    for frame_index, row in enumerate(semantic.itertuples(index=False)):
        row_dict = row._asdict()
        landmarks: dict[str, tuple[float, float]] = {}
        for role in SEMANTIC_ROLES:
            x = float(row_dict[f"{role}_x_px"])
            y = float(row_dict[f"{role}_y_px"])
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            store_automatic_landmark(
                connection,
                session_id=session_id,
                frame_index=frame_index,
                role=role,
                x_px=x,
                y_px=y,
                source="sports2d-0.8.34/Body_with_feet",
            )
            landmarks[role] = (x, y)
            landmark_count += 1

        frame_id = connection.execute(
            "SELECT id FROM frames WHERE session_id = ? AND frame_index = ?",
            (session_id, frame_index),
        ).fetchone()["id"]
        for definition in DEFINITIONS.values():
            result = evaluate_measurement(definition.name, landmarks)
            connection.execute(
                """
                INSERT INTO measurement_results(
                    frame_id, measurement_name, value_deg, valid, invalid_reason,
                    source_state, definition_version, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, 'automatic', ?, datetime('now'))
                """,
                (
                    frame_id,
                    definition.name,
                    result.value_deg,
                    int(result.valid),
                    result.invalid_reason,
                    definition.version,
                ),
            )
            measurement_count += 1

    connection.execute(
        "UPDATE sessions SET status = 'analyzed' WHERE id = ?", (session_id,)
    )
    return {
        "frames": len(semantic),
        "automatic_landmarks": landmark_count,
        "measurement_results": measurement_count,
    }


def create_app(*, workspace_root: str | Path = "workspace") -> FastAPI:
    context = AppContext(Path(workspace_root))
    app = FastAPI(
        title="NPL MotionLab Interactive Local API",
        version="0.1",
        docs_url="/docs",
        redoc_url=None,
    )

    @app.get(f"/api/{API_VERSION}/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "motionlab-interactive", "api_version": API_VERSION}

    @app.get(f"/api/{API_VERSION}/measurements")
    def measurements() -> list[dict[str, object]]:
        return [
            {
                "name": definition.name,
                "display_name": definition.display_name,
                "version": definition.version,
                "unit": definition.unit,
                "dependencies": list(definition.dependencies),
            }
            for definition in DEFINITIONS.values()
        ]

    @app.post(f"/api/{API_VERSION}/sessions", status_code=201)
    def new_session(request: SessionCreateRequest) -> dict[str, object]:
        try:
            metadata = inspect_video(request.source_path)
            if metadata.frame_count_reported is None or metadata.nominal_fps_reported is None:
                raise ValueError(
                    "source must expose reported frame count and nominal FPS for I3 session indexing"
                )
            session_id = f"session_{uuid.uuid4().hex}"
            db_path = context.sessions_root / session_id / "session.db"
            with SessionDatabase(db_path) as connection:
                create_session(
                    connection,
                    selected_side=request.selected_side,
                    label=request.label,
                    session_id=session_id,
                )
                register_video(
                    connection,
                    session_id=session_id,
                    source_path=Path(request.source_path).resolve(),
                    sha256=metadata.sha256,
                    decoded_width_px=metadata.decoded_width_px,
                    decoded_height_px=metadata.decoded_height_px,
                    fps=metadata.nominal_fps_reported,
                    frame_count=metadata.frame_count_reported,
                    duration_s=metadata.duration_seconds_derived or 0.0,
                )
                initialize_frames(
                    connection,
                    session_id=session_id,
                    frame_count=metadata.frame_count_reported,
                    fps=metadata.nominal_fps_reported,
                )
                snapshot = _session_snapshot(connection, session_id)
            return snapshot
        except HTTPException:
            raise
        except Exception as exc:
            raise _http_error(exc) from exc

    @app.get(f"/api/{API_VERSION}/sessions/{{session_id}}")
    def get_session(session_id: str) -> dict[str, object]:
        db_path = _require_db(context, session_id)
        try:
            with SessionDatabase(db_path) as connection:
                return _session_snapshot(connection, session_id)
        except Exception as exc:
            raise _http_error(exc) from exc

    @app.post(f"/api/{API_VERSION}/sessions/{{session_id}}/analysis/import")
    def import_analysis(session_id: str, request: AnalysisImportRequest) -> dict[str, object]:
        db_path = _require_db(context, session_id)
        try:
            with SessionDatabase(db_path) as connection:
                imported = _import_analysis(
                    connection,
                    session_id=session_id,
                    trc_path=Path(request.trc_path),
                    engine_provenance_path=Path(request.engine_provenance_path),
                )
                return {"session_id": session_id, "status": "analyzed", "imported": imported}
        except Exception as exc:
            raise _http_error(exc) from exc

    @app.get(f"/api/{API_VERSION}/sessions/{{session_id}}/frames/{{frame_index}}")
    def get_frame(session_id: str, frame_index: int) -> dict[str, object]:
        db_path = _require_db(context, session_id)
        try:
            with SessionDatabase(db_path) as connection:
                return _frame_snapshot(connection, session_id, frame_index)
        except Exception as exc:
            raise _http_error(exc) from exc

    @app.post(
        f"/api/{API_VERSION}/sessions/{{session_id}}/frames/{{frame_index}}/landmarks/{{role}}/corrections"
    )
    def correct_landmark(
        session_id: str,
        frame_index: int,
        role: str,
        request: ManualCorrectionRequest,
    ) -> dict[str, object]:
        db_path = _require_db(context, session_id)
        try:
            with SessionDatabase(db_path) as connection:
                add_manual_correction(
                    connection,
                    session_id=session_id,
                    frame_index=frame_index,
                    role=role,
                    x_px=request.x_px,
                    y_px=request.y_px,
                    note=request.note,
                )
                return _frame_snapshot(connection, session_id, frame_index)
        except Exception as exc:
            raise _http_error(exc) from exc

    @app.delete(
        f"/api/{API_VERSION}/sessions/{{session_id}}/frames/{{frame_index}}/landmarks/{{role}}/correction"
    )
    def reset_correction(session_id: str, frame_index: int, role: str) -> dict[str, object]:
        db_path = _require_db(context, session_id)
        try:
            with SessionDatabase(db_path) as connection:
                reset_manual_correction(
                    connection,
                    session_id=session_id,
                    frame_index=frame_index,
                    role=role,
                )
                return _frame_snapshot(connection, session_id, frame_index)
        except Exception as exc:
            raise _http_error(exc) from exc

    return app


app = create_app()
