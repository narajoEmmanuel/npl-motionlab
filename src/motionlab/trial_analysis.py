"""Descriptive analysis of exactly five completed, frozen M7 recordings."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from motionlab.angle_pipeline import (
    EVENT_RULE, _code_provenance, _file_hash, _validate_engine_provenance,
    summarize_recording,
)

TRIAL_IDS = [f"M7_T{i:02d}" for i in range(1, 6)]
EVENT_COLUMNS = [
    "total_rows", "valid_rows", "invalid_rows", "event_sports2d_frame",
    "event_sports2d_time_s", "maximum_projected_flexion_deg",
]
OUTPUT_NAMES = [
    "trial_event_summary.csv", "descriptive_summary.json", "trial_maxima.png",
    "representative_timeseries.png", "analysis_provenance.json",
]
REPO = Path(__file__).resolve().parents[2]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_frozen_modules(code: dict) -> None:
    """Verify historical bytes and current content, allowing Git LF/CRLF checkout.

    M7 hashes retain their original byte meaning; no recorded hash is replaced.
    """
    names = ["angle_pipeline.py", "sports2d_adapter.py", "geometry.py", "video_metadata.py"]
    _require(set(code["module_sha256"]) == set(names), "Frozen module set mismatch.")
    for name in names:
        committed = subprocess.run(
            ["git", "show", f"{code['git_revision']}:src/motionlab/{name}"],
            cwd=REPO, check=True, capture_output=True,
        ).stdout.replace(b"\r\n", b"\n")
        candidates = [committed, committed.replace(b"\n", b"\r\n")]
        _require(code["module_sha256"][name] in
                 {hashlib.sha256(data).hexdigest() for data in candidates}
                 and (REPO / "src/motionlab" / name).read_bytes().replace(b"\r\n", b"\n") == committed,
                 f"Frozen module content/hash mismatch: {name}.")


def load_validated_trials(manifest_path: str | Path) -> tuple[pd.DataFrame, list[dict], pd.DataFrame]:
    """Reject any mismatch before statistics; never repair or exclude trials.

    Relative manifest paths are repository-relative, matching the M7 manifest.
    No video decoding, pose inference, or angle computation is performed.
    """
    manifest = _json(Path(manifest_path))
    _require(manifest.get("schema_version") == "motionlab.m7-trial-manifest.v1",
             "Unsupported M7 manifest schema.")
    trials = manifest.get("trials", [])
    _require(len(trials) == 5 and sorted(t["trial_id"] for t in trials) == TRIAL_IDS,
             "Exactly M7_T01 through M7_T05 are required.")
    _require(len({t["source_sha256"] for t in trials}) == 5, "Source hashes must be distinct.")
    # Load configuration construction only; the isolated runner imports Sports2D
    # inside main(), which is never called by analysis.
    spec = importlib.util.spec_from_file_location(
        "motionlab_frozen_runner", REPO / "integrations/sports2d/run_sports2d.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    records, identities = [], []
    representative = None
    for trial in sorted(trials, key=lambda t: t["trial_id"]):
        label = trial["trial_id"]
        expected = {
            "processing_status": "complete", "selected_side": "right",
            "event_rule": EVENT_RULE, "sports2d_version": "0.8.34",
            "pose2sim_version": "0.10.49", "pose_model": "Body_with_feet",
            "pose_mode": "balanced", "working_tree_dirty": False,
        }
        for key, value in expected.items():
            _require(trial.get(key) == value, f"{label}: manifest mismatch: {key}.")
        root = (REPO / trial["result_directory"]).resolve()
        paths = {name: root / name for name in
                 ["summary.json", "provenance.json", "knee_flexion.csv", "knee_flexion.png"]}
        _require(all(p.is_file() and p.stat().st_size > 0 for p in paths.values()),
                 f"{label}: required outputs missing or empty.")
        before = {name: _file_hash(path) for name, path in paths.items()}
        summary, provenance = _json(paths["summary.json"]), _json(paths["provenance.json"])
        for key in [*EVENT_COLUMNS, "invalid_reason_counts", "event_rule"]:
            _require(trial.get(key) == summary.get(key), f"{label}: manifest-summary mismatch: {key}.")
        _require(summary.get("side") == "right", f"{label}: summary side mismatch.")
        _require(provenance.get("schema_version") == "motionlab.angle-pipeline.v1"
                 and provenance.get("event_rule") == EVENT_RULE
                 and provenance.get("landmark_mapping") == {"hip": "RHip", "knee": "RKnee", "ankle": "RAnkle"}
                 and provenance.get("angle_convention") ==
                 "180 - motionlab.geometry.angle_from_points_deg(hip, knee, ankle)",
                 f"{label}: incompatible M6 provenance.")
        code = provenance["motionlab_code"]
        _require(code["git_revision"] == trial["motionlab_git_revision"]
                 and code["working_tree_dirty"] is False,
                 f"{label}: frozen M6 code provenance mismatch.")
        _validate_frozen_modules(code)
        source, trc, engine_path = [
            (REPO / trial[key]).resolve()
            for key in ["source_path", "pixel_trc_path", "sports2d_provenance_path"]
        ]
        source_hash = _file_hash(source)
        _require(source.name == trial["source_filename"]
                 and source_hash == trial["source_sha256"] == provenance["source_metadata"]["sha256"],
                 f"{label}: source identity mismatch.")
        engine = provenance["engine_provenance"]
        _validate_engine_provenance(engine, source, source_hash, trc)
        _require(engine == _json(engine_path)
                 and provenance["engine_provenance_sha256"] == _file_hash(engine_path)
                 and provenance["pixel_trc"] == {"name": trc.name, "sha256": _file_hash(trc)},
                 f"{label}: cached engine/TRC integrity mismatch.")
        _require(engine["config_overrides"] == runner.build_config(source, engine_path.parent.parent),
                 f"{label}: incompatible full processing configuration.")
        data = pd.read_csv(paths["knee_flexion.csv"])
        _require(data["side"].eq("right").all()
                 and data["sports2d_frame"].is_unique
                 and data["sports2d_frame"].is_monotonic_increasing
                 and data["valid_geometry"].isin([True, False]).all(),
                 f"{label}: CSV side/frame/validity mismatch.")
        invalid = data.loc[~data["valid_geometry"]]
        _require(invalid["projected_flexion_deg"].isna().all()
                 and invalid["invalid_reason"].isin(["missing_landmark", "degenerate_geometry"]).all(),
                 f"{label}: invalid flexion/reason policy mismatch.")
        # Check the existing event against its CSV; do not replace the event.
        checked = summarize_recording(data)
        for key in [*EVENT_COLUMNS, "invalid_reason_counts"]:
            if key in ["event_sports2d_time_s", "maximum_projected_flexion_deg"]:
                equal = np.isclose(checked[key], summary[key], rtol=1e-12, atol=1e-12)
            else:
                equal = checked[key] == summary[key]
            _require(bool(equal), f"{label}: summary-CSV mismatch: {key}.")
        _require(before == {name: _file_hash(path) for name, path in paths.items()},
                 f"{label}: input changed during validation.")
        records.append({"trial_id": label, **{key: summary[key] for key in EVENT_COLUMNS},
                        "processing_status": "complete"})
        identities.append({"trial_id": label, "result_directory": str(root),
                           "input_sha256": before,
                           "invalid_reason_counts": summary["invalid_reason_counts"]})
        if label == TRIAL_IDS[0]:
            representative = data
    return pd.DataFrame(records), identities, representative


def descriptive_statistics(values: Sequence[float]) -> dict[str, int | float]:
    """Only n, mean, sample SD (ddof=1), minimum, maximum, and range."""
    values = np.asarray(values, dtype=float)
    _require(values.ndim == 1 and len(values) == 5 and np.isfinite(values).all(),
             "Exactly five finite per-trial event values are required.")
    return {"n": len(values), "mean_deg": float(np.mean(values)),
            "sample_sd_deg": float(np.std(values, ddof=1)),
            "minimum_deg": float(np.min(values)), "maximum_deg": float(np.max(values)),
            "range_deg": float(np.max(values) - np.min(values))}


def analyze_trials(manifest: str | Path, *, output_dir: str | Path) -> dict[str, Path]:
    """Validate cached M7 outputs and write five private M8 artifacts."""
    manifest = Path(manifest).resolve()
    destination = Path(output_dir).resolve()
    outputs = {name: destination / name for name in OUTPUT_NAMES}
    if any(path.exists() for path in outputs.values()):
        raise FileExistsError("Analysis outputs exist; choose a new output directory.")
    manifest_hash = _file_hash(manifest)
    table, inputs, representative = load_validated_trials(manifest)
    _require(_file_hash(manifest) == manifest_hash, "M7 manifest changed during validation.")
    reasons = {}
    for trial in inputs:
        for reason, count in trial["invalid_reason_counts"].items():
            reasons[reason] = reasons.get(reason, 0) + count
    summary = {
        "schema_version": "motionlab.trial-analysis.v1", "event_rule": EVENT_RULE,
        "side": "right", "standard_deviation_convention": "sample, ddof=1",
        **descriptive_statistics(table["maximum_projected_flexion_deg"]),
        "successful_trial_count": len(table), "pipeline_failure_count": 0,
        "invalid_rows_by_trial": dict(zip(table["trial_id"], table["invalid_rows"].astype(int))),
        "total_invalid_rows": int(table["invalid_rows"].sum()), "invalid_reason_counts": reasons,
        "all_required_trial_outputs_present": True,
        "representative_trial": "M7_T01", "representative_selection": "lowest trial ID; independent of outcome",
    }
    code = _code_provenance()
    provenance = {
        "schema_version": "motionlab.trial-analysis.v1",
        "git_revision": code["git_revision"], "working_tree_dirty": code["working_tree_dirty"],
        "manifest_path": str(manifest), "manifest_sha256": manifest_hash,
        "trial_ids": table["trial_id"].tolist(), "event_rule": EVENT_RULE, "side": "right",
        "standard_deviation_convention": "sample, ddof=1", "inputs": inputs,
        "analysis_module_sha256": _file_hash(Path(__file__)),
        "frozen_module_sha256": code["module_sha256"], "outputs": OUTPUT_NAMES,
    }
    destination.mkdir(parents=True, exist_ok=True)
    table.to_csv(outputs[OUTPUT_NAMES[0]], index=False)
    for name, record in [(OUTPUT_NAMES[1], summary), (OUTPUT_NAMES[4], provenance)]:
        outputs[name].write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    figure = Figure(figsize=(8, 4.8))
    FigureCanvasAgg(figure)
    figure.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.88)
    axis = figure.subplots()
    axis.plot(table["trial_id"], table["maximum_projected_flexion_deg"], "o")
    axis.set(xlabel="Controlled recording", ylabel="Maximum observed 2D projected\nknee flexion [deg]",
             title="Five controlled trial event results")
    axis.grid(axis="y", alpha=0.25)
    figure.savefig(outputs[OUTPUT_NAMES[2]], dpi=160)
    figure = Figure(figsize=(9, 4.5))
    FigureCanvasAgg(figure)
    figure.subplots_adjust(left=0.12, right=0.98, bottom=0.16, top=0.87)
    axis = figure.subplots()
    series = representative.set_index("sports2d_frame")["projected_flexion_deg"]
    series = series.reindex(range(int(series.index.min()), int(series.index.max()) + 1))
    axis.plot(series.index, series.to_numpy(), linewidth=1)
    axis.set(xlabel="Sports2D frame index", ylabel="2D projected knee flexion [deg]",
             title="M7_T01: representative selected by lowest trial ID",
             xlim=(series.index.min(), series.index.max()))
    axis.grid(alpha=0.25)
    figure.savefig(outputs[OUTPUT_NAMES[3]], dpi=160)
    return outputs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps({key: str(path) for key, path in analyze_trials(
        args.manifest, output_dir=args.output_dir).items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
