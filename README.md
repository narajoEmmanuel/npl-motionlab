# NPL MotionLab

Markerless biomechanics measurement, validation, and engineering practice lab.

MotionLab is organized around a measurement system for estimating a narrowly
defined 2D projected sagittal-plane knee flexion angle from standardized
single-camera video. **M0: Environment & Repository** and **M1: Charter, Scope
& Requirements** are complete. **M2: Literature & Measurement Framework** has
not started.

## Project definition

- [Project charter](docs/project_charter.md)
- [Engineering requirements](docs/requirements.md)
- [Controlled terminology](docs/terminology.md)

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
