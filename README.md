# NPL MotionLab

Markerless biomechanics measurement, validation, and engineering practice lab.

MotionLab is organized around a measurement system for estimating a narrowly
defined 2D projected sagittal-plane knee flexion angle from standardized
single-camera video. **M0: Environment & Repository**, **M1: Charter, Scope &
Requirements**, **M2: Literature & Measurement Framework**, and **M3:
Mathematical Verification** are complete. **M4: Camera & Image Verification**
is in progress. **M4-E: MATLAB Measurement Modeling and Cross-Verification** is
an in-progress M4 submilestone that adds an independent analytical layer without
replacing the Python pipeline.

## Project definition

- [Project charter](docs/project_charter.md)
- [Engineering requirements](docs/requirements.md)
- [Controlled terminology](docs/terminology.md)
- [Targeted literature review](docs/literature_review.md)
- [Measurement framework](docs/metrology/measurement_framework.md)
- [Mathematical measurement model](docs/metrology/measurement_model.md)
- [M4 camera and image verification](docs/metrology/camera_image_verification.md)
- [M4-E MATLAB modeling and cross-verification](docs/metrology/m4e_matlab_modeling.md)
- [M4 execution and handoff guide (Spanish)](docs/metrology/m4_handoff_guide_es.md)
- [Literature matrix](references/literature_matrix.csv)
- [Bibliography](references/references.bib)

## Python and MATLAB roles

Python remains the primary implementation for the MotionLab software pipeline,
image geometry, video inspection, analysis scripts, and automated pytest
verification. MATLAB is a secondary analytical environment used for independent
mathematical verification, deterministic measurement modeling, landmark
perturbation simulation, sensitivity analysis, replay of existing M4-D
descriptive analysis, technical visualization, and Python-MATLAB numerical
cross-verification. See [matlab/README.md](matlab/README.md).

The MATLAB layer does not introduce pose estimation and does not establish
biomechanical, clinical, diagnostic, participant-validation, completed
uncertainty, or professional-motion-capture-equivalence claims.

## Engineering Foundations

The [MotionLab Engineering Foundations](docs/foundations/README.md) knowledge
base explains the mathematical, numerical, programming, and software-
engineering concepts verified through M3. It links each concept to the current
implementation and evidence without extending claims into camera,
biomechanical, or experimental validity.

## Environment

The initial development environment uses Python 3.13 and is defined by
`pyproject.toml`. Create and install it in PowerShell with:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install ".[dev]"
```

`pyproject.toml` is the authoritative declaration of direct dependencies.
`requirements-lock.txt` records the complete resolved environment used at the
M0 checkpoint. To reproduce that exact environment instead, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Verify the Python environment with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

MATLAB is intentionally kept outside Python dependency management. The M4-E
implementation is designed for base MATLAB, with the exact MATLAB release to be
recorded when verification outputs are executed and retained.

No biomechanics, pose-estimation, clinical, or confirmatory human-performance
claims have been implemented or validated at this stage.
