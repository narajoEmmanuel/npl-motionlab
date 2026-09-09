# Camera and Image Verification — M4

## Status and purpose

M4 is in progress. Its purpose is to produce Layer B evidence for the behavior
of image-coordinate conversion and a controlled single-camera acquisition
setup. It does not validate pose landmarks, human biomechanics, or agreement
with the future reference method.

This document is both the M4 execution protocol and its evidence register.
Numerical camera tolerances will not be claimed until they are supported by
recorded physical tests.

Current real evidence: [baseline_001 readiness report](baseline_001_readiness.md).
It records one smartphone acquisition, four manual digitizations of its first
frame, record gaps, and a conditional seven-capture M4-D proposal. The first-
capture checklist below remains the acquisition procedure; its pending states
are updated by the report. M4 is not complete.

The seven-capture proposal was subsequently executed and is reported in
[M4-D horizontal image-position results](m4d01_results.md).

## Questions

1. Does conversion from normalized coordinates to decoded-image pixel
   coordinates preserve known planar angles at non-square aspect ratios?
2. Do encoded files preserve the requested dimensions, orientation, timing,
   and relevant camera settings?
3. How sensitive is a known planar angle to feasible camera yaw, pitch, roll,
   height, distance, crop, digital zoom, and stabilization settings?
4. Which controllable acquisition configuration should become the provisional
   baseline for the M9 pilot and the M10 protocol freeze?

## Evidence stages

| Stage | Evidence | Current state |
|---|---|---|
| M4-A | Analytical normalized-to-pixel conversion at multiple aspect ratios | Verified by automated tests |
| M4-B | Synthetic raster images with known point geometry | Verified by lossless encode/decode tests |
| M4-C | Device and encoded-video metadata inspection | baseline_001 decoded and source/frame checked; acquisition-record gaps remain |
| M4-D | Physical planar-target camera trials | Center/right sequence analyzed; other camera effects and setup tolerances unresolved |
| M4-E | Provisional baseline and empirically justified setup tolerances | Horizontal centering provisionally preferred; complete baseline and tolerances pending |

## Coordinate convention

MotionLab uses continuous pixel coordinates with origin at the decoded image's
top-left, positive `x` to the right, and positive `y` downward. For decoded
width `W` and height `H`, a normalized point `(x_n, y_n)` is converted by

```math
(x_p, y_p) = (W x_n, H y_n).
```

The values are not rounded to array indices. Values outside `[0, 1]` are not
silently clipped because an off-image pose landmark is raw information that
must remain available for later quality handling. Any pose engine whose
normalization convention differs from this equation must have an explicit
adapter and test in M5.

The automated M4-A evidence includes a 60° construction in a 1920 × 1080 image.
It verifies that pixel conversion recovers the known angle and that computing
directly in anisotropically scaled normalized coordinates produces a material
error. This is verification evidence for ML-MOD-002, not camera validity.

## Provisional acquisition controls to inspect

The following fields must be recorded before a camera configuration can become
the baseline:

- device manufacturer, model, operating-system version, and camera app;
- selected and decoded width and height;
- display and encoded orientation, including rotation metadata;
- nominal and measured frame-rate behavior and timestamps where accessible;
- selected lens, digital zoom, stabilization, and HDR state;
- focus, exposure, white-balance, and frame-rate locking capability;
- camera support, height, distance, yaw, pitch, and roll;
- subject-to-camera orientation, capture region, lighting, and calibration
  target placement;
- original filename, capture time, file size, and cryptographic checksum.

Controls are recorded even when the device does not expose or permit a setting.
An unknown value is reported as unknown, not inferred from appearance.

Use the draft [acquisition record template](acquisition_record_template.yaml)
for the manually observed device and setup fields. Inspect the encoded file
without altering it by running:

```powershell
.\.venv\Scripts\python.exe -m motionlab.video_metadata <video> --output <metadata.json>
```

The inspector records the SHA-256 checksum, file size, decoded dimensions,
reported frame count and nominal FPS, derived duration, codec, decoding
backend, and backend-reported orientation. Decoded frame dimensions are used
because they are the coordinate domain seen by downstream geometry. Header FPS
and frame count do not establish constant frame rate or timestamp integrity.
Likewise, a backend orientation value of zero can mean either zero rotation or
missing metadata, so the asymmetric-target check remains mandatory.

## Physical verification design

### First representative acquisition: baseline_001

This is a readiness capture, not a completed camera validation. Use three
high-contrast centers A, B, C on a rigid planar target, with B the vertex.
The initial design is a nominal 3-4-5 triangle: BA = 300 mm, BC = 400 mm,
AC = 500 mm, nominal angle ABC = 90 degrees (or a documented common scale).
Record nominal dimensions separately from actual center-to-center measurements.
Construction error and physical measurement uncertainty remain unquantified
unless supported by evidence; nominal 90 degrees is not an error-free reference.
Include a separate asymmetric mark and an identifiable target outline so that
rotation, mirroring, and cropping can be checked against the physical layout.

The acquisition YAML already covers the first capture's device and setup.
Its only added field is `physical_setup.target_record_path`: a private companion
record is necessary to identify the physical geometry behind the comparison.
Use existing `notes` for setup measurement methods, room constraints, image-field
position, and setting controllability; no further structured fields are needed.
Set `observed_file_metadata` to the relative path of the inspector JSON.

After baseline_001, provide the following locally, under the Git-ignored
`data/raw/m4/` directory (including private metadata and supporting images):

1. Exact path and original filename of the unedited smartphone video. Preserve
   the original bytes; describe the transfer method and any known processing.
2. Completed `baseline_001_acquisition.yaml`, with condition ID `baseline_001`,
   capture date/time including UTC offset, operator ID, device/app versions,
   requested resolution/FPS/orientation, lens, zoom, stabilization, HDR, focus,
   exposure, and white balance. Use null plus an explanation for unknown values.
3. `baseline_001_metadata.json` from the existing inspector, containing the
   source checksum and decoded dimensions. Use a new output filename, never the
   source-video path or an existing evidence file: the current CLI overwrites
   its output destination. If decoding fails, provide the error and source path.
4. The linked target record: target ID, material/flatness description, center
   shapes and sizes, labeled layout/photo of A/B/C and the asymmetric mark,
   nominal BA/BC/AC and angle ABC, actual measured center-to-center distances,
   instrument and measurement method, and any construction/measurement limits.
   A direct physical angle measurement is optional; distinguish it from the
   nominal value. Do not invent uncertainty values.
5. Setup observations in YAML notes: support, room and available movement space,
   camera-to-target relationship, height/distance measurement endpoints and
   methods, yaw/pitch/roll conventions and how assessed, lighting, target
   position within the image, and which settings can be locked or controlled.
   Describe unknown geometry rather than assuming zero angles.
6. A description of the interval where the target and camera were stationary,
   with all centers, the asymmetric mark, and outline visible; note blur, glare,
   occlusion, focus changes, or accidental movement. A rough playback time is a
   navigation aid, not a verified timestamp.

For the capture, secure the target and phone, aim approximately normal to the
target plane, keep the complete target visible, and record a stationary interval
with clearly distinguishable centers. Record the actual setup. No numerical
factor levels, repetition count, or final acceptance threshold is required to
make this first representative capture.

### Evidence chain and proposed localization

| Link | Required evidence and current boundary |
|---|---|
| Physical target → original video | baseline_001 source checksum checked; user-reported ruler dimensions available; target companion record missing |
| Original video → decoded image | Retain a lossless full-frame derivative with source checksum, zero-based sequential frame index, decoded dimensions, OpenCV version/backend, and actual orientation handling; current inspector reads only the first frame and does not export it |
| Decoded image → target point localization | baseline_001 has four manual A/B/C coordinate records; exploratory sensitivity only, full localization characterization pending |
| Localization → pixel coordinates | Retain each raw A/B/C (x, y) in the original decoded-image coordinate system, operator, tool/version, and selection notes; map display zoom back to original pixels |
| Pixel coordinates → measured planar angle | Use existing `angle_from_points_deg(A, B, C)` with B as vertex; inputs already in pixels need no normalized conversion |
| Measured angle → nominal comparison | Report signed difference measured ABC minus nominal ABC (90 degrees for this design); it combines construction, projection, optics, and localization effects and does not isolate camera error |

The smallest proposed first method is manual center digitization on a lossless
decoded still, with zoom for inspection and a saved coordinate/overlay record.
Define the center as the visually estimated geometric center of each marker's
boundary; flag ambiguous, clipped, or obscured markers rather than guessing.
Select the first sequentially decoded frame in the documented stationary
interval with all required features clear, before calculating its angle. Record
the rule, index, and reasons for rejected frames; never select by closeness to
90 degrees. Repeat digitization of the same frame without showing earlier picks
to assess operator sensitivity before treating localization as characterized.
Any spread is exploratory digitization evidence, not total camera uncertainty.

The baseline_001 report documents the existing user-created manual picker and
its limitations; no additional localization infrastructure is required here.
The synthetic exact-intensity centroid helper is test-only; it has not been
shown to work on compressed smartphone imagery. No automatic segmentation,
human pose estimation, or M5 work is introduced here.

Frame index is not physical time. Reported FPS/count and their duration ratio
do not establish CFR/VFR, dropped frames, or timestamp integrity. Preserve these
limitations during the static-angle analysis. Consider another decoder or
metadata dependency only if the real file exposes an OpenCV limitation that
prevents a specific M4 decision.

### Later physical experiments

Use a rigid planar target with at least three high-contrast point centers whose
included angle and relevant distances are independently specified. Preserve the
original video. For every condition, extract the same predefined target pose or
frame-selection rule and record both the requested camera settings and decoded
file properties.

The following are candidate follow-up experiments, not a requirement to run
every factor now. The bounded first sequence is specified in the baseline_001
report and awaits the missing setup feasibility information:

1. repeated baseline recordings without moving the target or camera;
2. one-factor changes in yaw, pitch, roll, height, distance, and image-field
   position (lens distortion may vary between image center and edges);
3. each available lens, zoom, stabilization, and resolution/frame-rate mode;
4. orientation and crop checks using an asymmetric target;
5. a return-to-baseline recording after the perturbations.

Define factor levels and repetitions only after the actual device, room,
target, support, baseline geometry, and controllability are known, and before
viewing the corresponding experimental errors. Image-field position is a
candidate factor only; no numerical levels are set. Setup tolerances require
evidence, and final engineering acceptance thresholds are not defined here.

## Acceptance conditions

M4 can be marked complete only when:

- automated coordinate and image tests pass and link to ML-MOD-002;
- at least one representative encoded video has a retained metadata record;
- the physical target, measurement method, factor levels, and repetitions are
  documented;
- baseline repeatability and each tested camera factor are reported without
  extending conclusions beyond tested conditions;
- a provisional M9 acquisition baseline and setup tolerances are justified by
  M4 evidence, with unresolved optics or timing limitations stated;
- ML-CAM-001 has explicit evidence and all earlier automated tests still pass.

## Evidence register

| Evidence ID | Artifact | Requirements | Result |
|---|---|---|---|
| M4-A-001 | `src/motionlab/image_geometry.py` | ML-MOD-002, ML-SW-001 | Implemented |
| M4-A-002 | `tests/unit/test_image_geometry.py` | ML-MOD-002, ML-REP-002 | Passed |
| M4-B-001 | `tests/test_synthetic_image_geometry.py` | ML-MOD-002, ML-REP-002 | Passed at M4 start: 49 tests total |
| M4-C-001 | `src/motionlab/video_metadata.py` | ML-CAM-001, ML-SW-001 | Inspector and CLI passed with generated video: 59 tests total |
| M4-C-002 | `docs/metrology/acquisition_record_template.yaml` | ML-CAM-001 | Draft template implemented |
| M4-C-003 | baseline_001 private source/metadata; public readiness report | ML-CAM-001 | Source and first-frame identity checked; requested settings/record structure incomplete |
| M4-D-001 | baseline_001 private coordinates; public readiness report | Camera Layer B | Four same-frame picks recalculated; exploratory manual sensitivity only |
| M4-D-002 | Seven-capture private records; public results report | Camera Layer B | Center/right sequence complete; horizontal centering provisionally preferred within tested conditions |
