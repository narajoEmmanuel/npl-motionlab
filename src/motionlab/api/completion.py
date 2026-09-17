"""Completion routes for MotionLab Interactive v0.2.

Kept separate from the I3 module so results/export functionality can be validated
without changing the established Core/service contracts.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from motionlab.session_export import export_session_bundle
from motionlab.sessions.database import SessionDatabase


class ExportRequest(BaseModel):
    include_overlay_mp4: bool = True


def register_completion_routes(
    app: FastAPI,
    *,
    context: Any,
    frame_snapshot: Callable[[sqlite3.Connection, str, int], dict[str, object]],
    api_version: str = "v1",
) -> None:
    """Register bulk-results and local export endpoints on an existing app."""

    def require_db(session_id: str) -> Path:
        try:
            path = context.db_path(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="session not found") from exc
        if not path.is_file():
            raise HTTPException(status_code=404, detail="session not found")
        return path

    @app.get(f"/api/{api_version}/sessions/{{session_id}}/frames")
    def get_session_frames(session_id: str) -> list[dict[str, object]]:
        db_path = require_db(session_id)
        try:
            with SessionDatabase(db_path) as connection:
                indices = connection.execute(
                    "SELECT frame_index FROM frames WHERE session_id = ? ORDER BY frame_index",
                    (session_id,),
                ).fetchall()
                return [
                    frame_snapshot(connection, session_id, int(row["frame_index"]))
                    for row in indices
                ]
        except (KeyError, ValueError, sqlite3.IntegrityError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post(f"/api/{api_version}/sessions/{{session_id}}/exports", status_code=201)
    def export_session(session_id: str, request: ExportRequest) -> dict[str, object]:
        db_path = require_db(session_id)
        export_root = context.sessions_root / session_id / "exports"
        next_index = 1
        while (export_root / f"export_{next_index:03d}").exists():
            next_index += 1
        destination = export_root / f"export_{next_index:03d}"
        try:
            with SessionDatabase(db_path) as connection:
                outputs = export_session_bundle(
                    connection,
                    session_id=session_id,
                    output_dir=destination,
                    include_overlay_mp4=request.include_overlay_mp4,
                )
                for artifact_type, path in outputs.items():
                    relative = path.relative_to(context.workspace_root)
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO artifacts(
                            session_id, artifact_type, relative_path, sha256, created_at_utc
                        ) VALUES (?, ?, ?, NULL, datetime('now'))
                        """,
                        (session_id, artifact_type, str(relative)),
                    )
            return {
                "session_id": session_id,
                "export_dir": str(destination),
                "artifacts": {name: str(path) for name, path in outputs.items()},
            }
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (ValueError, sqlite3.IntegrityError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
