"""M8 synthetic behavior tests; no private recording is used."""

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from motionlab.angle_pipeline import EVENT_RULE, _code_provenance, _file_hash, summarize_recording
from motionlab.trial_analysis import (
    OUTPUT_NAMES, REPO, analyze_trials, descriptive_statistics, load_validated_trials, main,
)


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def manifest(tmp_path):
    spec = importlib.util.spec_from_file_location("synthetic_runner", REPO / "integrations/sports2d/run_sports2d.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    trials = []
    for index in range(1, 6):
        root = tmp_path / f"M7_T{index:02d}"
        result = root / "motionlab"
        result.mkdir(parents=True)
        source = root / "synthetic.mov"
        source.write_bytes(f"non-video synthetic source {index}".encode())
        engine_root = root / "sports2d"
        engine_dir = engine_root / "synthetic_Sports2D"
        engine_dir.mkdir(parents=True)
        trc = engine_dir / "synthetic_Sports2D_px_person00.trc"
        # M8 consumes cached summaries/CSV; it only verifies the TRC byte hash.
        trc.write_text("synthetic cached boundary", encoding="utf-8")
        engine_path = engine_dir / "motionlab_sports2d_provenance.json"
        engine = {
            "contract_version": 1, "source_video_name": source.name,
            "source_video_sha256": _file_hash(source), "sports2d_version": "0.8.34",
            "pose2sim_version": "0.10.49", "pose_model": "Body_with_feet",
            "pose_mode": "balanced", "trc_outputs": [trc.name],
            "config_overrides": runner.build_config(source, engine_root),
        }
        write_json(engine_path, engine)
        data = pd.DataFrame({
            "sports2d_frame": [0, 1, 2], "sports2d_time_s": [0.0, 0.1, 0.2],
            "side": ["right"] * 3, "projected_flexion_deg": [0.0, float("nan"), float(index * 10)],
            "valid_geometry": [True, False, True], "invalid_reason": ["", "missing_landmark", ""],
        })
        data.to_csv(result / "knee_flexion.csv", index=False, na_rep="NaN")
        summary = summarize_recording(data)
        write_json(result / "summary.json", summary)
        (result / "knee_flexion.png").write_bytes(b"synthetic existing technical figure")
        code = _code_provenance()
        provenance = {
            "schema_version": "motionlab.angle-pipeline.v1", "event_rule": EVENT_RULE,
            "landmark_mapping": {"hip": "RHip", "knee": "RKnee", "ankle": "RAnkle"},
            "angle_convention": "180 - motionlab.geometry.angle_from_points_deg(hip, knee, ankle)",
            "source_metadata": {"sha256": _file_hash(source)},
            "engine_provenance": engine, "engine_provenance_sha256": _file_hash(engine_path),
            "pixel_trc": {"name": trc.name, "sha256": _file_hash(trc)},
            "motionlab_code": {**code, "working_tree_dirty": False},
        }
        write_json(result / "provenance.json", provenance)
        trials.append({
            **summary, "trial_id": root.name, "source_path": str(source),
            "source_filename": source.name, "source_sha256": _file_hash(source),
            "result_directory": str(result), "pixel_trc_path": str(trc),
            "sports2d_provenance_path": str(engine_path), "selected_side": "right",
            "processing_status": "complete", "sports2d_version": "0.8.34",
            "pose2sim_version": "0.10.49", "pose_model": "Body_with_feet", "pose_mode": "balanced",
            "motionlab_git_revision": code["git_revision"], "working_tree_dirty": False,
        })
    path = tmp_path / "manifest.json"
    write_json(path, {"schema_version": "motionlab.m7-trial-manifest.v1", "trials": trials})
    return path


def test_known_descriptive_values_use_sample_sd():
    assert descriptive_statistics([10, 20, 30, 40, 50]) == pytest.approx({
        "n": 5, "mean_deg": 30, "sample_sd_deg": 250 ** 0.5,
        "minimum_deg": 10, "maximum_deg": 50, "range_deg": 40,
    })


@pytest.mark.parametrize("defect", [
    "count", "duplicate_source", "side", "event_rule", "incomplete",
    "summary", "version", "configuration", "module_hash", "csv_invalid",
])
def test_inconsistent_inputs_rejected_without_outputs(manifest, tmp_path, defect):
    record = json.loads(manifest.read_text())
    trial = record["trials"][0]
    if defect == "count":
        record["trials"].pop()
    elif defect == "duplicate_source":
        trial["source_sha256"] = record["trials"][1]["source_sha256"]
    elif defect in ["side", "event_rule", "incomplete", "version"]:
        key, value = {"side": ("selected_side", "left"), "event_rule": ("event_rule", "different"),
                      "incomplete": ("processing_status", "pending"), "version": ("sports2d_version", "other")}[defect]
        trial[key] = value
    elif defect == "summary":
        trial["maximum_projected_flexion_deg"] += 1
    elif defect in ["configuration", "module_hash"]:
        path = Path(trial["result_directory"]) / "provenance.json"
        provenance = json.loads(path.read_text())
        if defect == "module_hash":
            provenance["motionlab_code"]["module_sha256"]["angle_pipeline.py"] = "wrong"
        else:
            engine = provenance["engine_provenance"]
            engine["config_overrides"]["pose"]["det_frequency"] = 99
            engine_path = Path(trial["sports2d_provenance_path"])
            write_json(engine_path, engine)
            provenance["engine_provenance_sha256"] = _file_hash(engine_path)
        write_json(path, provenance)
    else:
        path = Path(trial["result_directory"]) / "knee_flexion.csv"
        data = pd.read_csv(path)
        data.loc[1, "projected_flexion_deg"] = 0
        data.to_csv(path, index=False)
    write_json(manifest, record)
    destination = tmp_path / "rejected"
    with pytest.raises(ValueError):
        analyze_trials(manifest, output_dir=destination)
    assert not destination.exists()


def test_cli_outputs_schema_missingness_and_overwrite_protection(manifest, tmp_path, capsys):
    destination = tmp_path / "analysis"
    assert main([str(manifest), "--output-dir", str(destination)]) == 0
    paths = json.loads(capsys.readouterr().out)
    assert set(paths) == set(OUTPUT_NAMES)
    summary = json.loads((destination / "descriptive_summary.json").read_text())
    assert summary["mean_deg"] == 30
    assert summary["sample_sd_deg"] == pytest.approx(250 ** 0.5)
    assert summary["total_invalid_rows"] == 5
    assert summary["invalid_reason_counts"] == {"missing_landmark": 5}
    assert summary["successful_trial_count"] == 5 and summary["pipeline_failure_count"] == 0
    assert summary["representative_trial"] == "M7_T01"
    provenance = json.loads((destination / "analysis_provenance.json").read_text())
    assert provenance["manifest_sha256"] == _file_hash(manifest)
    assert provenance["standard_deviation_convention"] == "sample, ddof=1"
    assert len(provenance["inputs"]) == 5
    table = pd.read_csv(destination / "trial_event_summary.csv")
    assert table["maximum_projected_flexion_deg"].tolist() == [10, 20, 30, 40, 50]
    for name in ["trial_maxima.png", "representative_timeseries.png"]:
        assert (destination / name).read_bytes().startswith(b"\x89PNG")
    with pytest.raises(FileExistsError):
        analyze_trials(manifest, output_dir=destination)


def test_validation_accepts_only_verified_git_line_ending_conversion(manifest):
    record = json.loads(manifest.read_text())
    for trial in record["trials"]:
        path = Path(trial["result_directory"]) / "provenance.json"
        provenance = json.loads(path.read_text())
        import hashlib
        module = (REPO / "src/motionlab/angle_pipeline.py").read_bytes().replace(b"\r\n", b"\n")
        provenance["motionlab_code"]["module_sha256"]["angle_pipeline.py"] = hashlib.sha256(module).hexdigest()
        write_json(path, provenance)
    table, _, series = load_validated_trials(manifest)
    assert len(table) == 5 and pd.isna(series.loc[1, "projected_flexion_deg"])
