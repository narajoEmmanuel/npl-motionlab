"""Adapter for Sports2D pixel-coordinate TRC outputs.

Sports2D is an external pose-estimation engine. This module deliberately does
not import Sports2D. It consumes the pixel TRC boundary produced by the pinned
external workflow and maps named landmarks into MotionLab's verified geometry.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from motionlab.geometry import angle_from_points_deg

Side = Literal["right", "left"]

SPORTS2D_BODY_WITH_FEET_LANDMARKS: dict[str, dict[str, str]] = {
    "right": {"hip": "RHip", "knee": "RKnee", "ankle": "RAnkle"},
    "left": {"hip": "LHip", "knee": "LKnee", "ankle": "LAnkle"},
}


def _parse_float(value: str, *, field: str, allow_nan: bool) -> float:
    text = value.strip()
    if text == "":
        if allow_nan:
            return float("nan")
        raise ValueError(f"{field} is blank.")

    try:
        parsed = float(text)
    except ValueError as exc:
        raise ValueError(f"{field} must be numeric; received {value!r}.") from exc

    if np.isinf(parsed):
        raise ValueError(f"{field} must not be infinite.")
    if np.isnan(parsed) and not allow_nan:
        raise ValueError(f"{field} must be finite.")
    return parsed


def read_sports2d_pixel_trc(path: str | Path) -> pd.DataFrame:
    """Read a Sports2D ``*_px_personNN.trc`` file without rescaling coordinates.

    The returned frame/time fields are Sports2D's own TRC fields. MotionLab
    preserves them as engine provenance and does not treat the TRC time column
    as an independently verified source-video timestamp.
    """
    trc_path = Path(path)
    if not trc_path.is_file():
        raise FileNotFoundError(f"Sports2D TRC file not found: {trc_path}")

    lines = trc_path.read_text(encoding="utf-8-sig").splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.split("\t", 2)[:2] == ["Frame#", "Time"]
        ),
        None,
    )
    if header_index is None:
        raise ValueError("TRC marker header 'Frame#\\tTime' was not found.")

    header_fields = lines[header_index].split("\t")
    marker_names = tuple(
        field.strip() for field in header_fields[2:] if field.strip()
    )
    if not marker_names:
        raise ValueError("TRC file does not declare any marker names.")
    if len(set(marker_names)) != len(marker_names):
        raise ValueError("TRC marker names must be unique.")

    expected_fields = 2 + 3 * len(marker_names)
    records: list[dict[str, float | int]] = []

    for line_number, line in enumerate(lines[header_index + 2 :], start=header_index + 3):
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) < expected_fields:
            fields += [""] * (expected_fields - len(fields))
        elif len(fields) > expected_fields:
            extras = fields[expected_fields:]
            if any(value.strip() for value in extras):
                raise ValueError(
                    f"TRC row {line_number} has unexpected non-empty fields."
                )
            fields = fields[:expected_fields]

        frame_value = _parse_float(
            fields[0], field=f"row {line_number} Frame#", allow_nan=False
        )
        if not frame_value.is_integer():
            raise ValueError(f"TRC row {line_number} Frame# must be an integer.")

        record: dict[str, float | int] = {
            "sports2d_frame": int(frame_value),
            "sports2d_time_s": _parse_float(
                fields[1], field=f"row {line_number} Time", allow_nan=False
            ),
        }

        for marker_index, marker_name in enumerate(marker_names):
            offset = 2 + marker_index * 3
            record[f"{marker_name}_x_px"] = _parse_float(
                fields[offset],
                field=f"row {line_number} {marker_name} X",
                allow_nan=True,
            )
            record[f"{marker_name}_y_px"] = _parse_float(
                fields[offset + 1],
                field=f"row {line_number} {marker_name} Y",
                allow_nan=True,
            )
            record[f"{marker_name}_z"] = _parse_float(
                fields[offset + 2],
                field=f"row {line_number} {marker_name} Z",
                allow_nan=True,
            )
        records.append(record)

    if not records:
        raise ValueError("TRC file contains no data rows.")

    return pd.DataFrame.from_records(records)


def projected_knee_flexion_from_sports2d(
    trc_data: pd.DataFrame,
    *,
    side: Side = "right",
) -> pd.DataFrame:
    """Map Sports2D landmarks to MotionLab and compute projected knee flexion."""
    side_key = side.lower()
    if side_key not in SPORTS2D_BODY_WITH_FEET_LANDMARKS:
        raise ValueError("side must be 'right' or 'left'.")

    mapping = SPORTS2D_BODY_WITH_FEET_LANDMARKS[side_key]
    required = ["sports2d_frame", "sports2d_time_s"]
    for marker_name in mapping.values():
        required.extend([f"{marker_name}_x_px", f"{marker_name}_y_px"])

    missing_columns = [column for column in required if column not in trc_data]
    if missing_columns:
        raise ValueError(
            "Sports2D TRC data is missing required columns: "
            + ", ".join(missing_columns)
        )

    rows: list[dict[str, object]] = []
    for row in trc_data.itertuples(index=False):
        row_dict = row._asdict()
        hip = np.array(
            [
                row_dict[f"{mapping['hip']}_x_px"],
                row_dict[f"{mapping['hip']}_y_px"],
            ],
            dtype=float,
        )
        knee = np.array(
            [
                row_dict[f"{mapping['knee']}_x_px"],
                row_dict[f"{mapping['knee']}_y_px"],
            ],
            dtype=float,
        )
        ankle = np.array(
            [
                row_dict[f"{mapping['ankle']}_x_px"],
                row_dict[f"{mapping['ankle']}_y_px"],
            ],
            dtype=float,
        )

        included_angle = float("nan")
        projected_flexion = float("nan")
        valid = False
        invalid_reason = ""

        if not np.all(np.isfinite(np.concatenate([hip, knee, ankle]))):
            invalid_reason = "missing_landmark"
        else:
            try:
                included_angle = angle_from_points_deg(hip, knee, ankle)
            except ValueError:
                invalid_reason = "degenerate_geometry"
            else:
                projected_flexion = 180.0 - included_angle
                valid = True

        rows.append(
            {
                "sports2d_frame": int(row_dict["sports2d_frame"]),
                "sports2d_time_s": float(row_dict["sports2d_time_s"]),
                "side": side_key,
                "hip_x_px": float(hip[0]),
                "hip_y_px": float(hip[1]),
                "knee_x_px": float(knee[0]),
                "knee_y_px": float(knee[1]),
                "ankle_x_px": float(ankle[0]),
                "ankle_y_px": float(ankle[1]),
                "included_angle_deg": included_angle,
                "projected_flexion_deg": projected_flexion,
                "valid_geometry": valid,
                "invalid_reason": invalid_reason,
            }
        )

    return pd.DataFrame.from_records(rows)
