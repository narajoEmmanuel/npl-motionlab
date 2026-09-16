# NPL MotionLab

MotionLab is a compact measurement-engineering project for estimating a
**2D projected sagittal-plane knee flexion angle** from controlled single-camera
smartphone video.

The project deliberately reuses mature open-source pose-estimation software
instead of rebuilding pose detection, tracking, filtering, or camera-calibration
infrastructure from scratch. MotionLab keeps the project-specific pieces that
matter for engineering traceability: source provenance, verified angle geometry,
landmark adaptation, controlled acquisition, repeatable processing, and bounded
interpretation.

## Current scope

The Core workflow is:

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

**M0: Environment & Repository**, **M1: Charter & Requirements**, **M2:
Literature & Measurement Framework**, **M3: Mathematical Verification**, and
**M4: Controlled Camera & Image Baseline** are complete under the simplified
Core scope.

**M5: Sports2D Integration** is the next milestone.

The complete current plan is in the [simplified Core roadmap](docs/roadmap.md).

## Core completion path

1. integrate one pinned Sports2D/RTMPose workflow;
2. ingest pixel hip, knee, and ankle landmarks;
3. compute the authoritative MotionLab angle using the already verified geometry;
4. demonstrate the complete workflow on one representative video;
5. collect and process five controlled one-squat video trials;
6. report simple descriptive results, failures, configuration, and limitations;
7. publish a concise technical conclusion and reproducible release.

No second pose engine, manual reference, full uncertainty budget, Monte Carlo
study, robustness matrix, or generalized camera calibration is required to
finish the Core.

## Optional work

### Kinovea reference appendix

An independent Kinovea manual-reference comparison may be added **after the Core
is complete** if it materially improves the technical report. It is not a Core
milestone and does not block project completion.

### Optional Advanced MATLAB Verification Appendix

The MATLAB work remains an optional advanced verification appendix. It may be
used to demonstrate independent angle implementation, analytical verification,
deterministic sensitivity, and Python-to-MATLAB consistency. MATLAB execution
is not required for the Core release.

## Project definition

- [Simplified Core roadmap](docs/roadmap.md)
- [Project charter](docs/project_charter.md)
- [Engineering requirements](docs/requirements.md)
- [Controlled terminology](docs/terminology.md)
- [Targeted literature review](docs/literature_review.md)
- [Measurement framework](docs/metrology/measurement_framework.md)
- [M4 camera and image evidence](docs/metrology/camera_image_verification.md)
- [M4-D results](docs/metrology/m4d01_results.md)
- [Reuse-versus-build architecture](docs/decisions/ADR-0002-reuse-vs-build-architecture.md)
- [Simplified Core scope decision](docs/decisions/ADR-0003-simplified-core-scope.md)
- [Literature matrix](references/literature_matrix.csv)
- [Bibliography](references/references.bib)

## Engineering Foundations

The [MotionLab Engineering Foundations](docs/foundations/README.md) knowledge
base explains the mathematical, numerical, programming, and software-engineering
concepts verified through M3. These foundations remain valid and are retained.

## Environment

The current development environment uses Python 3.13 and is defined by
`pyproject.toml`.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

`pyproject.toml` remains the authoritative declaration of direct MotionLab
dependencies. External pose-engine dependencies may be isolated and pinned when
M5 is implemented so they do not destabilize the small verified Core package.

## Claim boundary

MotionLab does not claim clinical validity, diagnostic capability, anatomical
3D knee kinematics, equivalence to professional marker-based motion capture, or
population-level performance. The final Core conclusion will apply only to the
explicitly tested single-camera workflow and conditions.
