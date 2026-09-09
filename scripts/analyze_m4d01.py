"""Verify and summarize the private M4-D digitization records."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

from motionlab.geometry import angle_from_points_deg


NOMINAL_ANGLE_DEG = 90.0
EXPECTED_REPEATS = 4


def _sha256(path: Path) -> str:
    """Return a file digest without changing the file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sample_sd(values: list[float]) -> float:
    """Return sample standard deviation for at least two observations."""
    return statistics.stdev(values)


def _capture_summary(
    capture_id: str,
    records: list[dict[str, object]],
) -> dict[str, object]:
    """Validate and summarize four digitizations nested in one frame."""
    angles: list[float] = []
    b_x: list[float] = []
    b_y: list[float] = []

    for record in records:
        if record["capture_id"] != capture_id:
            raise ValueError(f"Capture ID mismatch for {capture_id}.")
        if record["click_order"] != ["A", "B", "C"]:
            raise ValueError(f"Unexpected click order for {capture_id}.")
        if float(record["nominal_reference_deg"]) != NOMINAL_ANGLE_DEG:
            raise ValueError(f"Unexpected nominal angle for {capture_id}.")

        points = record["points_px"]
        if not isinstance(points, dict):
            raise ValueError(f"Invalid point record for {capture_id}.")
        coordinates = []
        for label in ("A", "B", "C"):
            point = points[label]
            if not isinstance(point, dict):
                raise ValueError(f"Invalid point {label} for {capture_id}.")
            coordinate = (float(point["x"]), float(point["y"]))
            if not all(math.isfinite(value) for value in coordinate):
                raise ValueError(f"Non-finite point {label} for {capture_id}.")
            coordinates.append(coordinate)

        angle = angle_from_points_deg(*coordinates)
        saved_angle = record.get("angle_ABC_deg")
        if saved_angle is not None and not math.isclose(
            angle,
            float(saved_angle),
            abs_tol=1e-12,
        ):
            raise ValueError(f"Saved angle mismatch for {capture_id}.")

        angles.append(angle)
        b_x.append(coordinates[1][0])
        b_y.append(coordinates[1][1])

    if len(angles) != EXPECTED_REPEATS:
        raise ValueError(
            f"Expected {EXPECTED_REPEATS} records for {capture_id}; "
            f"found {len(angles)}."
        )

    width = int(records[0]["image_width_px"])
    height = int(records[0]["image_height_px"])
    mean_angle = statistics.fmean(angles)
    mean_b_x = statistics.fmean(b_x)
    mean_b_y = statistics.fmean(b_y)
    return {
        "capture_id": capture_id,
        "n_digitizations": len(angles),
        "verified_angles_deg": angles,
        "mean_angle_deg": mean_angle,
        "mean_signed_difference_deg": mean_angle - NOMINAL_ANGLE_DEG,
        "sample_sd_within_frame_deg": _sample_sd(angles),
        "range_within_frame_deg": max(angles) - min(angles),
        "mean_absolute_difference_deg": statistics.fmean(
            abs(angle - NOMINAL_ANGLE_DEG) for angle in angles
        ),
        "mean_b_px": {"x": mean_b_x, "y": mean_b_y},
        "mean_b_normalized": {
            "x": mean_b_x / width,
            "y": mean_b_y / height,
        },
    }


def _condition_summary(
    condition: str,
    captures: list[dict[str, object]],
) -> dict[str, object]:
    """Summarize recording-level means, not individual digitizations."""
    means = [float(capture["mean_angle_deg"]) for capture in captures]
    return {
        "condition": condition,
        "n_recordings": len(means),
        "capture_means_deg": means,
        "mean_of_capture_means_deg": statistics.fmean(means),
        "mean_signed_difference_deg": (
            statistics.fmean(means) - NOMINAL_ANGLE_DEG
        ),
        "sample_sd_between_recordings_deg": _sample_sd(means),
        "range_between_recording_means_deg": max(means) - min(means),
        "mean_within_frame_sample_sd_deg": statistics.fmean(
            float(capture["sample_sd_within_frame_deg"])
            for capture in captures
        ),
    }


def analyze(directory: Path) -> dict[str, object]:
    """Validate provenance and calculate the predefined nested summaries."""
    manifest = json.loads((directory / "m4d01_manifest.json").read_text())
    summaries: list[dict[str, object]] = []
    operator_ids: set[str] = set()
    procedures: set[str] = set()
    display_settings: set[tuple[int, float]] = set()

    for entry in manifest["captures"]:
        capture_id = entry["capture_id"]
        frame_path = directory / f"{capture_id}_frame_000.png"
        if _sha256(frame_path) != entry["frame_sha256"]:
            raise ValueError(f"Frame checksum mismatch for {capture_id}.")

        paths = sorted(
            directory.glob(f"{capture_id}_digitization_*.json")
        )
        records = [json.loads(path.read_text()) for path in paths]
        for record in records:
            if record["frame_sha256"] != entry["frame_sha256"]:
                raise ValueError(f"Record/frame mismatch for {capture_id}.")
            operator_ids.add(str(record["operator_id"]))
            procedures.add(str(record["procedure"]))
            display_settings.add(
                (int(record["display_width_px"]), float(record["scale"]))
            )
        summaries.append(_capture_summary(capture_id, records))

    if len(operator_ids) != 1:
        raise ValueError(f"Expected one operator; found {sorted(operator_ids)}.")
    if len(procedures) != 1 or len(display_settings) != 1:
        raise ValueError("Digitization procedure or display setting changed.")

    center = [
        summary
        for summary in summaries
        if str(summary["capture_id"]).startswith("m4d01_C_")
        and "return" not in str(summary["capture_id"])
    ]
    right = [
        summary
        for summary in summaries
        if str(summary["capture_id"]).startswith("m4d01_R_")
    ]
    returned = next(
        summary
        for summary in summaries
        if summary["capture_id"] == "m4d01_C_return_01"
    )
    if len(center) != 3 or len(right) != 3:
        raise ValueError("Expected three Center and three Right recordings.")

    center_summary = _condition_summary("Center", center)
    right_summary = _condition_summary("Right", right)
    center_mean = float(center_summary["mean_of_capture_means_deg"])
    right_mean = float(right_summary["mean_of_capture_means_deg"])

    residuals = []
    for capture in summaries:
        angles = [float(value) for value in capture["verified_angles_deg"]]
        capture_mean = statistics.fmean(angles)
        residuals.extend(angle - capture_mean for angle in angles)
    pooled_within_sd = math.sqrt(
        sum(residual * residual for residual in residuals)
        / (len(residuals) - len(summaries))
    )

    return {
        "analysis": "m4d01 predefined image-position comparison",
        "nominal_angle_deg": NOMINAL_ANGLE_DEG,
        "operator_id": next(iter(operator_ids)),
        "observational_structure": (
            "Four digitizations nested within each of seven recordings; "
            "digitizations are not independent camera trials."
        ),
        "angle_verification": (
            "All angles independently calculated with "
            "motionlab.geometry.angle_from_points_deg."
        ),
        "captures": summaries,
        "center": center_summary,
        "right": right_summary,
        "right_minus_center_mean_deg": right_mean - center_mean,
        "return_to_center": returned,
        "return_minus_initial_center_mean_deg": (
            float(returned["mean_angle_deg"]) - center_mean
        ),
        "pooled_within_frame_sample_sd_deg": pooled_within_sd,
        "interpretation_limits": [
            "Not camera accuracy, camera bias, or total uncertainty.",
            "No significance test and no final acceptance threshold.",
            "Target construction, ruler measurement, projection, optics, "
            "decoding, and manual localization remain combined.",
        ],
    }


def main() -> int:
    """Run the private analysis and optionally retain its result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = analyze(arguments.directory)
    serialized = json.dumps(result, indent=2)
    print(serialized)
    if arguments.output is not None:
        with arguments.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
