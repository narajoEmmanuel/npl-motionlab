# Video Angle Overlay

This is a post-Core visualization feature beside the frozen measurement
pipeline. It draws already-computed MotionLab results on the original decoded
video. It does not run Sports2D, compute angles, change the event rule, or alter
M5-M9 code, data, or conclusions. No dependencies were added.

## Inputs and command

Use the original video and its corresponding M6 `knee_flexion.csv`:

```powershell
& .\.venv\Scripts\python.exe -m motionlab.video_overlay `
    data\raw\m7\IMG_5329.mov `
    data\derived\m7\M7_T01\motionlab\knee_flexion.csv `
    data\derived\visualization\M7_T01\M7_T01_angle_overlay.mp4
```

`render_angle_overlay(source_video, csv, output_mp4, *, provenance=None)` is
also available as a Python function. A neighboring M6 `provenance.json` is
automatically used if present; `--provenance PATH` selects it explicitly. It
checks source filename/hash, selected-side mapping, and decoded dimensions.
Without provenance, the caller must establish the source/CSV identity and
orientation; frame counts alone cannot identify a video. M6 provenance does
not authenticate the CSV bytes.

Required CSV fields are `sports2d_frame`, `side`, `hip_x_px`, `hip_y_px`,
`knee_x_px`, `knee_y_px`, `ankle_x_px`, `ankle_y_px`, `projected_flexion_deg`,
`valid_geometry`, and `invalid_reason`.

## Rendering and alignment

Valid rows draw the three named points, hip-knee and knee-ankle segments, and
the CSV projected-flexion value rounded to one decimal for display. Invalid
rows draw only available finite points, no segments or angle, and display
`Projected flexion: invalid` with the explicit invalid reason. No interpolation,
smoothing, missing-coordinate replacement, or geometry computation occurs.
Pixel coordinates are rounded only for raster drawing; input CSVs are unchanged.

CSV row i must have zero-based frame index i in source decode order. Missing,
duplicated, reordered, or partial frame ranges are rejected. Invalid rows still
occupy their original frames. Reported and actual decoded frame counts must
match the CSV. Source dimensions remain unchanged; odd dimensions are rejected
rather than silently cropped. Encoded frames are decoded again to verify count
and dimensions. A mismatch raises an error with no final MP4; temporary video
files are cleaned up. Existing outputs are never overwritten.

## Limitations and privacy

OpenCV uses `mp4v` encoding. Output is re-encoded, silent, and constant at the
source's reported nominal FPS. Audio, original variable-frame timestamps,
container metadata, and lossless image fidelity are not preserved. Source
orientation follows the OpenCV decoder; no additional rotation, flip, rescaling,
or pixel-domain conversion is applied. This is a visual rendering, not timing
verification, pose-accuracy validation, or a second measurement result.

Keep source videos, CSVs, rendered MP4s, and inspection frames private under
ignored `data/raw/` or `data/derived/`. None is committed or published.

## Local checkpoint

The T01 command completed on 2026-09-17 with 70 output frames at 3840 by 2160
pixels and nominal 30 FPS. Start, existing event frame 41, and final frame 69
were visually inspected for readable text, corresponding landmarks, and CSV
angle display. T01 has no invalid rows; invalid rendering is covered by synthetic
tests. No Core processing was rerun or changed.

Focused synthetic tests: **9 passed**. Full suite, run once after implementation:
**95 passed** (86 existing plus 9 visualization tests). Tests cover CSV values
independent of geometry, invalid-frame behavior, schema/side/index errors,
missing finite valid points, source-provenance mismatch, output frame order,
actual decode-count mismatches and cleanup, and overwrite prevention.

**Video overlay feature complete locally.** No remote Git operations or merges
were performed for this feature.
