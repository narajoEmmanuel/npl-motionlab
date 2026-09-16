# MATLAB verification layer

MATLAB is a secondary analytical implementation for MotionLab. Python remains the primary software implementation and pytest environment.

## Purpose

MATLAB is used for independent mathematical verification, deterministic measurement modeling, controlled landmark-perturbation simulation, sensitivity analysis, replay of existing private M4-D descriptive analysis, technical figures, and Python-MATLAB numerical cross-verification.

It does not implement pose estimation and does not establish biomechanical, clinical, diagnostic, participant-validation, completed-uncertainty, or markerless-accuracy claims.

## Requirements

The implementation is designed for base MATLAB, with no toolbox required. The exact MATLAB release used for verified results must be recorded when the workflow is executed. Until then, the MATLAB runtime verification remains pending.

## Execution

From the repository root, generate Python results from the neutral CSV:

```powershell
.\.venv\Scripts\python.exe scripts\export_matlab_crosscheck.py
```

Then in MATLAB:

```matlab
addpath('matlab')
outputs = run_m4e_verification();
```

To replay M4-D using the existing private directory without copying it into the public repository:

```matlab
outputs = run_m4e_verification('C:\path\to\private\m4d01');
```

Known-angle and Python-MATLAB comparisons use `1e-10` degrees as a numerical implementation tolerance, not an experimental acceptance threshold. Generated artifacts are written under `matlab/results/` and are ignored by default except for its README.
