"""Render existing MotionLab CSV angles on video; visualization only."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np
import pandas as pd

COORDINATES = [f"{point}_{axis}_px" for point in ["hip", "knee", "ankle"] for axis in ["x", "y"]]
REQUIRED = ["sports2d_frame", "side", *COORDINATES,
            "projected_flexion_deg", "valid_geometry", "invalid_reason"]


def _load_rows(csv: Path) -> pd.DataFrame:
    rows = pd.read_csv(csv)
    if not set(REQUIRED).issubset(rows.columns):
        raise ValueError("CSV missing required MotionLab columns.")
    if rows.empty or not rows["sports2d_frame"].eq(np.arange(len(rows))).all():
        raise ValueError("CSV frames must be consecutive zero-based source indices, in order.")
    if rows["side"].nunique() != 1 or not rows["side"].isin(["right", "left"]).all():
        raise ValueError("CSV must contain one consistent selected side.")
    if not rows["valid_geometry"].isin([True, False]).all():
        raise ValueError("CSV valid_geometry must contain booleans.")
    for column in [*COORDINATES, "projected_flexion_deg"]:
        rows[column] = pd.to_numeric(rows[column], errors="raise")
        if np.isinf(rows[column]).any():
            raise ValueError("CSV cannot contain infinite coordinates or angles.")
    valid = rows["valid_geometry"].astype(bool)
    if not np.isfinite(rows.loc[valid, [*COORDINATES, "projected_flexion_deg"]]).all().all():
        raise ValueError("Valid rows require finite coordinates and CSV angles.")
    if not rows.loc[~valid, "projected_flexion_deg"].isna().all():
        raise ValueError("Invalid rows must retain NaN angles.")
    if not rows.loc[~valid, "invalid_reason"].isin(["missing_landmark", "degenerate_geometry"]).all():
        raise ValueError("Invalid rows require an explicit MotionLab invalid reason.")
    return rows


def _draw_row(frame: np.ndarray, row: pd.Series, index: int) -> None:
    scale = max(0.5, min(frame.shape[:2]) / 720)
    thickness = max(1, round(2 * scale))
    points = {}
    for name in ["hip", "knee", "ankle"]:
        xy = [row[f"{name}_x_px"], row[f"{name}_y_px"]]
        if np.isfinite(xy).all():
            points[name] = tuple(round(float(value)) for value in xy)
    valid = bool(row["valid_geometry"])
    if valid:
        for start, end in [("hip", "knee"), ("knee", "ankle")]:
            cv2.line(frame, points[start], points[end], (0, 220, 255), thickness, cv2.LINE_AA)
    for name, point in points.items():
        cv2.circle(frame, point, max(3, round(5 * scale)), (0, 255, 0), -1, cv2.LINE_AA)
        cv2.putText(frame, name, (point[0] + round(8 * scale), point[1] - round(8 * scale)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55 * scale, (0, 255, 0), thickness, cv2.LINE_AA)
    text = (f"Projected flexion: {row['projected_flexion_deg']:.1f} deg" if valid
            else "Projected flexion: invalid")
    status = f"Frame {index} | {row['side']} | " + ("valid" if valid else str(row["invalid_reason"]))
    lines = [text, status]
    font_scale = 0.8 * scale
    height = round(35 * scale)
    width = max(cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0][0]
                for line in lines) + round(30 * scale)
    cv2.rectangle(frame, (0, 0), (width, height * 2 + round(10 * scale)), (0, 0, 0), -1)
    for line_index, line in enumerate(lines, 1):
        cv2.putText(frame, line, (round(12 * scale), height * line_index),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    (255, 255, 255) if valid else (80, 80, 255), thickness, cv2.LINE_AA)


def render_angle_overlay(
    source_video: str | Path, csv: str | Path, output_mp4: str | Path,
    *, provenance: str | Path | None = None,
) -> Path:
    """Render CSV values verbatim (one decimal for display), without geometry.

    CSV row i must correspond to decoded source frame i, including invalid rows.
    A neighboring provenance.json is used automatically when present. Output is
    a silent, constant-nominal-FPS MP4; source timing/audio are not reconstructed.
    Existing results are never overwritten; failed renders leave no final MP4.
    """
    source, csv_path, output = [Path(path).resolve() for path in [source_video, csv, output_mp4]]
    if output.suffix.lower() != ".mp4":
        raise ValueError("Output must be an MP4 path.")
    if output.exists():
        raise FileExistsError("Overlay exists; choose a new output path.")
    rows = _load_rows(csv_path)
    provenance_path = Path(provenance).resolve() if provenance is not None else csv_path.with_name("provenance.json")
    metadata = None
    if provenance is not None or provenance_path.exists():
        record = json.loads(provenance_path.read_text(encoding="utf-8"))
        if record.get("schema_version") != "motionlab.angle-pipeline.v1":
            raise ValueError("Expected existing MotionLab M6 provenance.")
        metadata = record["source_metadata"]
        with source.open("rb") as stream:
            source_hash = hashlib.file_digest(stream, "sha256").hexdigest()
        if source.name != metadata["source_filename"] or source_hash != metadata["sha256"]:
            raise ValueError("Source video does not match M6 provenance.")
        expected_mapping = {name: ("R" if rows.iloc[0]["side"] == "right" else "L") + name.capitalize()
                            for name in ["hip", "knee", "ankle"]}
        if record.get("landmark_mapping") != expected_mapping:
            raise ValueError("CSV side does not match M6 provenance.")
    capture = cv2.VideoCapture(str(source))
    writer, temporary = None, None
    try:
        if not capture.isOpened():
            raise ValueError("Cannot open source video.")
        fps = capture.get(cv2.CAP_PROP_FPS)
        reported = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        if not np.isfinite(fps) or fps <= 0:
            raise ValueError("Source nominal FPS is unavailable.")
        if np.isfinite(reported) and reported > 0 and reported != len(rows):
            raise ValueError("Video/CSV frame count mismatch.")
        count, size = 0, None
        while True:
            decoded, frame = capture.read()
            if not decoded:
                break
            if count >= len(rows):
                raise ValueError("Video/CSV decoded frame count mismatch.")
            current_size = (frame.shape[1], frame.shape[0])
            if size is None:
                size = current_size
                if metadata and size != (metadata["decoded_width_px"], metadata["decoded_height_px"]):
                    raise ValueError("Decoded orientation/dimensions differ from M6 provenance.")
                if size[0] % 2 or size[1] % 2:
                    raise ValueError("MP4 encoding requires even dimensions; no silent crop is allowed.")
                output.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".mp4", delete=False) as handle:
                    temporary = Path(handle.name)
                writer = cv2.VideoWriter(str(temporary), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
                if not writer.isOpened():
                    raise ValueError("OpenCV cannot encode MP4 with mp4v.")
            elif current_size != size:
                raise ValueError("Source frame dimensions changed.")
            _draw_row(frame, rows.iloc[count], count)
            writer.write(frame)
            count += 1
        if count != len(rows):
            raise ValueError("Video/CSV decoded frame count mismatch.")
        writer.release()
        # Verify the encoder did not silently drop/crop frames before publishing.
        check = cv2.VideoCapture(str(temporary))
        encoded_count = 0
        try:
            while True:
                decoded, frame = check.read()
                if not decoded:
                    break
                if (frame.shape[1], frame.shape[0]) != size:
                    raise ValueError("Encoded frame dimensions mismatch.")
                encoded_count += 1
        finally:
            check.release()
        if encoded_count != count:
            raise ValueError("Encoded frame count mismatch.")
        if output.exists():
            raise FileExistsError("Overlay output appeared during rendering.")
        temporary.rename(output)
        return output
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_video", type=Path)
    parser.add_argument("csv", type=Path)
    parser.add_argument("output_mp4", type=Path)
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args(argv)
    print(render_angle_overlay(args.source_video, args.csv, args.output_mp4, provenance=args.provenance))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
