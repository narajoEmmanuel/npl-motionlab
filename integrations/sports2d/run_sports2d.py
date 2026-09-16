"""Run the pinned Sports2D workflow used by MotionLab M5.

This script belongs to the isolated Sports2D environment. It intentionally does
not import the MotionLab package. The integration boundary is the pixel TRC
file written by Sports2D.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path

SPORTS2D_VERSION = "0.8.34"
POSE2SIM_VERSION = "0.10.49"
POSE_MODEL = "Body_with_feet"
POSE_MODE = "balanced"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_config(video: Path, result_dir: Path) -> dict[str, object]:
    """Return the explicit MotionLab overrides for Sports2D 0.8.34."""
    return {
        "base": {
            "video_input": str(video.resolve()),
            "nb_persons_to_detect": 1,
            "person_ordering_method": "highest_likelihood",
            "visible_side": ["none"],
            "time_range": [],
            "video_dir": "",
            "show_realtime_results": False,
            "save_vid": False,
            "save_img": False,
            "save_pose": True,
            "calculate_angles": False,
            "save_angles": False,
            "result_dir": str(result_dir.resolve()),
        },
        "pose": {
            "pose_model": POSE_MODEL,
            "mode": POSE_MODE,
            "det_frequency": 4,
            "device": "auto",
            "backend": "auto",
            "keypoint_likelihood_threshold": 0.3,
            "average_likelihood_threshold": 0.5,
            "keypoint_number_threshold": 0.3,
            "tracking_mode": "sports2d",
            "predict_displacement": False,
            "match_by": "keypoints",
            "max_distance": 250,
            "min_iou": 0.2,
            "max_unseen_time": 1.0,
        },
        "px_to_meters_conversion": {
            "to_meters": False,
            "make_c3d": False,
            "save_calib": False,
        },
        "post-processing": {
            "interpolate": False,
            "reject_outliers": False,
            "filter": False,
            "show_graphs": False,
            "save_graphs": False,
        },
        "kinematics": {
            "do_augmentation": False,
            "do_ik": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the pinned Sports2D pixel-landmark workflow for MotionLab."
    )
    parser.add_argument("video", type=Path, help="Original local video path.")
    parser.add_argument(
        "--result-dir",
        type=Path,
        default=Path("data/derived/sports2d"),
        help="Private/local Sports2D output root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video = args.video.resolve()
    result_dir = args.result_dir.resolve()

    if not video.is_file():
        raise FileNotFoundError(f"Video not found: {video}")

    installed_sports2d = version("sports2d")
    installed_pose2sim = version("Pose2Sim")
    if installed_sports2d != SPORTS2D_VERSION:
        raise RuntimeError(
            f"Expected sports2d=={SPORTS2D_VERSION}, found {installed_sports2d}."
        )
    if installed_pose2sim != POSE2SIM_VERSION:
        raise RuntimeError(
            f"Expected Pose2Sim=={POSE2SIM_VERSION}, found {installed_pose2sim}."
        )

    # Import only inside the isolated pose-engine environment. Sports2D carries
    # a substantially larger dependency/global-state surface than MotionLab.
    from Sports2D import Sports2D

    result_dir.mkdir(parents=True, exist_ok=True)
    config = build_config(video, result_dir)
    Sports2D.process(config)

    output_dir = result_dir / f"{video.stem}_Sports2D"
    output_dir.mkdir(parents=True, exist_ok=True)
    trc_candidates = sorted(output_dir.glob(f"{video.stem}_Sports2D_px_person*.trc"))

    provenance = {
        "contract_version": 1,
        "source_video_name": video.name,
        "source_video_sha256": _sha256_file(video),
        "sports2d_version": installed_sports2d,
        "pose2sim_version": installed_pose2sim,
        "python_version": platform.python_version(),
        "pose_model": POSE_MODEL,
        "pose_mode": POSE_MODE,
        "authoritative_angle_engine": "MotionLab, not Sports2D",
        "coordinate_contract": "Sports2D *_px_personNN.trc X/Y pixel coordinates",
        "confidence_contract": (
            "Sports2D applies the configured likelihood thresholds before TRC "
            "export; low-confidence coordinates may be NaN. Confidence scores "
            "are not part of the M5 TRC file contract."
        ),
        "source_time_contract": (
            "TRC frame/time fields are preserved as Sports2D engine provenance; "
            "they are not independently verified source-video timestamps."
        ),
        "model_artifact_hash": None,
        "model_artifact_hash_note": (
            "Sports2D 0.8.34 does not expose the downloaded inference artifact "
            "hash through this file contract. Package/model/mode configuration "
            "is pinned; model-file hashing is deferred unless a Core result "
            "specifically requires it."
        ),
        "config_overrides": config,
        "trc_outputs": [str(path.relative_to(output_dir)) for path in trc_candidates],
    }
    provenance_path = output_dir / "motionlab_sports2d_provenance.json"
    provenance_path.write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if not trc_candidates:
        raise RuntimeError(
            "Sports2D completed without the expected pixel TRC output. "
            f"Inspect {output_dir / 'logs.txt'}."
        )

    print(f"Pixel TRC: {trc_candidates[0]}")
    print(f"Provenance: {provenance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
