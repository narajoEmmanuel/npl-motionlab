# NPL MotionLab

Markerless biomechanics measurement, validation, and engineering practice lab.

MotionLab is organized around a measurement system for estimating a narrowly
defined 2D projected sagittal-plane knee flexion angle from standardized
single-camera video. **M0: Environment & Repository**, **M1: Charter, Scope &
Requirements**, **M2: Literature & Measurement Framework**, and **M3:
Mathematical Verification** are complete.

## Project definition

- [Project charter](docs/project_charter.md)
- [Engineering requirements](docs/requirements.md)
- [Controlled terminology](docs/terminology.md)
- [Targeted literature review](docs/literature_review.md)
- [Measurement framework](docs/metrology/measurement_framework.md)
- [Literature matrix](references/literature_matrix.csv)
- [Bibliography](references/references.bib)

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

Verify the environment with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

No biomechanics, pose-estimation, experimental, or statistical performance
claims have been implemented or validated at this stage.
