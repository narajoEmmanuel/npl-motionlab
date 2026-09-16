# M6 End-to-End Angle Pipeline

**M6 COMPLETE locally**, demonstrated on the existing private representative
video on 2026-09-16. M7 has not started. No remote Git operations were performed.

## Architecture

`motionlab.angle_pipeline.process_video` orchestrates the existing `inspect_video`,
`read_sports2d_pixel_trc`, and `projected_knee_flexion_from_sports2d` without
modifying them. The adapter calls the existing verified geometry. Sports2D owns
inference/tracking; MotionLab owns mapping, geometry and traceability. No new
dependencies, filtering, interpolation, or pose implementation were added.

## Reproduction on Windows

From the repository root, the demonstrated command is:

```powershell
& .\.venv\Scripts\python.exe -m motionlab.angle_pipeline `
  data\raw\m5\IMG_5306.mov `
  --trc data\derived\sports2d\IMG_5306_Sports2D\IMG_5306_Sports2D_px_person00.trc `
  --engine-provenance data\derived\sports2d\IMG_5306_Sports2D\motionlab_sports2d_provenance.json `
  --side right `
  --output-dir data\derived\m6\IMG_5306_right_clean_4cc8cfa
```

These are private local inputs, unavailable in a public checkout. Substitute
the source and corresponding M5 export paths for other local recordings. The
M6 checkpoint reused the M5 TRC; no inference was rerun. For a new recording,
first run the existing M5 runner in the isolated Sports2D environment:

```powershell
& "$env:USERPROFILE\.venv\sports2d-motionlab\Scripts\python.exe" `
  integrations\sports2d\run_sports2d.py `
  data\raw\YOUR_VIDEO.mp4 `
  --result-dir data\derived\sports2d
```

Then consume its pixel TRC and engine JSON with the MotionLab command. Side is
explicit (`right` by default, or `left`). Existing result files are not
overwritten; choose a new output directory for another run.

## Checks and provenance

The source is decoded/hashed using the existing metadata utility. Filename and
SHA-256 must match engine provenance. M6 requires Sports2D 0.8.34, Pose2Sim
0.10.49, Body_with_feet, balanced mode, one highest-likelihood person, and the
source-specific `_px_person00.trc` listed in engine provenance. Meter conversion,
Sports2D angles, interpolation, filtering, outlier rejection, augmentation and
IK must be disabled. Partial time ranges are rejected. Engine frames must be
unique and increasing; rows are neither reordered nor dropped.

`provenance.json` records source metadata/hash, the full engine JSON and its
hash, input TRC identity/hash, semantic mapping, angle convention, event rule,
output names, Python/dependency versions, Git revision and dirty status, and
SHA-256 of the four MotionLab modules used. Module hashes identify the executed
code even before it is committed. Git fields may be null when Git is unavailable.
The output names/directory link all four artifacts to this provenance record.

These checks detect source/config mismatches; they do not authenticate the
engine JSON or prove that the TRC was never edited before consumption. The M5
runner does not supply an original TRC hash. M6 hashes the consumed bytes and
checks that they did not change during parsing.

The Sports2D `Units=m` header quirk remains unchanged. Pixel meaning comes from
the pinned `_px_` export path/configuration, not that label. Frame/time fields
remain engine provenance, not independently verified source timestamps.

## Output contract and invalid-data policy

| File | Contents |
|---|---|
| `knee_flexion.csv` | All adapted frames including invalid rows |
| `knee_flexion.png` | Projected flexion versus engine frame, with invalid gaps unfilled |
| `summary.json` | Deterministic recording maximum and validity counts |
| `provenance.json` | Source, engine, configuration and code traceability |

CSV columns, in order:

```text
sports2d_frame, sports2d_time_s, side,
hip_x_px, hip_y_px, knee_x_px, knee_y_px, ankle_x_px, ankle_y_px,
included_angle_deg, projected_flexion_deg, valid_geometry, invalid_reason
```

Coordinates are preserved without rescaling. Missing points retain NaN
coordinates/angles, `valid_geometry=false` and `missing_landmark`. Degenerate
geometry retains NaN angles and `degenerate_geometry`. The CSV explicitly
writes missing numbers as `NaN`. No invalid frames are dropped or filled.
If no valid geometry exists, processing fails before creating output artifacts.

The figure spans the full engine frame range, including an invalid tail.
NaN values and absent frame indices break the curve. No smoothing or
interpolation is applied; labels include units and the invalid-row count.

## Event rule

Identifier: `maximum_valid_projected_flexion_first_frame_v1`.

1. Consider rows with valid geometry and finite projected flexion.
2. Take the maximum across the recording.
3. Resolve exact ties using the lowest engine frame index.
4. Record that frame/time, selected side, maximum, total/valid/invalid counts
   and invalid-reason counts.

This is the **maximum observed valid projected flexion of the recording**. It
does not segment repetitions, infer a physical bottom-of-squat instant, or
recover peaks hidden by missing landmarks. The rule and side must remain fixed
before applying it identically to M7's five one-squat-per-video trials.

Inspection of the unsmoothed representative series showed three prominent
flexion episodes. The global maximum, 118.19774379200672 degrees at frame 260,
belongs to a sustained high-flexion episode: frames 252 through 268 are valid
and exceed 111 degrees. Another episode reaches approximately 117.98 degrees.
The maximum is defensible as a recording summary without segmentation. This
does not establish stability of the winning frame/repetition under landmark
noise or repeated inference. The representative recording is not claimed as a
single M7 trial or three independent trials. Single-squat interpretation depends
on acquisition, not automatic repetition detection.

## Demonstrated checkpoint and tests

The documented command completed successfully and generated all four artifacts:
597 rows, engine frames 0 through 596, 541 valid geometries, 56 missing-landmark
rows with NaN flexion, and recording maximum 118.19774379200672 degrees at frame
260. The source hash matched M5. The earlier implementation checkpoint's saved
figure was visually inspected; the final evidence run reused that committed
implementation without changes or renewed Sports2D inference.
The final checkpoint ran on `feature/m6-end-to-end-pipeline` with a clean working
tree at revision `4cc8cfa32982920f9d3fcb121c6733e041f9c53f`. Its provenance records
that revision and `working_tree_dirty: false`. All four module hashes and the
source, TRC and engine-JSON hashes were verified against the local files, along
with the pinned Sports2D contract and the expected counts/event result.
The full test suite was run once after this final clean checkpoint: **73 passed**.

```powershell
& .\.venv\Scripts\python.exe -m pytest tests\test_angle_pipeline.py -q
& .\.venv\Scripts\python.exe -m pytest -q
```

Focused result: **9 passed**. Full suite: **73 passed** (64 existing + 9 new).
Synthetic tests cover CLI-to-file execution, schema, preserved invalid rows,
known angle, file generation, deterministic ties, all-invalid failure,
source/version/processing/pixel-domain/frame-order mismatches, and overwrite
prevention. No private input is used in automated tests.

Raw video, TRC, CSV, PNG and JSON results remain local under Git-ignored
`data/raw/` and `data/derived/`. Public content contains only code, synthetic
tests and documentation. This is execution/integration evidence, not pose
accuracy, anatomical 3D accuracy, clinical validity or general robustness.
Kinovea, MATLAB, uncertainty propagation, segmentation, filter tuning, new pose
engines and M7 acquisition remain outside M6.
