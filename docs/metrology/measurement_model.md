# MotionLab mathematical measurement model

## Deterministic model

For projected proximal, joint, and distal points `P`, `K`, and `D`, define `u=P-K` and `v=D-K`. For nonzero vectors, MotionLab evaluates the unsigned included angle

```math
\alpha=\operatorname{atan2}(|\det(\hat u,\hat v)|,\hat u\cdot\hat v)
```

in degrees on `[0,180]`. This is the numerical contract already implemented in Python and independently replicated in MATLAB.

If inputs are normalized image coordinates, first apply `x_px=x_norm W` and `y_px=y_norm H`. Euclidean geometry is evaluated after this conversion so the normalized axes are not assumed isotropic.

The broader conceptual projected-flexion convention remains `theta_flex=180°-alpha`. MATLAB reports both quantities explicitly, while Python-MATLAB cross-verification compares the currently implemented and unit-tested generic included angle.

## Perturbed-input sensitivity model

Collect landmark coordinates in `q` and apply a controlled deterministic perturbation `delta q`:

```math
\hat\alpha=f(q+\delta q),\qquad \Delta\alpha=\hat\alpha-\alpha
```

At M4-E, `delta q` is a modeling input such as ±1, ±2, ±3, or ±5 pixels. It is not an experimentally measured distribution and must not be called completed landmark uncertainty.

## Boundaries

The model does not yet quantify camera projection bias, optics, landmark semantics, pose-model behavior, manual-reference uncertainty, human movement, or combined measurement uncertainty. Those remain assigned to later validation and metrology milestones.
