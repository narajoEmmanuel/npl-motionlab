"""Video metadata inspection tests using a generated source video."""

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from motionlab.video_metadata import SCHEMA_VERSION, inspect_video, main


def _write_test_video(path: Path) -> None:
    """Write a small deterministic Motion JPEG video for inspection."""
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        10.0,
        (160, 120),
    )
    if not writer.isOpened():
        pytest.skip("The OpenCV build cannot encode Motion JPEG test video.")
    try:
        for index in range(5):
            frame = np.full((120, 160, 3), index * 30, dtype=np.uint8)
            writer.write(frame)
    finally:
        writer.release()


def test_inspect_video_records_decoded_geometry_and_provenance(
    tmp_path: Path,
) -> None:
    """Record identity and backend-reported properties from a real container."""
    video_path = tmp_path / "synthetic.avi"
    _write_test_video(video_path)

    metadata = inspect_video(video_path)

    assert metadata.schema_version == SCHEMA_VERSION
    assert metadata.source_filename == video_path.name
    assert metadata.sha256 == hashlib.sha256(video_path.read_bytes()).hexdigest()
    assert metadata.file_size_bytes == video_path.stat().st_size
    assert metadata.container_suffix == ".avi"
    assert metadata.decoded_width_px == 160
    assert metadata.decoded_height_px == 120
    assert metadata.frame_count_reported == 5
    assert metadata.nominal_fps_reported == pytest.approx(10.0)
    assert metadata.duration_seconds_derived == pytest.approx(0.5)
    assert metadata.codec_fourcc == "MJPG"
    assert metadata.capture_backend
    assert metadata.to_dict()["sha256"] == metadata.sha256


def test_inspect_video_rejects_missing_path(tmp_path: Path) -> None:
    """Fail explicitly when the requested source file is absent."""
    with pytest.raises(FileNotFoundError, match="does not exist"):
        inspect_video(tmp_path / "missing.mp4")


def test_inspect_video_rejects_undecodable_file(tmp_path: Path) -> None:
    """Do not emit plausible metadata for a non-video file."""
    invalid_path = tmp_path / "invalid.mp4"
    invalid_path.write_bytes(b"not a video")

    with pytest.raises(ValueError, match="Unable to open|Unable to decode"):
        inspect_video(invalid_path)


def test_metadata_cli_writes_same_json_emitted_to_stdout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Provide a reproducible command-line path for retained metadata."""
    video_path = tmp_path / "synthetic.avi"
    output_path = tmp_path / "metadata.json"
    _write_test_video(video_path)

    exit_code = main([str(video_path), "--output", str(output_path)])

    stdout_record = json.loads(capsys.readouterr().out)
    file_record = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert stdout_record == file_record
    assert file_record["schema_version"] == SCHEMA_VERSION
