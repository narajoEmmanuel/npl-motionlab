# Camera and Image Verification, M4

## Status

**M4 is complete under the simplified Core scope adopted on 2026-09-16.**

M4 establishes enough evidence to select one bounded single-camera baseline for
the Core MotionLab experiment. It does not establish a general camera
calibration, universal setup tolerances, or full robustness across camera
positions, devices, lenses, or recording modes.

Historical evidence is preserved in:

- [`baseline_001_readiness.md`](baseline_001_readiness.md)
- [`m4d01_registration.md`](m4d01_registration.md)
- [`m4d01_results.md`](m4d01_results.md)
- the existing M4 scripts and automated tests

## M4 question under the simplified scope

Does the repository contain enough verified image-coordinate behavior and real
acquisition evidence to justify one fixed practical camera setup for the bounded
Core workflow?

For the simplified project, the answer is yes.

## Evidence retained

| Stage | Evidence | Core interpretation |
|---|---|---|
| M4-A | Normalized-to-pixel conversion tests at non-square image sizes | Verified coordinate handling |
| M4-B | Synthetic raster images with known point geometry | Verified image-to-geometry software path |
| M4-C | Real smartphone source inspection and metadata/hashing support | Real acquisition provenance available |
| M4-D | Physical planar-target center-versus-right sequence | Horizontal centering provisionally preferred under tested conditions |

The complete Python suite at the documented M4 checkpoint contained 59 passing
tests. Those tests remain the verification baseline until later development
adds or updates tests.

## Coordinate convention

MotionLab uses continuous pixel coordinates with origin at the decoded image's
top-left, positive `x` to the right, and positive `y` downward.

For decoded width `W` and height `H`, a normalized point `(x_n, y_n)` is mapped
as:

```math
(x_p, y_p) = (W x_n, H y_n)
```

Coordinates are not rounded to array indices and are not silently clipped.

This behavior is retained because an external pose engine may produce
normalized or pixel coordinates, and the adapter must preserve the declared
coordinate domain.

## Existing physical result

The M4-D experiment compared repeated planar-target captures under centered and
right-shifted horizontal placement. The public result record supports a bounded
engineering decision to use **centered horizontal framing** for the Core setup.

This result must not be generalized into a complete lens-distortion model. It
only supports the tested positional choice.

## Simplified Core acquisition baseline

The Core repeated-trial dataset shall keep the following practically consistent
and recorded:

- same smartphone;
- same camera mode/lens used for the chosen baseline;
- same orientation;
- same mounting approach;
- approximately consistent camera height and distance;
- subject approximately sagittal to the camera;
- subject centered horizontally in frame;
- practical consistency of lighting and capture area;
- original source file retained privately;
- source-video identity/checksum and decoded dimensions retained.

The project does not need numerical tolerances for every setup variable before
continuing.

## What is no longer required for Core completion

The following were candidate extensions in the earlier M4 plan but are now
future work rather than blocking requirements:

- systematic yaw experiments;
- systematic pitch experiments;
- systematic roll experiments;
- multiple camera heights;
- multiple camera distances;
- multiple lenses or devices;
- full intrinsic calibration;
- lens-distortion mapping;
- stabilization/HDR factorial studies;
- universal mounting tolerances;
- generalized frame-rate or timing validation beyond what is necessary for the
  selected Core workflow.

If one of these becomes a concrete source of failure during M5 or M6, it may be
investigated narrowly. Otherwise it remains deferred.

## Evidence register

| Evidence ID | Artifact | Result |
|---|---|---|
| M4-A-001 | `src/motionlab/image_geometry.py` | Implemented |
| M4-A-002 | `tests/unit/test_image_geometry.py` | Passed |
| M4-B-001 | `tests/test_synthetic_image_geometry.py` | Passed |
| M4-C-001 | `src/motionlab/video_metadata.py` | Inspector and CLI implemented and tested |
| M4-C-002 | `docs/metrology/acquisition_record_template.yaml` | Retained for source/setup records |
| M4-C-003 | private `baseline_001` source/metadata + public readiness report | Real acquisition evidence retained |
| M4-D-001 | repeated baseline digitizations | Exploratory localization evidence retained |
| M4-D-002 | center/right capture sequence + public results | Centered framing provisionally selected |

## M4 exit condition

M4 is closed because:

- the project-specific image-coordinate mathematics is verified;
- a real smartphone acquisition and provenance path exist;
- physical planar-target evidence exists;
- a practical centered-framing baseline can be selected without claiming
  general camera validity;
- unresolved advanced camera questions are explicitly bounded as future work.

The next milestone is **M5, Sports2D Integration**.
