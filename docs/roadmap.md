# MotionLab Simplified Core Roadmap

## Current direction

MotionLab is a small measurement-engineering project built around a controlled
single-camera 2D squat workflow. It reuses mature pose-estimation software and
keeps only the project-specific responsibilities that add value:

1. preserve source-video provenance and configuration;
2. obtain hip, knee, and ankle landmarks from a pinned Sports2D workflow;
3. compute the project-defined 2D projected knee flexion angle with verified
   MotionLab geometry;
4. run a small repeated-trial experiment under one fixed acquisition setup;
5. summarize observed computational and within-protocol behavior;
6. publish a bounded engineering conclusion and reproducible release.

The Core project does not need to develop pose estimation, tracking, filtering
frameworks, camera-calibration software, a manual-reference system, a full
uncertainty budget, Monte Carlo propagation, or a robustness matrix.

## Core architecture

```text
original smartphone video
        |
        v
MotionLab source hash + metadata
        |
        v
Sports2D / RTMPose
        |
        v
pixel hip / knee / ankle landmarks
        |
        v
MotionLab verified geometry
        |
        v
2D projected knee-flexion time series
        |
        v
small controlled repeated-trial analysis
        |
        v
bounded engineering conclusion
```

Sports2D is a replaceable external pose engine. MotionLab does not need to
reimplement its detector, tracker, visualization, interpolation, filtering, or
video-processing stack.

## Milestones

| Milestone | Scope | Exit condition | Status |
|---|---|---|---|
| M0 | Environment and repository | Reproducible Python project and tests | Complete |
| M1 | Charter and requirements | Bounded 2D measurand and scope | Complete |
| M2 | Literature and measurement framework | Evidence boundaries documented | Complete |
| M3 | Mathematical verification | Known-angle geometry and edge cases verified | Complete |
| M4 | Controlled camera and image baseline | Pixel conversion verified, one real acquisition characterized, M4-D supports centered framing under tested conditions | Complete under simplified scope |
| M5 | Sports2D integration | Pinned engine/configuration produces traceable pixel landmarks that MotionLab can ingest | Complete |
| M6 | End-to-end angle pipeline | One representative video runs from source metadata to MotionLab angle time series and summary without manual coordinate entry | Complete locally |
| M7 | Small controlled squat dataset | Five independent one-squat video trials collected under the fixed baseline and processed reproducibly | Planned |
| M8 | Final Core analysis | Per-trial outputs and simple descriptive summaries generated with explicit limitations | Planned |
| M9 | Technical conclusion and release | Short report, reproducible public artifacts, README and tagged release completed | Planned |

Milestones after M4 are intentionally small. New work must demonstrate that it
changes the final Core conclusion before it is made mandatory.

## M5 completion evidence

The representative private-video runtime check was completed with the pinned
Sports2D `0.8.34` / Pose2Sim `0.10.49` environment.

Observed integration evidence:

- 597 frames exported by Sports2D;
- the real `_px_person00.trc` was consumed by MotionLab;
- `RHip`, `RKnee`, and `RAnkle` mapping was confirmed on the real boundary;
- 541 frames produced valid MotionLab geometry;
- 56 frames remained invalid as `missing_landmark` with `NaN` projected flexion;
- the full MotionLab test suite passed, `64 passed`.

This is integration evidence, not pose-accuracy or biomechanical-validity
evidence. M5 is complete and its feature branch is merged to `main`, satisfying
the prerequisite for the subsequent M6 implementation.

## M4 closure decision

M4 is considered complete for the simplified Core because the repository
already contains:

- analytical and automated image-coordinate verification;
- synthetic raster verification;
- source-video metadata and hashing support;
- a real smartphone acquisition record;
- repeated manual digitization evidence for the planar target;
- the M4-D center-versus-right experiment;
- a provisional decision to keep the subject/target horizontally centered
  under the tested setup.

This does not establish a general camera calibration. Lens maps, arbitrary yaw,
pitch, roll, camera height, distance, multiple devices, and universal setup
tolerances are outside the Core.

## M5 minimum deliverable

Use a pinned stable Sports2D release and explicit configuration. The initial
integration should prefer raw pixel landmarks and avoid optional processing
unless a concrete problem requires it.

The adapter only needs to prove:

- which pose model and Sports2D version produced the landmarks;
- how hip, knee, and ankle columns map to MotionLab landmark roles;
- that pixel coordinates are retained without silent rescaling;
- that frame/order provenance remains linkable to the source video;
- that missing or invalid landmarks are not silently fabricated;
- that MotionLab, not Sports2D, computes the authoritative project angle.

No second pose engine is required.

## M6 minimum deliverable

The exit condition was demonstrated locally on 2026-09-16: the documented
command reused the M5 TRC, preserved 597 rows (541 valid, 56 missing), generated
CSV/figure/summary/provenance, and passed 73 tests.
See [M6 evidence and reproduction](m6_angle_pipeline.md). The selected rule is
maximum valid projected flexion across the recording, resolving exact ties by
lowest engine frame. Multiple flexion episodes in the representative recording
support a recording maximum, not automatic repetition segmentation. M7 remains
planned.

One command or clearly documented sequence shall:

1. inspect/hash the original video;
2. run or consume the pinned Sports2D output;
3. ingest pixel landmarks;
4. calculate MotionLab projected knee flexion;
5. write a compact machine-readable result;
6. generate one technical angle-versus-frame/time figure.

A one-video smoke test belongs inside M6. It is not a separate pilot milestone.

## M7 minimum experiment

The default Core dataset is five independent video trials, one controlled
bodyweight squat per video, using the same phone, camera mode, orientation,
mounting approach, approximate distance, centered framing, lighting setup, and
movement instructions.

The purpose is not population inference and not clinical validation. The dataset
exists only to demonstrate repeatable operation and describe observed variation
under one bounded setup.

The exact event-summary rule will be frozen in M6 before processing the five
Core trials. It should be the simplest rule that remains stable on the
representative video.

## M8 minimum analysis

Keep the analysis descriptive. At minimum report:

- one result per independent trial for the predefined squat event;
- mean, standard deviation, minimum, maximum, and range across trials;
- missing-landmark or pipeline-failure count;
- one representative full angle time series;
- configuration and software/model versions;
- limitations that prevent accuracy, clinical, 3D, or population claims.

Do not add inferential statistics, ICC, ANOVA, Bland-Altman analysis, confidence
interval machinery, or uncertainty propagation unless a later optional
reference experiment creates a specific need.

## M9 completion package

The Core project is finished when the repository contains:

- the pinned Sports2D integration/configuration;
- the MotionLab adapter and tested angle pipeline;
- traceable derived results from the five controlled trials (raw identifiable
  video remains private by default);
- a concise technical report;
- one reproducible results command or documented workflow;
- a release with evidence-bounded claims.

A valid final conclusion can be positive, limited, or negative. Completion does
not depend on achieving a target angle value or proving agreement with another
system.

## Optional work, explicitly outside the critical path

### Optional A, Kinovea manual reference

Kinovea may be used after the Core is complete if an independent manual
comparison would materially improve the final portfolio or technical report.
This is not required for M5 through M9.

If performed, use only a small predefined subset of Core trials, preserve the
manual procedure and software version, and report paired differences without
calling Kinovea ground truth.

### Optional B, Advanced MATLAB Verification Appendix

The existing `feature/m4e-matlab-verification` work remains a separate optional
advanced appendix. It may demonstrate an independent implementation of the
angle geometry, analytical cases, deterministic sensitivity, and Python to
MATLAB numerical consistency.

MATLAB completion, MATLAB runtime evidence, and MATLAB figures are not required
to complete the Core project.

### Future work

The following are deferred until a specific future question requires them:

- full intrinsic/lens camera calibration;
- multiple camera positions or devices;
- robustness matrices;
- multiple pose engines;
- multiple participants or population inference;
- manual-reference validation beyond the optional Kinovea appendix;
- full GUM-style uncertainty budgets;
- Monte Carlo uncertainty propagation;
- advanced filtering comparisons;
- 3D reconstruction, OpenSim, inverse kinematics, or multi-camera systems;
- clinical, diagnostic, injury-risk, or rehabilitation applications;
- accreditation and teaching-module expansion.

## Scope-control rule

A proposed new task enters the Core only when all three conditions are true:

1. it is necessary to run the end-to-end workflow or interpret the bounded
   result;
2. an existing mature tool cannot reasonably supply the capability;
3. omitting it would materially weaken the final Core conclusion.

Otherwise it remains optional or future work.
