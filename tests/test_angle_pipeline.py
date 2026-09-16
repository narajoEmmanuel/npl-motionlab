"""M6 contract tests; all inputs are generated and non-identifying."""

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytest

from motionlab.angle_pipeline import EVENT_RULE, main, process_video, summarize_recording
from motionlab.sports2d_adapter import projected_knee_flexion_from_sports2d, read_sports2d_pixel_trc


@pytest.fixture
def inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    video = tmp_path / "synthetic.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 120))
    if not writer.isOpened():
        pytest.skip("OpenCV cannot encode the synthetic Motion JPEG video.")
    try:
        for _ in range(4):
            writer.write(np.zeros((120, 160, 3), dtype=np.uint8))
    finally:
        writer.release()
    trc = tmp_path / "synthetic_Sports2D_px_person00.trc"
    trc.write_text(
        "PathFileType\t4\t(X/Y/Z)\tsynthetic.trc\n"
        "DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\n"
        "10\t10\t4\t3\tm\n"
        "Frame#\tTime\tRHip\t\t\tRKnee\t\t\tRAnkle\t\t\t\n"
        "\t\tX1\tY1\tZ1\tX2\tY2\tZ2\tX3\tY3\tZ3\n"
        "0\t0\t110\t60\t0\t80\t60\t0\t80\t90\t0\n"
        "1\t0.1\t110\t60\t0\t80\t60\t0\t\t\t0\n"
        "2\t0.2\t110\t60\t0\t80\t60\t0\t50\t60\t0\n"
        "3\t0.3\t110\t60\t0\t80\t60\t0\t80\t90\t0\n",
        encoding="utf-8",
    )
    engine = {
        "contract_version": 1, "source_video_name": video.name,
        "source_video_sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
        "sports2d_version": "0.8.34", "pose2sim_version": "0.10.49",
        "pose_model": "Body_with_feet", "pose_mode": "balanced",
        "trc_outputs": [trc.name],
        "config_overrides": {
            "base": {"nb_persons_to_detect": 1, "person_ordering_method": "highest_likelihood",
                     "save_pose": True, "calculate_angles": False, "save_angles": False,
                     "time_range": []},
            "pose": {"pose_model": "Body_with_feet", "mode": "balanced"},
            "px_to_meters_conversion": {"to_meters": False, "make_c3d": False},
            "post-processing": {"interpolate": False, "reject_outliers": False, "filter": False},
            "kinematics": {"do_augmentation": False, "do_ik": False},
        },
    }
    provenance = tmp_path / "engine.json"
    provenance.write_text(json.dumps(engine), encoding="utf-8")
    return video, trc, provenance


def test_cli_end_to_end_preserves_invalid_rows_and_writes_traceable_outputs(
    inputs: tuple[Path, Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    video, trc, engine = inputs
    destination = tmp_path / "results"
    assert main([str(video), "--trc", str(trc), "--engine-provenance", str(engine),
                 "--output-dir", str(destination)]) == 0
    paths = {key: Path(path) for key, path in json.loads(capsys.readouterr().out).items()}
    result = pd.read_csv(paths["csv"], keep_default_na=False)
    assert result.columns.tolist() == [
        "sports2d_frame", "sports2d_time_s", "side", "hip_x_px", "hip_y_px",
        "knee_x_px", "knee_y_px", "ankle_x_px", "ankle_y_px", "included_angle_deg",
        "projected_flexion_deg", "valid_geometry", "invalid_reason",
    ]
    assert result.sports2d_frame.tolist() == [0, 1, 2, 3]
    assert result.loc[1, "projected_flexion_deg"] == "NaN"
    assert result.loc[1, "invalid_reason"] == "missing_landmark"
    assert result.loc[1, "valid_geometry"] == False
    assert result.hip_x_px.tolist() == [110.0] * 4
    summary = json.loads(paths["summary"].read_text())
    assert summary["event_rule"] == EVENT_RULE
    assert summary["maximum_projected_flexion_deg"] == pytest.approx(90)
    assert summary["event_sports2d_frame"] == 0
    assert summary["invalid_reason_counts"] == {"missing_landmark": 1}
    provenance = json.loads(paths["provenance"].read_text())
    assert provenance["source_metadata"]["sha256"] == hashlib.sha256(video.read_bytes()).hexdigest()
    assert provenance["pixel_trc"]["sha256"] == hashlib.sha256(trc.read_bytes()).hexdigest()
    assert provenance["engine_provenance"] == json.loads(engine.read_text())
    assert "angle_pipeline.py" in provenance["motionlab_code"]["module_sha256"]
    assert cv2.imread(str(paths["figure"])).shape[0] > 100


def test_summary_tie_is_lowest_frame_even_when_rows_are_reordered(inputs) -> None:
    _, trc, _ = inputs
    result = projected_knee_flexion_from_sports2d(read_sports2d_pixel_trc(trc))
    assert summarize_recording(result.iloc[::-1])["event_sports2d_frame"] == 0


def test_all_invalid_fails_before_creating_outputs(inputs, tmp_path: Path) -> None:
    video, trc, engine = inputs
    trc.write_text(trc.read_text().replace("110\t60", "80\t60"))
    destination = tmp_path / "results"
    with pytest.raises(ValueError, match="No valid geometry"):
        process_video(video, trc=trc, engine_provenance=engine, output_dir=destination)
    assert not destination.exists()


@pytest.mark.parametrize("defect", ["source_hash", "version", "processing", "meters", "frames"])
def test_incompatible_cached_output_is_rejected(inputs, tmp_path: Path, defect: str) -> None:
    video, trc, engine_path = inputs
    engine = json.loads(engine_path.read_text())
    if defect == "source_hash":
        engine["source_video_sha256"] = "wrong"
    elif defect == "version":
        engine["sports2d_version"] = "0.8.33"
    elif defect == "processing":
        engine["config_overrides"]["post-processing"]["interpolate"] = True
    elif defect == "meters":
        trc = trc.rename(tmp_path / "synthetic_Sports2D_m_person00.trc")
        engine["trc_outputs"] = [trc.name]
    else:
        trc.write_text(trc.read_text().replace("3\t0.3", "2\t0.3"))
    engine_path.write_text(json.dumps(engine))
    destination = tmp_path / "results"
    with pytest.raises(ValueError):
        process_video(video, trc=trc, engine_provenance=engine_path, output_dir=destination)
    assert not destination.exists()


def test_existing_output_is_not_overwritten(inputs, tmp_path: Path) -> None:
    video, trc, engine = inputs
    destination = tmp_path / "results"
    destination.mkdir()
    existing = destination / "summary.json"
    existing.write_text("previous result")
    with pytest.raises(FileExistsError):
        process_video(video, trc=trc, engine_provenance=engine, output_dir=destination)
    assert existing.read_text() == "previous result"
