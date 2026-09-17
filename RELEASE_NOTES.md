# NPL MotionLab v0.1.0

## First bounded Core release

NPL MotionLab v0.1.0 packages the completed simplified Core workflow for
estimating a **2D projected sagittal-plane knee flexion angle** from controlled
single-camera smartphone video.

This release is a measurement-engineering and experimental-engineering artifact.
It emphasizes traceability, explicit scope, verified project-specific geometry,
controlled acquisition, reproducible processing, and evidence-bounded
interpretation.

## What is included

- verified 2D hip-knee-ankle angle geometry and image-coordinate handling;
- source-video metadata inspection and SHA-256 provenance;
- controlled camera/image baseline documentation;
- pinned external Sports2D `0.8.34` / Pose2Sim `0.10.49` integration;
- isolated Sports2D file boundary with named pixel-landmark mapping;
- MotionLab-owned projected-flexion calculation;
- explicit missing/degenerate landmark handling without fabricated angles;
- end-to-end source-to-result pipeline with CSV, technical figure, summary, and
  provenance outputs;
- deterministic event rule
  `maximum_valid_projected_flexion_first_frame_v1`;
- five independent controlled one-squat trial workflow;
- reproducible descriptive analysis of the frozen trial event summaries;
- synthetic and regression tests covering the public computational contracts;
- final bounded technical conclusion in `docs/m9_core_release.md`.

## Verification state

The final M8 checkpoint passed the full MotionLab suite with **86 tests**. M9
adds release documentation and version alignment only; it does not change the
frozen M5-M8 processing contracts.

The real-video and five-trial checkpoints remain private because they contain
human source/derived data. The public repository contains the implementation,
contracts, synthetic tests, and documentation needed to inspect the released
workflow.

## Claim boundary

v0.1.0 demonstrates traceable computational execution of the tested controlled
single-camera workflow. It does **not** establish:

- pose-estimation accuracy against ground truth;
- anatomical 3D knee-angle accuracy;
- clinical validity or diagnostic capability;
- squat quality, injury-risk, or athlete-performance assessment;
- population-level performance;
- general reliability across devices, participants, camera positions, or
  environments;
- equivalence to professional marker-based motion capture.

The primary measurand is an image-plane projected angle. External pose-engine
outputs are treated as inputs to MotionLab, not as unquestioned truth.

## Reproduction

Create the MotionLab environment and run the public test suite:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Sports2D is intentionally installed in a separate pinned environment; see
`integrations/sports2d/README.md`.

The real human-video checkpoints cannot be reproduced from a public checkout
without the corresponding private source recordings and derived engine outputs.

## Documentation

Start with:

- `README.md`
- `docs/project_charter.md`
- `docs/roadmap.md`
- `docs/m5_sports2d_integration.md`
- `docs/m6_angle_pipeline.md`
- `docs/m7_controlled_squat_dataset.md`
- `docs/m8_final_core_analysis.md`
- `docs/m9_core_release.md`

## Deferred work

Kinovea comparison, MATLAB cross-verification, multiple pose engines, formal
uncertainty propagation, generalized camera calibration, robustness matrices,
3D reconstruction, and population-scale studies are outside the v0.1.0 Core.
They should be added only in response to a specific future engineering question.
