# Vector Magnitude and Normalization

## Purpose

An angle compares directions, not segment lengths. MotionLab therefore needs a
reliable magnitude and a way to convert nonzero vectors to unit length.

## Core Concept

The Euclidean norm is straight-line vector length. A unit vector has norm 1.
Normalization divides a nonzero vector by its norm, removing scale while
preserving direction.

## Intuition

A 2D vector is a right-triangle hypotenuse. Normalizing replaces its arrow with
a length-one arrow pointing the same way.

## Mathematical Foundation

For $\vec{u}=(u_x,u_y)$:

$$
\|\vec{u}\|_2=\sqrt{u_x^2+u_y^2},\qquad
\hat{u}=\frac{\vec{u}}{\|\vec{u}\|_2}.
$$

For positive $k$, $\widehat{k\vec{u}}=\hat{u}$, proving positive-scale
invariance. A negative factor reverses direction.

## Worked Example

For $(3,4)$, the norm is $\sqrt{9+16}=5$ and the unit vector is
$(0.6,0.8)$. Vector $(-3,-4)$ also has norm 5 but opposite direction.
Scaling to $(6,8)$ doubles length without changing direction.

## Connection to MotionLab

[`_vector_norm_2d`](../../../src/motionlab/geometry.py) uses `numpy.hypot`.
The public function rejects zero norm and normalizes both vectors. Tests cover
components near $10^{-300}$ and $10^{300}$.

## Assumptions

- Inputs are finite 2D vectors in compatible units.
- M3 rejects exact zero length; it defines no pixel-quality threshold.

## Limitations

A nonzero vector has mathematical direction even if it represents 0.01 pixel.
That does not make the segment metrologically useful. A minimum pixel length
must later be justified by resolution, landmark uncertainty, and experiments.

## Common Mistakes

- Assuming magnitude can be negative or normalization changes direction.
- Dividing a zero vector by its norm.
- Claiming negative scaling preserves direction.
- Confusing representability with measurement quality.

## Implementation

`np.hypot(x, y)` avoids avoidable intermediate overflow or underflow from
forming `x*x + y*y`. Normalization makes the subsequent comparison depend on
direction rather than length.

## Verification

M3 checked the 3–4–5 example, positive-scale invariance, zero-vector rejection,
and 90-degree results for extreme finite magnitudes.

## Evidence Status

- **V1:** norm and scale properties were analytically exercised.
- **V2:** zero, scale, and extreme-magnitude cases are unit-tested.

## Interview Explanation

“I normalize nonzero vectors so angle depends on direction, not length. I use
`numpy.hypot` for robust 2D norms and keep mathematical degeneracy separate
from future measurement-quality thresholds.”

## Knowledge Check

1. Why do $(-3,-4)$ and $(3,4)$ have equal norms?
2. What does normalization remove and preserve?
3. Why can a zero vector not define an angle?
4. Why should geometry code not invent a minimum pixel length?

## References

- [Geometry implementation](../../../src/motionlab/geometry.py)
- [Geometry tests](../../../tests/unit/test_geometry.py)
- [ADR-0001](../../decisions/ADR-0001-angle-computation-formulation.md)
