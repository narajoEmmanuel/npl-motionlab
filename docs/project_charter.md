# Project Charter

## Document control

| Field | Value |
|---|---|
| Project | NPL MotionLab |
| Status | Simplified Core baseline |
| Owner | Emmanuel Naranjo Blanco |
| Last updated | 2026-09-16 |

## Objective

Build and characterize a reproducible engineering workflow that estimates a
**2D projected sagittal-plane knee flexion angle** from controlled single-camera
smartphone video during a bodyweight squat.

The project reuses one mature external pose-estimation workflow for landmark
localization and retains MotionLab-specific responsibilities for provenance,
landmark adaptation, verified geometry, controlled acquisition, repeatable
processing, and bounded interpretation.

## Engineering question

Can a small, explicitly versioned single-camera workflow reproducibly transform
controlled squat video into traceable 2D projected knee-flexion results using
external pose landmarks and independently verified MotionLab geometry?

The Core project is not designed to prove clinical validity, population-level
accuracy, or equivalence to professional motion-capture systems.

## Intended use

MotionLab is intended as a compact engineering and portfolio project that
demonstrates:

- reuse of mature technical tools instead of unnecessary reimplementation;
- mathematical and software verification of the project-specific angle layer;
- reproducible source-to-result traceability;
- controlled experimental execution;
- evidence-bounded engineering conclusions.

## Primary measurand

The primary measurand is the **2D projected sagittal-plane knee flexion angle**
derived from projected hip, knee, and ankle landmark roles in the image plane.

The project convention assigns 0° to projected full extension and increasing
positive values to projected flexion. The underlying generic included-angle
geometry is already analytically verified and unit-tested in M3.

This is an image-plane measurand. It is not a full anatomical three-dimensional
knee joint angle.

## Core system boundary

The simplified Core begins with an original smartphone video and ends with
traceable project results and a bounded engineering conclusion.

```text
source video
→ source hash and metadata
→ Sports2D / RTMPose landmark generation
→ explicit hip/knee/ankle adapter
→ MotionLab verified angle geometry
→ compact result and technical figure
→ repeated-trial descriptive analysis
→ bounded conclusion
```

Sports2D is a replaceable external pose-engine component. MotionLab does not
reimplement pose detection, tracking, model inference, generalized filtering,
or camera-calibration infrastructure.

## In scope

- one principal 2D projected knee-flexion measurand;
- standardized single-camera smartphone video;
- controlled bodyweight squats;
- source-video hashing and metadata inspection;
- one pinned Sports2D/RTMPose workflow;
- explicit mapping of external pixel landmarks to MotionLab landmark roles;
- MotionLab angle computation using the verified project convention;
- one end-to-end representative-video demonstration;
- a small Core dataset of five independent one-squat video trials;
- simple descriptive summaries and failure counts;
- reproducible configuration and software/model version records;
- a concise technical report and public release with bounded claims.

## Out of scope for the Core

- clinical, diagnostic, injury-risk, or rehabilitation use;
- claims of anatomical 3D joint-angle measurement;
- equivalence to Vicon or professional marker-based motion capture;
- population-level, athlete-performance, or multi-participant claims;
- multiple pose-engine benchmarking;
- generalized intrinsic or lens calibration;
- full yaw, pitch, roll, height, distance, or device robustness matrices;
- mandatory manual reference validation;
- full GUM-style uncertainty budgets;
- Monte Carlo uncertainty propagation;
- 3D reconstruction, multi-camera workflows, OpenSim, or inverse kinematics;
- unnecessary cloud, database, ML-training, or distributed infrastructure.

## Optional work after Core completion

### Kinovea manual reference appendix

A small independent Kinovea comparison may be added after the Core is finished
if it materially improves the technical report. It is not required for Core
completion and must not be described as ground truth.

### Optional Advanced MATLAB Verification Appendix

MATLAB may be used as an independent secondary verification layer for angle
geometry, analytical cases, deterministic sensitivity, experimental-analysis
replay, and Python-to-MATLAB numerical consistency. MATLAB runtime completion is
not required for the Core release.

## Evidence architecture

The simplified project uses three evidence layers:

1. **Analytical/software evidence:** known geometries, edge cases, unit tests,
   coordinate conversion, and numerical implementation.
2. **Controlled workflow evidence:** one fixed camera baseline, explicit
   software/model configuration, traceable video-to-landmark-to-angle processing.
3. **Repeated-trial evidence:** a small set of independent controlled squat
   videos used to describe observed within-protocol behavior.

An optional Kinovea appendix may later add an independent comparison layer, but
that layer is not part of the Core acceptance path.

## M4 closure under simplified scope

M4 is complete for the Core because the repository already contains:

- automated normalized-to-pixel and image-geometry verification;
- synthetic image tests;
- video metadata and source-hashing support;
- a real smartphone acquisition;
- repeated planar-target digitization evidence;
- the M4-D center-versus-right experiment;
- a provisional choice to use centered horizontal framing under the tested
  setup.

This closure does not establish a general camera calibration or universal setup
tolerances.

## Core completion criterion

The Core is complete when:

- a pinned Sports2D workflow produces traceable pixel landmarks;
- MotionLab ingests those landmarks and computes its own projected knee angle;
- one representative video demonstrates the complete pipeline;
- five independent controlled squat videos are processed with the frozen Core
  configuration;
- compact descriptive results and failures are reported;
- limitations and claim boundaries are explicit;
- a short technical report and reproducible repository release are published.

Completion does not require a favorable performance result.

## Governing principles

- reuse mature tools when they already solve the non-project-specific problem;
- keep MotionLab small and testable;
- preserve raw/source provenance and derived-output traceability;
- external engine outputs are inputs, not unquestioned truth;
- MotionLab owns its angle convention and project interpretation;
- independent trials, not frame count, support repeated-trial summaries;
- optional work must not silently become a blocking Core requirement;
- negative or limited results are acceptable;
- public claims must not exceed the evidence actually produced.

## Scope-control rule

A proposed task enters the Core only if it is necessary to run or interpret the
end-to-end workflow, cannot reasonably be supplied by an existing mature tool,
and materially affects the final bounded conclusion.

Otherwise it is optional or future work.
