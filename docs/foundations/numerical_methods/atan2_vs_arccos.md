# `atan2` Versus `arccos`

## Purpose

M3 compared two mathematically valid formulations and selected the one that
preserved more angular information near 0 and 180 degrees. This page reconstructs
that engineering reasoning; [ADR-0001](../../decisions/ADR-0001-angle-computation-formulation.md)
is the authoritative decision record.

## Core Concept

For normalized 2D vectors, the dot product represents cosine and the determinant
represents signed sine:

$$
d=\hat{u}\cdot\hat{v}=\cos\theta,
\qquad
s=\det(\hat{u},\hat{v})=\sin\theta.
$$

The textbook formula is $\theta=\arccos(d)$. MotionLab instead uses
$\theta=\operatorname{atan2}(|s|,d)$.

## Intuition

Near zero, cosine changes quadratically while sine changes approximately
linearly:

$$
\cos\theta\approx1-\theta^2/2,
\qquad \sin\theta\approx\theta.
$$

A tiny direction difference can therefore disappear when cosine rounds to 1,
while the determinant still carries a representable small value. `atan2` uses
both pieces of information and resolves the correct unsigned quadrant.

## Mathematical Foundation

The 2D determinant is

$$
\det(u,v)=u_xv_y-u_yv_x.
$$

For unit vectors, its magnitude is $|\sin\theta|$. The pair
$(|\sin\theta|,\cos\theta)$ uniquely identifies an included angle on
$[0,\pi]$. Taking `abs(det)` discards clockwise/counterclockwise sign because
the API contract is deliberately unsigned.

`arccos` remains mathematically correct. Clipping a cosine to ([-1,1]) can
protect against small domain excursions, but it cannot recover angular
information already rounded to (+1) or (-1).

## Worked Example

For `u = (1, 0)` and `v = (1, 1e-8)`, the expected angle is approximately

$$
\operatorname{degrees}(\arctan(10^{-8}))
\approx 5.7295779513\times10^{-7}\text{ degrees}.
$$

The tested normalized-`arccos` implementation returned exactly `0.0` because
its cosine rounded to 1. The `atan2` formulation preserved
`5.729577951308232e-07`. The corresponding near-180 case collapsed to exactly
180 under `arccos`, while `atan2` preserved the nonzero offset.

## Connection to MotionLab

The final formula is implemented in
[`angle_between_vectors_deg`](../../../src/motionlab/geometry.py). The
[notebook](../../../notebooks/01_geometry_foundations.ipynb) demonstrates the
near-zero comparison. Regression tests require a positive near-zero result and
a near-180 result below 180 degrees.

## Assumptions

- Inputs are valid nonzero finite 2D vectors.
- The desired quantity is an unsigned included angle from 0 to 180 degrees.
- Normalization is completed using a robust finite norm.

## Limitations

`atan2` improved numerical robustness of the geometry calculation. It did **not**
improve camera accuracy, landmark localization, biomechanical validity,
experimental agreement, or measurement uncertainty. It does not supply signed
rotation, 3D geometry, or a pixel-quality rule.

## Common Mistakes

- Saying `arccos` is mathematically wrong.
- Assuming clipping recovers information lost to rounding.
- Omitting `abs(det)` while claiming an unsigned contract.
- Treating improved numerical resolution as improved experimental accuracy.
- Generalizing a boundary experiment beyond the tested data type and domain.

## Implementation

The production path normalizes each vector, computes the explicit determinant
and `np.dot`, calls `np.arctan2(abs(determinant), dot_product)`, converts to
degrees, and returns a Python float. The refactor preserved the public API.

## Verification

Both formulations agreed on ordinary 30, 60, 90, 120, and 180-degree cases
within tolerance. Boundary investigation exposed the collapse, motivated the
refactor, and produced regression tests. Known angles, invalid inputs,
invariances, symmetry, and extreme magnitudes remained passing afterward.

## Evidence Status

- **V1:** analytical and numerical comparison justified the formulation.
- **V2:** near-zero and near-180 regression tests protect the decision.

## Interview Explanation

“The cosine-only formula passed ordinary cases but lost tiny angles when cosine
rounded to plus or minus one. In 2D, determinant magnitude supplies sine, so
`atan2(abs(det), dot)` preserved about 5.73e-7 degrees without changing the
unsigned angle contract. That is numerical robustness, not experimental accuracy.”

## Knowledge Check

1. Why is `arccos` sensitive near 0 and 180 degrees?
2. What geometric quantity does the normalized determinant represent?
3. Why does MotionLab apply `abs` to the determinant?
4. What information can clipping not restore?
5. Which validity claims remain unsupported after this refactor?

## References

- [ADR-0001](../../decisions/ADR-0001-angle-computation-formulation.md)
- [Geometry implementation](../../../src/motionlab/geometry.py)
- [Numerical regression tests](../../../tests/unit/test_geometry.py)
