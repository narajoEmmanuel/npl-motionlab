# Camera and Image Verification — M4

## Status and purpose

M4 is in progress. Its purpose is to produce Layer B evidence for the behavior
of image-coordinate conversion and a controlled single-camera acquisition
setup. It does not validate pose landmarks, human biomechanics, or agreement
with the future reference method.

This document is both the M4 execution protocol and its evidence register.
Numerical camera tolerances will not be claimed until they are supported by
recorded physical tests.

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
| M4-C | Device and encoded-video metadata inspection | Planned; requires representative source files |
| M4-D | Physical planar-target camera trials | Planned; requires target and device |
| M4-E | Provisional baseline and empirically justified setup tolerances | Blocked until M4-C and M4-D evidence exists |

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

## Physical verification design

Use a rigid planar target with at least three high-contrast point centers whose
included angle and relevant distances are independently specified. Preserve the
original video. For every condition, extract the same predefined target pose or
frame-selection rule and record both the requested camera settings and decoded
file properties.

The first controlled sequence should contain:

1. repeated baseline recordings without moving the target or camera;
2. one-factor changes in yaw, pitch, roll, height, and distance;
3. each available lens, zoom, stabilization, and resolution/frame-rate mode;
4. orientation and crop checks using an asymmetric target;
5. a return-to-baseline recording after the perturbations.

Factor levels, repetition count, and allowable tolerances must be entered
before viewing outcome errors. They depend on the available tripod, target,
room, and smartphone and therefore are not invented in this initial commit.

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
| M4-C-001 | Representative device/video metadata record | ML-CAM-001 | Pending |
| M4-D-001 | Physical planar-target dataset and report | Camera Layer B | Pending |
