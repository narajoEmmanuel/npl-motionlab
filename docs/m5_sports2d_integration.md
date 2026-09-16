# M5 Initial Audit and Sports2D Integration

## Status

**M5 COMPLETE.**

This document records the M5 audit performed on 2026-09-16, the resulting
minimal integration design, the representative private-video runtime checkpoint,
and the final pull-request review. All M5 acceptance criteria are satisfied.
The M5 feature branch was merged to `main` through PR #2 at commit `8619356`.
M6 has not started; its M5 prerequisite is satisfied.

## Current MotionLab state

M0 through M4 are complete under the simplified Core scope. MotionLab already
has verified generic 2D included-angle geometry, the project flexion convention,
image-coordinate handling, video metadata inspection, privacy exclusions, and a
bounded centered-camera baseline. M5 does not replace those components.

MotionLab currently requires Python `>=3.13,<3.14`. Sports2D is not and should
not become a direct dependency of the MotionLab package environment.

## Current Sports2D state

The selected stable release is Sports2D `0.8.34`, published 2026-07-10. Its
package metadata supports Python `>=3.11`, uses the BSD 3-Clause license, and
depends on Pose2Sim `>=0.10.49`. Pose2Sim `0.10.49` is pinned with it for the
MotionLab external environment.

Sports2D provides exactly the commodity capability MotionLab needs: single-video
pose estimation, person tracking/selection, named 2D keypoints, and pixel TRC
export. It also implements many features MotionLab does not need for the Core,
including its own angles, coordinate conversion to meters, filtering, plots,
OpenSim-oriented processing, and optional inverse kinematics.

## Compatibility findings

### Python and dependency boundary

Both projects can run on Python 3.13. Direct installation into the MotionLab
environment is rejected because Sports2D brings a larger Pose2Sim and inference
dependency surface. Its processing module also modifies process-wide state. A
subprocess/file boundary is simpler and safer than an in-process Core
dependency.

The representative runtime checkpoint used an isolated Python `3.13.5`
environment created with the standard-library `venv` module and installed with
`pip`. The installed versions were confirmed as Sports2D `0.8.34` and Pose2Sim
`0.10.49`, `pip check` reported no broken dependencies, and importing
`Sports2D.process` succeeded.

### Output format

Sports2D `save_pose=true` writes per-person TRC files in pixel coordinates before
its optional pixel-to-meter conversion. The expected name is:

```text
<video>_Sports2D_px_person00.trc
```

The TRC contains frame, engine-derived time, and named marker X/Y/Z columns.
MotionLab uses X/Y only.

### TRC header unit-label quirk in Sports2D 0.8.34

Sports2D `0.8.34` writes the TRC header field `Units=m` through
`make_trc_with_trc_data` even when that function is used for the pre-conversion
pixel TRC. In the same processing flow, the `_px_` TRC is written before the
optional `to_meters` conversion block.

MotionLab therefore does not infer the coordinate domain from the TRC `Units`
header. For this pinned integration, the coordinate contract is established by:

1. the Sports2D `_px_` output path and processing flow;
2. the explicit MotionLab runner setting `to_meters = false`;
3. preservation of the exported X/Y values without rescaling in the adapter.

This upstream metadata quirk is documented rather than patched or hidden.

### Missing data

Sports2D applies `keypoint_likelihood_threshold` before the export path. Points
below threshold are converted to `NaN`. It can also invalidate a person when too
few acceptable points remain. With interpolation, outlier rejection, and
filtering disabled, missing coordinates are preserved instead of being silently
filled.

The standard pixel TRC does not provide confidence scores as part of the M5 file
contract. MotionLab therefore makes no claim that the adapter consumes raw model
confidence.

### Timing

Sports2D creates its TRC time values from the analyzed frame range and a rounded
FPS value reported by OpenCV. The fields are useful engine provenance, not a
verified timestamp record for arbitrary variable-frame-rate source files.

## Recommended environment boundary

Use an external environment outside the repository, for example:

```text
%USERPROFILE%\.venv\sports2d-motionlab
```

Pin:

```text
sports2d==0.8.34
Pose2Sim==0.10.49
Python 3.13
```

The MotionLab package remains unchanged in `pyproject.toml`.

The standard-library `venv` plus `pip` workflow is the documented baseline
because it was exercised successfully during the runtime checkpoint. `uv` may
be used as an equivalent environment manager, but it is not required by the
Core.

## Selected output contract

```text
private source video
  -> integrations/sports2d/run_sports2d.py
  -> Sports2D *_px_person00.trc
  -> motionlab.sports2d_adapter.read_sports2d_pixel_trc
  -> explicit side landmark mapping
  -> motionlab.geometry.angle_from_points_deg
  -> projected flexion = 180 deg - included angle
```

Sports2D's own knee angle is not the authoritative MotionLab result.

## Selected Sports2D configuration

The M5 runner explicitly overrides the settings that matter to the boundary:

- one detected/selected person;
- noninteractive `highest_likelihood` selection;
- `Body_with_feet` pose model;
- `balanced` mode;
- pixel pose export enabled;
- Sports2D angle calculation disabled;
- conversion to meters disabled;
- C3D/calibration export disabled;
- interpolation disabled;
- outlier rejection disabled;
- trajectory filtering disabled;
- marker augmentation and inverse kinematics disabled;
- real-time display, output video, images, and graphs disabled.

Unspecified Sports2D settings remain the defaults of the pinned `0.8.34`
release. The runner stores the explicit overrides in its provenance JSON.

## Landmark mapping

Sports2D `Body_with_feet` defines the relevant HALPE-style keypoints as:

| MotionLab role | Right-side marker | Sports2D id | Left-side marker | Sports2D id |
|---|---|---:|---|---:|
| proximal / hip | `RHip` | 12 | `LHip` | 11 |
| vertex / knee | `RKnee` | 14 | `LKnee` | 13 |
| distal / ankle | `RAnkle` | 16 | `LAnkle` | 15 |

MotionLab maps by marker name rather than numeric column position. This makes the
file contract easier to inspect and less dependent on column ordering.

## Files added in M5

```text
integrations/sports2d/README.md
integrations/sports2d/requirements.txt
integrations/sports2d/run_sports2d.py
src/motionlab/sports2d_adapter.py
tests/test_sports2d_adapter.py
docs/m5_sports2d_integration.md
```

`.gitignore` is extended so locally generated `data/derived/` engine outputs are
private by default.

No Sports2D dependency is added to MotionLab's `pyproject.toml`.

## Adapter behavior

`read_sports2d_pixel_trc`:

- requires a standard `Frame#` / `Time` marker header;
- maps named marker X/Y/Z groups into explicit columns;
- preserves X/Y values without scaling;
- preserves missing numeric values as `NaN`;
- rejects malformed rows and infinities;
- labels time as `sports2d_time_s` to avoid implying an independently verified
  source timestamp.

`projected_knee_flexion_from_sports2d`:

- requires explicit `right` or `left` landmark mapping;
- preserves the selected hip/knee/ankle pixel coordinates;
- calls the existing verified MotionLab included-angle function;
- reports projected flexion as `180 - included_angle`;
- returns `NaN` and a reason rather than fabricating an angle when a landmark is
  missing or geometry is degenerate.

## Representative private-video runtime checkpoint

The pinned external environment was executed locally on one representative
private video. The raw video, Sports2D TRC, provenance JSON, and checkpoint CSV
remain local and Git-ignored.

Observed results:

| Check | Result |
|---|---|
| Sports2D frames exported | 597 |
| MotionLab frame order | 0 through 596, unique and monotonic |
| Side inspected | right |
| Required markers | `RHip`, `RKnee`, `RAnkle` present in the real TRC contract |
| Valid MotionLab geometry rows | 541 |
| Invalid rows | 56 |
| Invalid reason | `missing_landmark` for all 56 invalid rows |
| Invalid projected-flexion values | `NaN` for all 56 invalid rows |
| Valid projected-flexion values | finite MotionLab-calculated values |
| Sports2D built-in angle used as authority | no |
| Full MotionLab test suite after checkpoint | 64 passed |

The observed 56 invalid rows had missing mapped right-side coordinates. MotionLab
did not replace them with zeroes, interpolation, or fabricated values.

This checkpoint demonstrates that the selected external engine/file boundary and
MotionLab adapter operate together on a real representative video. It does not
validate pose-estimation accuracy, anatomical accuracy, clinical validity, or
general performance.

## Tests added

The M5 adapter tests use a synthetic Sports2D-like TRC and verify:

1. frame order and pixel coordinates are preserved;
2. missing coordinates remain missing;
3. known right-side geometries reach MotionLab's verified angle function;
4. degenerate geometry is not fabricated;
5. left-side mapping is explicit;
6. missing required markers are rejected;
7. malformed TRC headers are rejected.

The adapter test file currently contains five pytest test functions covering the
behaviors above. The representative runtime checkpoint is separate evidence and
does not convert those unit tests into Sports2D inference validation.

## Risks and limitations

- Sports2D is under active development. The Core pins `0.8.34` instead of
  following moving defaults.
- The selected `balanced` RTMPose model may download an external model artifact
  on first use. The current M5 file boundary does not expose a model-file hash.
  This is documented rather than solved with custom download infrastructure.
- Sports2D thresholding occurs before pixel TRC export. The file is therefore a
  minimally processed, thresholded landmark record, not an untouched detector
  tensor.
- Confidence scores are not preserved in the standard pixel TRC contract.
- The Sports2D `0.8.34` TRC writer labels the `Units` header as meters even for
  the pre-conversion pixel TRC, so MotionLab relies on the pinned `_px_` contract
  and processing path rather than that header field.
- Person selection by highest likelihood is appropriate only because the Core
  acquisition is deliberately one-person and controlled.
- Engine-derived TRC time does not replace source timestamp validation.

## Explicit non-goals

M5 does not:

- validate Sports2D pose accuracy;
- compare pose engines;
- enable Sports2D angle outputs as project results;
- tune filters for favorable curves;
- implement camera calibration;
- add Kinovea;
- run MATLAB;
- collect the five-trial Core dataset;
- select the final squat event rule;
- perform M6 analysis.

## Implementation sequence

1. Pin the external engine environment. Complete.
2. Add the isolated Sports2D runner and provenance record. Complete.
3. Add the MotionLab TRC parser and named landmark adapter. Complete.
4. Add synthetic boundary tests. Complete.
5. Run the existing MotionLab test suite. Complete.
6. Install/run the pinned Sports2D environment locally on one representative
   private video. Complete.
7. Ingest its pixel TRC and inspect mapping/missingness. Complete.
8. Complete final documentation and PR review. Complete.
9. Merge the completed M5 feature branch before starting M6. Complete, PR #2.

## M5 acceptance status

| Criterion | Status |
|---|---|
| Sports2D and Pose2Sim versions selected/pinned | Implemented and runtime-confirmed |
| Isolated environment boundary documented | Implemented and runtime-confirmed |
| Explicit `Body_with_feet` hip/knee/ankle mapping | Implemented and runtime-confirmed |
| Pixel TRC parser implemented | Implemented and runtime-confirmed |
| MotionLab angle ownership preserved | Implemented and runtime-confirmed |
| Missing/degenerate landmarks preserved as invalid | Implemented and runtime-confirmed |
| Adapter unit tests | Implemented, 5 passed |
| Representative private-video Sports2D runtime | Observed, 597 frames |
| Real Sports2D pixel TRC ingestion | Observed, 541 valid and 56 missing-landmark rows |
| Full MotionLab regression suite | 64 passed |
| Private raw/derived artifacts excluded from Git | Maintained by `.gitignore` |
| Final PR review | Complete, no M5 blocker found |

M5 is **COMPLETE**. The integration milestone is closed with evidence bounded to
the tested representative workflow. No inference-performance or biomechanical-
validity claim is authorized by this milestone. PR #2 is merged to `main`, so
the prerequisite for starting M6 is satisfied.
