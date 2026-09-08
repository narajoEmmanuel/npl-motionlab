"""Inspect reproducibility-relevant metadata from a source video.

The decoded frame dimensions are authoritative for downstream image geometry.
Container metadata exposed by OpenCV is recorded as reported and must not be
interpreted as proof of constant frame timing or correct camera configuration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import cv2


SCHEMA_VERSION = "motionlab.video-metadata.v1"


@dataclass(frozen=True)
class VideoMetadata:
    """Metadata observable from a video file and its first decoded frame."""

    schema_version: str
    source_filename: str
    sha256: str
    file_size_bytes: int
    container_suffix: str
    decoded_width_px: int
    decoded_height_px: int
    frame_count_reported: int | None
    nominal_fps_reported: float | None
    duration_seconds_derived: float | None
    codec_fourcc: str | None
    capture_backend: str
    backend_orientation_degrees: int | None
    orientation_note: str
    timing_note: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable record."""
        return asdict(self)


def _sha256(path: Path) -> str:
    """Return the hexadecimal SHA-256 digest without loading the whole file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _positive_finite_or_none(value: float) -> float | None:
    """Normalize unavailable or invalid positive capture properties to None."""
    if not math.isfinite(value) or value <= 0.0:
        return None
    return float(value)


def _reported_frame_count(value: float) -> int | None:
    """Return a whole reported frame count when the backend provides one."""
    normalized = _positive_finite_or_none(value)
    if normalized is None:
        return None
    rounded = round(normalized)
    if not math.isclose(normalized, rounded, abs_tol=1e-6):
        return None
    return int(rounded)


def _fourcc_text(value: float) -> str | None:
    """Decode an OpenCV FOURCC property when it contains printable text."""
    if not math.isfinite(value) or value <= 0.0:
        return None
    integer = int(value)
    text = "".join(chr((integer >> (8 * index)) & 0xFF) for index in range(4))
    return text if all(character.isprintable() for character in text) else None


def _orientation_degrees(capture: cv2.VideoCapture) -> int | None:
    """Return a supported right-angle orientation value, otherwise None."""
    property_id = getattr(cv2, "CAP_PROP_ORIENTATION_META", None)
    if property_id is None:
        return None
    value = capture.get(property_id)
    if not math.isfinite(value):
        return None
    rounded = int(round(value)) % 360
    return rounded if rounded in {0, 90, 180, 270} else None


def inspect_video(path: str | Path) -> VideoMetadata:
    """Inspect one video without modifying it.

    Raises
    ------
    FileNotFoundError
        If the source path does not identify an existing regular file.
    ValueError
        If OpenCV cannot open the file or decode its first frame.
    """
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Video file does not exist: {source}")

    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        capture.release()
        raise ValueError(f"Unable to open video: {source}")

    try:
        reported_frame_count = _reported_frame_count(
            capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )
        nominal_fps = _positive_finite_or_none(
            capture.get(cv2.CAP_PROP_FPS)
        )
        codec = _fourcc_text(capture.get(cv2.CAP_PROP_FOURCC))
        orientation = _orientation_degrees(capture)
        try:
            backend = capture.getBackendName()
        except cv2.error:
            backend = "unknown"

        decoded, frame = capture.read()
        if not decoded or frame is None or frame.ndim < 2:
            raise ValueError(f"Unable to decode first video frame: {source}")
        height_px, width_px = frame.shape[:2]
    finally:
        capture.release()

    duration = None
    if reported_frame_count is not None and nominal_fps is not None:
        duration = reported_frame_count / nominal_fps

    return VideoMetadata(
        schema_version=SCHEMA_VERSION,
        source_filename=source.name,
        sha256=_sha256(source),
        file_size_bytes=source.stat().st_size,
        container_suffix=source.suffix.lower(),
        decoded_width_px=int(width_px),
        decoded_height_px=int(height_px),
        frame_count_reported=reported_frame_count,
        nominal_fps_reported=nominal_fps,
        duration_seconds_derived=duration,
        codec_fourcc=codec,
        capture_backend=backend,
        backend_orientation_degrees=orientation,
        orientation_note=(
            "Backend-reported orientation; zero can mean either no rotation "
            "or unavailable metadata. Verify display orientation with an "
            "asymmetric target."
        ),
        timing_note=(
            "FPS and frame count are backend-reported header values. Their "
            "ratio is only a derived duration and does not establish constant "
            "frame rate or timestamp integrity."
        ),
    )


def _parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Inspect MotionLab-relevant video metadata."
    )
    parser.add_argument("video", type=Path, help="Source video to inspect.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path; stdout is always emitted.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Inspect a video and emit its metadata as formatted JSON."""
    arguments = _parser().parse_args(argv)
    record = inspect_video(arguments.video)
    serialized = json.dumps(record.to_dict(), indent=2, sort_keys=True)
    print(serialized)
    if arguments.output is not None:
        arguments.output.write_text(serialized + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
