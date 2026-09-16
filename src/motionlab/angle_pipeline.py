"""Consume the pinned Sports2D pixel boundary and write traceable M6 results."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from importlib.metadata import version
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from motionlab.sports2d_adapter import (
    SPORTS2D_BODY_WITH_FEET_LANDMARKS,
    Side,
    projected_knee_flexion_from_sports2d,
    read_sports2d_pixel_trc,
)
from motionlab.video_metadata import inspect_video

EVENT_RULE = "maximum_valid_projected_flexion_first_frame_v1"


def _file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def summarize_recording(result: pd.DataFrame) -> dict[str, object]:
    """Maximum finite valid flexion; exact ties select the lowest engine frame."""
    valid = result.loc[result["valid_geometry"]]
    if valid.empty:
        raise ValueError("No valid geometry exists; no event summary can be produced.")
    if not np.isfinite(valid["projected_flexion_deg"]).all():
        raise ValueError("Valid geometry must have finite projected flexion.")
    maximum = valid["projected_flexion_deg"].max()
    peak = valid.loc[valid["projected_flexion_deg"] == maximum].sort_values(
        "sports2d_frame", kind="stable"
    ).iloc[0]
    return {
        "event_rule": EVENT_RULE,
        "side": str(peak["side"]),
        "event_sports2d_frame": int(peak["sports2d_frame"]),
        "event_sports2d_time_s": float(peak["sports2d_time_s"]),
        "maximum_projected_flexion_deg": float(maximum),
        "total_rows": len(result),
        "valid_rows": len(valid),
        "invalid_rows": len(result) - len(valid),
        "invalid_reason_counts": {
            str(reason): int(count)
            for reason, count in result.loc[
                ~result["valid_geometry"], "invalid_reason"
            ].value_counts().items()
        },
        "interpretation": (
            "Maximum observed valid projected flexion across this recording. "
            "A single-squat event interpretation requires a one-squat recording. "
            "Missing frames may conceal a larger flexion value."
        ),
    }


def _validate_engine_provenance(
    engine: dict[str, object], video: Path, source_hash: str, trc: Path
) -> None:
    """Require the existing M5 runner contract, including unprocessed pixels."""
    expected = {
        "contract_version": 1,
        "source_video_name": video.name,
        "source_video_sha256": source_hash,
        "sports2d_version": "0.8.34",
        "pose2sim_version": "0.10.49",
        "pose_model": "Body_with_feet",
        "pose_mode": "balanced",
    }
    for key, value in expected.items():
        if engine.get(key) != value:
            raise ValueError(f"Engine provenance mismatch: {key}.")
    if trc.name != f"{video.stem}_Sports2D_px_person00.trc":
        raise ValueError("Expected the source video's pixel person00 TRC.")
    if trc.name not in engine.get("trc_outputs", []):
        raise ValueError("Pixel TRC is not listed in the engine provenance.")
    config = engine.get("config_overrides", {})
    required = {
        "base": {
            "nb_persons_to_detect": 1,
            "person_ordering_method": "highest_likelihood",
            "save_pose": True,
            "calculate_angles": False,
            "save_angles": False,
            "time_range": [],
        },
        "pose": {"pose_model": "Body_with_feet", "mode": "balanced"},
        "px_to_meters_conversion": {"to_meters": False, "make_c3d": False},
        "post-processing": {
            "interpolate": False, "reject_outliers": False, "filter": False
        },
        "kinematics": {"do_augmentation": False, "do_ik": False},
    }
    for section, settings in required.items():
        for key, value in settings.items():
            if config.get(section, {}).get(key) != value:
                raise ValueError(f"Engine configuration mismatch: {section}.{key}.")


def _code_provenance() -> dict[str, object]:
    module_dir = Path(__file__).resolve().parent
    repo = module_dir.parents[1]
    revision = None
    dirty = None
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo, check=True,
            capture_output=True, text=True,
        ).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        pass
    return {
        "git_revision": revision,
        "working_tree_dirty": dirty,
        "module_sha256": {
            name: _file_hash(module_dir / name)
            for name in ["angle_pipeline.py", "sports2d_adapter.py",
                         "geometry.py", "video_metadata.py"]
        },
    }


def process_video(
    video: str | Path, *, trc: str | Path, engine_provenance: str | Path,
    output_dir: str | Path, side: Side = "right",
) -> dict[str, Path]:
    """Inspect source, verify cached pose provenance, adapt, summarize and plot.

    Existing output files are never overwritten. Inference remains a separate
    documented M5 command; this command only consumes its pinned file boundary.
    """
    video_path, trc_path = Path(video).resolve(), Path(trc).resolve()
    engine_path, destination = Path(engine_provenance).resolve(), Path(output_dir).resolve()
    outputs = {name: destination / filename for name, filename in {
        "csv": "knee_flexion.csv", "figure": "knee_flexion.png",
        "summary": "summary.json", "provenance": "provenance.json",
    }.items()}
    if any(path.exists() for path in outputs.values()):
        raise FileExistsError("Result files already exist; choose a new output directory.")
    metadata = inspect_video(video_path)
    engine_bytes = engine_path.read_bytes()
    engine = json.loads(engine_bytes)
    _validate_engine_provenance(engine, video_path, metadata.sha256, trc_path)
    # Hash exactly the bytes parsed; reject a boundary changing during this read.
    trc_hash = _file_hash(trc_path)
    data = read_sports2d_pixel_trc(trc_path)
    if _file_hash(trc_path) != trc_hash:
        raise ValueError("Pixel TRC changed while it was being read.")
    if not data["sports2d_frame"].is_monotonic_increasing or not data["sports2d_frame"].is_unique:
        raise ValueError("Sports2D frames must be unique and increasing.")
    result = projected_knee_flexion_from_sports2d(data, side=side)
    summary = summarize_recording(result)
    provenance = {
        "schema_version": "motionlab.angle-pipeline.v1",
        "source_metadata": metadata.to_dict(),
        "engine_provenance": engine,
        "engine_provenance_sha256": hashlib.sha256(engine_bytes).hexdigest(),
        "pixel_trc": {"name": trc_path.name, "sha256": trc_hash},
        "motionlab_code": _code_provenance(),
        "python_version": platform.python_version(),
        "motionlab_dependency_versions": {
            package: version(package)
            for package in ["numpy", "pandas", "matplotlib", "opencv-python"]
        },
        "landmark_mapping": SPORTS2D_BODY_WITH_FEET_LANDMARKS[side],
        "coordinate_domain": "pixels from pinned _px_ export; Units=m is an upstream label quirk",
        "timing_contract": "Sports2D engine fields; not independently verified source timestamps",
        "angle_convention": "180 - motionlab.geometry.angle_from_points_deg(hip, knee, ankle)",
        "event_rule": EVENT_RULE,
        "outputs": {key: path.name for key, path in outputs.items()},
    }
    destination.mkdir(parents=True, exist_ok=True)
    result.to_csv(outputs["csv"], index=False, na_rep="NaN")
    figure = Figure(figsize=(9, 4.5))
    FigureCanvasAgg(figure)
    axis = figure.subplots()
    figure.subplots_adjust(left=0.12, right=0.98, bottom=0.16, top=0.87)
    # Reindex gaps too, so missing engine rows cannot be joined by a line.
    series = result.set_index("sports2d_frame")["projected_flexion_deg"]
    series = series.reindex(range(int(series.index.min()), int(series.index.max()) + 1))
    axis.plot(series.index, series.to_numpy(), linewidth=1)
    axis.set(xlabel="Sports2D frame index", ylabel="2D projected knee flexion [deg]",
             title=f"MotionLab projected knee flexion ({side})")
    if series.index.min() != series.index.max():
        axis.set_xlim(series.index.min(), series.index.max())
    axis.text(0.99, 0.97, f"Invalid rows: {summary['invalid_rows']} (unfilled)",
              transform=axis.transAxes, ha="right", va="top", fontsize=9)
    axis.grid(alpha=0.25)
    figure.savefig(outputs["figure"], dpi=160)
    for key, record in [("summary", summary), ("provenance", provenance)]:
        outputs[key].write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return outputs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--trc", required=True, type=Path)
    parser.add_argument("--engine-provenance", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--side", choices=["right", "left"], default="right")
    args = parser.parse_args(argv)
    outputs = process_video(args.video, trc=args.trc, engine_provenance=args.engine_provenance,
                            output_dir=args.output_dir, side=args.side)
    print(json.dumps({key: str(path) for key, path in outputs.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
