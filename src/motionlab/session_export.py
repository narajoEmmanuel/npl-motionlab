"""Session-linked exports for MotionLab Interactive.

Exports are derived artifacts. They never become the database of record and they
never overwrite automatic landmark/measurement evidence.
"""

from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path

import cv2
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from motionlab.measurements import DEFINITIONS, evaluate_measurement
from motionlab.sessions.database import get_effective_landmark

SEMANTIC_ROLES = ("shoulder", "hip", "knee", "ankle", "toe")
SEGMENTS = (("shoulder", "hip"), ("hip", "knee"), ("knee", "ankle"), ("ankle", "toe"))


def _session_video(connection, session_id: str):
    row = connection.execute(
        """
        SELECT source_path, source_filename, sha256, decoded_width_px,
               decoded_height_px, fps, frame_count, duration_s
        FROM videos WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    if row is None:
        raise KeyError("session video not found")
    return row


def _frame_indices(connection, session_id: str) -> list[tuple[int, float]]:
    rows = connection.execute(
        "SELECT frame_index, time_s FROM frames WHERE session_id = ? ORDER BY frame_index",
        (session_id,),
    ).fetchall()
    return [(int(row["frame_index"]), float(row["time_s"])) for row in rows]


def _effective_frame(connection, session_id: str, frame_index: int):
    landmarks: dict[str, tuple[float, float]] = {}
    states: dict[str, str] = {}
    automatic: dict[str, tuple[float, float] | None] = {}
    for role in SEMANTIC_ROLES:
        point = get_effective_landmark(
            connection,
            session_id=session_id,
            frame_index=frame_index,
            role=role,
        )
        if point is None:
            automatic[role] = None
            continue
        landmarks[role] = (point.x_px, point.y_px)
        states[role] = point.source_state
        automatic[role] = (point.automatic_x_px, point.automatic_y_px)

    measurements = {}
    for definition in DEFINITIONS.values():
        result = evaluate_measurement(definition.name, landmarks)
        measurements[definition.name] = {
            "value_deg": result.value_deg,
            "valid": result.valid,
            "invalid_reason": result.invalid_reason,
            "definition_version": definition.version,
            "source_state": (
                "manual_corrected"
                if any(states.get(role) == "manual_corrected" for role in definition.dependencies)
                else "automatic"
            ),
        }
    return landmarks, states, automatic, measurements


def _write_session_bundle(
    connection,
    *,
    session_id: str,
    output_dir: str | Path,
    include_overlay_mp4: bool = True,
) -> dict[str, Path]:
    """Export reviewed/effective session state to CSV/JSON/PNG and optional MP4."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    video = _session_video(connection, session_id)
    frames = _frame_indices(connection, session_id)
    if not frames:
        raise ValueError("session contains no frames")

    measurements_csv = output / "measurements.csv"
    landmarks_csv = output / "landmarks.csv"
    session_json = output / "session.json"
    figure_png = output / "measurements.png"
    overlay_mp4 = output / "reviewed_overlay.mp4"

    if any(path.exists() for path in (measurements_csv, landmarks_csv, session_json, figure_png)):
        raise FileExistsError("export output already exists; choose a new output directory")
    if include_overlay_mp4 and overlay_mp4.exists():
        raise FileExistsError("export overlay already exists; choose a new output directory")

    measurement_rows: list[dict[str, object]] = []
    landmark_rows: list[dict[str, object]] = []
    json_frames: list[dict[str, object]] = []

    for frame_index, time_s in frames:
        landmarks, states, automatic, measurements = _effective_frame(
            connection, session_id, frame_index
        )
        measurement_rows.append(
            {
                "frame_index": frame_index,
                "time_s": time_s,
                **{
                    f"{name}_deg": payload["value_deg"]
                    for name, payload in measurements.items()
                },
                **{
                    f"{name}_valid": payload["valid"]
                    for name, payload in measurements.items()
                },
            }
        )
        for role in SEMANTIC_ROLES:
            effective = landmarks.get(role)
            auto = automatic.get(role)
            landmark_rows.append(
                {
                    "frame_index": frame_index,
                    "time_s": time_s,
                    "role": role,
                    "effective_x_px": None if effective is None else effective[0],
                    "effective_y_px": None if effective is None else effective[1],
                    "automatic_x_px": None if auto is None else auto[0],
                    "automatic_y_px": None if auto is None else auto[1],
                    "source_state": states.get(role, "missing"),
                }
            )
        json_frames.append(
            {
                "frame_index": frame_index,
                "time_s": time_s,
                "landmarks": {
                    role: (
                        None
                        if role not in landmarks
                        else {
                            "x_px": landmarks[role][0],
                            "y_px": landmarks[role][1],
                            "source_state": states[role],
                            "automatic_x_px": automatic[role][0] if automatic[role] else None,
                            "automatic_y_px": automatic[role][1] if automatic[role] else None,
                        }
                    )
                    for role in SEMANTIC_ROLES
                },
                "measurements": measurements,
            }
        )

    with measurements_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(measurement_rows[0]))
        writer.writeheader()
        writer.writerows(measurement_rows)

    with landmarks_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(landmark_rows[0]))
        writer.writeheader()
        writer.writerows(landmark_rows)

    session_payload = {
        "schema_version": "motionlab.interactive-export.v1",
        "session_id": session_id,
        "video": dict(video),
        "measurement_definitions": {
            name: {
                "display_name": definition.display_name,
                "version": definition.version,
                "unit": definition.unit,
                "dependencies": list(definition.dependencies),
            }
            for name, definition in DEFINITIONS.items()
        },
        "frames": json_frames,
        "notes": {
            "timing": "Frame time uses the session nominal-FPS indexing contract and is not an exact VFR reconstruction.",
            "review": "Manual corrections are operator review edits and are not claims of clinical accuracy.",
        },
    }
    session_json.write_text(json.dumps(session_payload, indent=2) + "\n", encoding="utf-8")

    fig = Figure(figsize=(10, 4.8))
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    for name, definition in DEFINITIONS.items():
        x, y = [], []
        for row in json_frames:
            payload = row["measurements"][name]
            x.append(row["frame_index"])
            y.append(payload["value_deg"] if payload["valid"] else np.nan)
        if x:
            ax.plot(x, y, label=definition.display_name)
    ax.set_xlabel("Frame")
    ax.set_ylabel("Angle (deg)")
    ax.set_title("MotionLab Interactive reviewed/effective measurements")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(figure_png, dpi=160)
    fig.clear()

    outputs = {
        "measurements_csv": measurements_csv,
        "landmarks_csv": landmarks_csv,
        "session_json": session_json,
        "figure_png": figure_png,
    }

    if include_overlay_mp4:
        source = Path(str(video["source_path"]))
        if not source.is_file():
            raise FileNotFoundError(f"source video not found: {source}")
        capture = cv2.VideoCapture(str(source))
        if not capture.isOpened():
            capture.release()
            raise ValueError("unable to open source video for overlay export")
        fps = float(video["fps"])
        size = (int(video["decoded_width_px"]), int(video["decoded_height_px"]))
        if any(dimension % 2 for dimension in size):
            capture.release()
            raise ValueError("MP4 export requires even source dimensions; refusing to crop")
        if len(json_frames) != int(video["frame_count"]) or any(row["frame_index"] != index for index, row in enumerate(json_frames)):
            capture.release()
            raise ValueError("session frames differ from source frame contract")
        writer = cv2.VideoWriter(str(overlay_mp4), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
        if not writer.isOpened():
            capture.release()
            writer.release()
            raise ValueError("unable to create MP4 overlay")
        scale = max(1.0, min(size[0] / 1280, size[1] / 720))
        thickness = max(1, round(2 * scale))
        try:
            count = 0
            while count < len(json_frames):
                decoded, frame = capture.read()
                if not decoded:
                    raise ValueError("source ended before session frame count")
                if (frame.shape[1], frame.shape[0]) != size:
                    raise ValueError("decoded source dimensions differ from session metadata")
                row = json_frames[count]
                landmarks = row["landmarks"]
                for start, end in SEGMENTS:
                    a, b = landmarks[start], landmarks[end]
                    if a and b:
                        cv2.line(
                            frame,
                            (round(a["x_px"]), round(a["y_px"])),
                            (round(b["x_px"]), round(b["y_px"])),
                            (0, 220, 255),
                            thickness,
                            cv2.LINE_AA,
                        )
                for role in SEMANTIC_ROLES:
                    point = landmarks[role]
                    if not point:
                        continue
                    p = (round(point["x_px"]), round(point["y_px"]))
                    cv2.circle(frame, p, round(6 * scale), (0, 255, 0), -1, cv2.LINE_AA)
                    cv2.putText(frame, role, (p[0] + round(8 * scale), p[1] - round(8 * scale)), cv2.FONT_HERSHEY_SIMPLEX, 0.5 * scale, (0, 255, 0), thickness, cv2.LINE_AA)
                lines = []
                for name in ("projected_knee_flexion", "projected_shank_foot_angle", "projected_trunk_inclination"):
                    payload = row["measurements"][name]
                    label = DEFINITIONS[name].display_name.replace("2D projected ", "")
                    lines.append(f"{label}: {payload['value_deg']:.1f} deg" if payload["valid"] and payload["value_deg"] is not None else f"{label}: invalid")
                cv2.rectangle(frame, (0, 0), (round(520 * scale), round(105 * scale)), (0, 0, 0), -1)
                for index, text in enumerate(lines):
                    cv2.putText(frame, text, (round(12 * scale), round((28 + index * 30) * scale)), cv2.FONT_HERSHEY_SIMPLEX, 0.65 * scale, (255, 255, 255), thickness, cv2.LINE_AA)
                writer.write(frame)
                count += 1
            if capture.read()[0]:
                raise ValueError("source contains more frames than session metadata")
        finally:
            capture.release()
            writer.release()
        outputs["overlay_mp4"] = overlay_mp4

        decoded_output = cv2.VideoCapture(str(overlay_mp4))
        try:
            count = 0
            while True:
                ok, frame = decoded_output.read()
                if not ok:
                    break
                if (frame.shape[1], frame.shape[0]) != size:
                    raise ValueError("encoded overlay dimensions differ from source")
                count += 1
            if count != len(json_frames):
                raise ValueError("encoded overlay frame count differs from source")
        finally:
            decoded_output.release()

    return outputs


def export_session_bundle(
    connection,
    *,
    session_id: str,
    output_dir: str | Path,
    include_overlay_mp4: bool = True,
) -> dict[str, Path]:
    """Publish a complete bundle atomically; failed exports leave no partial files."""
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError("export output already exists; choose a new output directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".export-", dir=output.parent) as temporary:
        staging = Path(temporary) / "bundle"
        outputs = _write_session_bundle(
            connection, session_id=session_id, output_dir=staging,
            include_overlay_mp4=include_overlay_mp4,
        )
        staging.rename(output)
        return {name: output / path.name for name, path in outputs.items()}
