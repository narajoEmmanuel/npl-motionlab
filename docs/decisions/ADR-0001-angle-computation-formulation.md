# ADR-0001: Use atan2 for unsigned 2D angle computation

## Status

Accepted for M3 mathematical verification.

## Context

MotionLab requires a reusable function for calculating the unsigned included
angle between two finite, nonzero 2D vectors.

The initial implementation used the normalized dot-product relation:

```text
theta = arccos((u dot v) / (||u|| ||v||))
```

This formulation is mathematically correct and recovered the analytically
known 30, 45, 60, 90, 120, and 180 degree test geometries within floating-point
tolerance.

During numerical edge-case investigation, however, vectors separated by
approximately 1e-8 radians near 0 and 180 degrees were evaluated as exactly
0 and 180 degrees. The normalized cosine rounded to exactly +1 or -1 in
float64 before arccos was applied.

MotionLab distinguishes mathematical implementation behavior from later
experimental measurement quality. The purpose of this decision is therefore
to improve numerical robustness of the geometry layer, not to claim improved
camera, landmark, biomechanical, or experimental accuracy.

## Options considered

### Normalized dot product with arccos

Advantages:

- direct correspondence with the standard textbook angle formula;
- simple mathematical interpretation;
- correct results for ordinary geometries.

Disadvantages:

- loses small angular differences near 0 and 180 degrees when the normalized
  cosine rounds to +1 or -1;
- requires domain protection such as clipping;
- clipping can conceal implementation defects if used indiscriminately.

### Normalized determinant and dot product with atan2

For two normalized vectors, use:

```text
theta = atan2(
    |det(u_hat, v_hat)|,
    u_hat dot v_hat
)
```

where:

```text
det(u, v) = u_x * v_y - u_y * v_x
```

Advantages:

- preserves the same unsigned included-angle contract in [0, 180] degrees;
- agrees with the arccos formulation for ordinary geometries within numerical
  tolerance;
- retains angular information close to 0 and 180 degrees that was lost by the
  tested arccos implementation;
- does not require clipping of a normalized cosine before inverse
  trigonometric evaluation.

Disadvantages:

- is less immediately recognizable than the textbook arccos formula;
- requires understanding the geometric role of both determinant and dot
  product.

## Decision

Use the atan2 formulation for `angle_between_vectors_deg`.

Normalize the input vectors first, then calculate:

```text
determinant = u_hat_x * v_hat_y - u_hat_y * v_hat_x
dot_product = u_hat dot v_hat

theta = atan2(|determinant|, dot_product)
```

Convert the resulting angle from radians to degrees.

Use the absolute determinant because the current API represents an unsigned
included angle and intentionally does not encode clockwise versus
counterclockwise orientation.

For 2D vector magnitude, use `numpy.hypot` to reduce avoidable intermediate
underflow or overflow when calculating the Euclidean norm.

## Rationale

Manual numerical comparison showed:

- equivalent results for 30, 60, 90, 120, and 180 degree reference cases;
- an arccos result of exactly 0 degrees for a nonzero angle of approximately
  5.73e-7 degrees;
- an atan2 result preserving that nonzero angular difference;
- an arccos result of exactly 180 degrees for the corresponding near-180 case;
- an atan2 result preserving the offset from 180 degrees.

The atan2 formulation therefore provides better numerical behavior for the
identified boundary cases without changing the mathematical quantity being
reported.

## Consequences

- `angle_between_vectors_deg` continues to return an unsigned angle in
  [0, 180] degrees;
- the public API does not change;
- existing known-angle and invalid-input tests remain applicable;
- regression tests preserve the newly identified near-boundary behavior;
- signed rotation is explicitly outside the current function contract;
- this decision does not establish any experimental measurement threshold;
- a future pixel-length quality threshold, if required, must be justified by
  camera and measurement evidence rather than by this numerical implementation.

## Evidence

Evidence level at this decision:

- V1: analytically and numerically verified;
- V2: unit-tested.

Observed verification included:

- analytically known angles at 30, 45, 60, 90, 120, and 180 degrees;
- invalid zero-length, non-2D, NaN, and infinite inputs;
- translation invariance;
- positive uniform-scale invariance;
- symmetry of the unsigned angle;
- numerical behavior near 0 and 180 degrees;
- valid nonzero vectors with magnitudes on the order of 1e-300 and 1e300.

This evidence verifies the software geometry layer only. It does not validate:

- smartphone camera measurement;
- image-coordinate transformations;
- pose-estimation landmarks;
- projected knee flexion measurement;
- biomechanical validity;
- experimental accuracy;
- agreement with a reference method.

## Reconsideration conditions

Reconsider this decision if later requirements introduce:

- signed angles;
- three-dimensional geometry;
- alternative numerical precision requirements;
- vectorized high-volume computation requiring a different implementation;
- evidence of numerical failure within the actual MotionLab operating range.
