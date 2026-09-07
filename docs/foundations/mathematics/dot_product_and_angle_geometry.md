# Dot Product and Angle Geometry

## Purpose

MotionLab needs a generic unsigned angle between two nonzero 2D vectors. The
dot product connects direction, magnitude, and angle cosine.

## Core Concept

The dot product multiplies corresponding components and adds them. Its result
is a scalar whose sign indicates directional alignment.

## Intuition

Vectors pointing mostly together produce a positive dot product; perpendicular
vectors produce zero; mostly opposing vectors produce a negative value.

## Mathematical Foundation

For $\vec{u}=(u_x,u_y)$ and $\vec{v}=(v_x,v_y)$:

$$
\vec{u}\cdot\vec{v}=u_xv_x+u_yv_y
=\|\vec{u}\|\|\vec{v}\|\cos(\theta).
$$

For nonzero vectors, positive, zero, and negative products correspond to acute,
right, and obtuse included angles. After normalization,
$\hat{u}\cdot\hat{v}=\cos(\theta)$. MotionLab combines this with determinant
information as explained in [`atan2` versus `arccos`](../numerical_methods/atan2_vs_arccos.md).

## Worked Example

With $u=(1,0)$, dot products with $(2,0)$, $(0,3)$, and $(-4,0)$ are 2,
0, and -4, corresponding to 0, 90, and 180 degrees. Also,
$(2,3)\cdot(4,-1)=5$. M3 verified 30, 45, 60, 90, 120, and 180 degrees using
known unit-circle endpoints.

## Connection to MotionLab

[`angle_between_vectors_deg`](../../../src/motionlab/geometry.py) combines
`np.dot(u_unit, v_unit)` with the absolute 2D determinant. The
[tests](../../../tests/unit/test_geometry.py) cover acute through opposite
vectors and symmetry under vector-order exchange.

## Assumptions

- Vectors are finite, 2D, nonzero, and consistently scaled.
- The result is the unsigned included angle in $[0^\circ,180^\circ]$.

## Limitations

This generic result is not automatically a knee-flexion angle. The included
segment angle and projected flexion convention are distinct, and landmarks,
image conversion, projection, and anatomical interpretation need later evidence.

## Common Mistakes

- Treating the dot product itself as an angle.
- Ignoring length before interpreting it as cosine.
- Inferring perpendicularity when one vector is zero.
- Assuming an unsigned result carries rotation direction.
- Calling verified geometry validated biomechanics.

## Implementation

MotionLab normalizes first. `abs(determinant)` removes orientation sign, while
the dot product distinguishes acute from obtuse configurations. The production
module remains the authoritative algorithm.

## Verification

Analytical known-angle cases, symmetry, translation, positive scaling, invalid
inputs, and near-boundary regressions are automated.

## Evidence Status

- **V1:** analytical geometries and algebraic properties were checked.
- **V2:** output, failure, and invariance contracts are unit-tested.

## Interview Explanation

“The dot product supplies cosine alignment and the 2D determinant supplies sine
magnitude. `atan2(abs(det), dot)` returns an unsigned included angle from zero
to 180 degrees; biomechanical interpretation is a separate layer.”

## Knowledge Check

1. Why is a dot product scalar?
2. What does its sign reveal for nonzero vectors?
3. Why normalize before interpreting it as cosine?
4. Why is the current angle symmetric?
5. Why is it not yet a validated knee angle?

## References

- [Geometry implementation](../../../src/motionlab/geometry.py)
- [Controlled terminology](../../terminology.md)
- [Measurement framework](../../metrology/measurement_framework.md)
