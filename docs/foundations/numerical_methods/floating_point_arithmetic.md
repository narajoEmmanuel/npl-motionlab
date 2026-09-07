# Floating-Point Arithmetic

## Purpose

MotionLab's equations use real numbers, but its implementation uses finite
`float64` values. This document explains why mathematically equivalent
operations can produce tiny differences and why numerical error must not be
confused with measurement error.

## Core Concept

Binary floating-point stores a finite approximation with sign, exponent, and
significand. `float64` provides a wide range and roughly 16 significant decimal
digits, but it cannot represent most real numbers exactly. **Machine precision**
describes the local spacing between representable values, not a universal
guarantee of decimal accuracy.

## Intuition

Floating-point is a very large, uneven ruler. Marks are close near zero and
farther apart at large magnitudes. Each operation may round to a nearby mark.
Subtracting nearly equal large values can discard shared leading digits; this
is cancellation.

## Mathematical Foundation

A simplified operation model is

$$
\operatorname{fl}(x\circ y)=(x\circ y)(1+\delta),
$$

where (operatorname{fl}) is the rounded machine result, (circ) is an
operation, and (delta) is a small operation-dependent relative error when the
result remains in normal range. This model is not an absolute error guarantee.

Overflow occurs when magnitude exceeds the finite range. Underflow occurs when
a result becomes too small for normal representation, potentially reaching a
subnormal value or zero. Because the spacing around 1 is about
$2.22\times10^{-16}$, `1.0 + 1e-16` rounds to `1.0` in float64.

## Worked Example

The M3 60-degree geometry returned approximately
`59.99999999999999`. After translating all points by `(100, 250)`, subtraction
produced about `60.00000000000028`, a difference near
$2.842\times10^{-13}$ degrees. The mathematical angle did not change; binary
representation and cancellation changed the computed last digits.

Near zero, vectors `(1, 0)` and `(1, 1e-8)` have an angle near
$5.73\times10^{-7}$ degrees. Their normalized cosine can round to exactly 1,
causing an `arccos` implementation to return exactly zero.

## Connection to MotionLab

The [geometry implementation](../../../src/motionlab/geometry.py) uses
`np.hypot` to limit avoidable norm overflow/underflow and `np.arctan2` to retain
boundary information. The [tests](../../../tests/unit/test_geometry.py) encode
explicit absolute tolerances and extreme finite-vector regressions.

## Assumptions

- NumPy arrays use the production conversion to floating dtype, currently
  standard double precision on the supported platform.
- Tolerances are selected for a specific numerical assertion.
- Inputs are finite before geometry is attempted.

## Limitations

Numerical robustness does not imply exact arithmetic. A $10^{-12}$-degree
pytest tolerance is a software-verification allowance, not a biomechanical
acceptance criterion, sensor resolution, or measurement uncertainty. Numerical
error, mathematical model error, and experimental error answer different
questions.

## Common Mistakes

- Comparing computed floats for exact equality without justification.
- Treating every last-digit difference as an algorithm failure.
- Treating a tight test tolerance as experimental accuracy.
- Using clipping to hide arbitrarily invalid results.
- Ignoring cancellation, overflow, or underflow because inputs are finite.

## Implementation

MotionLab validates `np.isfinite`, computes 2D norms with `np.hypot`, normalizes,
and evaluates determinant and dot product. `pytest.approx(..., abs=...)` states
the acceptable numerical difference for each test rather than asserting an
unrelated measurement threshold.

## Verification

M3 recorded analytical errors near $10^{-14}$ degrees, the translated-case
difference near $2.842\times10^{-13}$, near-boundary loss in the tested
`arccos` formula, and successful 90-degree calculations for components near
$10^{-300}$ and $10^{300}$.

## Evidence Status

- **V1:** observed behavior was compared with analytical expectations.
- **V2:** numerical regressions and tolerances are automated.

No experimental uncertainty or accuracy is established.

## Interview Explanation

“Float64 approximates real numbers, so algebraically invariant operations can
differ in the last digits. I characterize those effects, use robust primitives
such as `hypot` and `atan2`, and keep software tolerances separate from future
measurement acceptance criteria.”

## Knowledge Check

1. Why can `1.0 + 1e-16` equal `1.0` in float64?
2. What is cancellation?
3. How do overflow and underflow differ?
4. Why is a pytest tolerance not a biomechanical threshold?
5. How do numerical and experimental error differ?

## References

- [Geometry regression tests](../../../tests/unit/test_geometry.py)
- [M3 notebook](../../../notebooks/01_geometry_foundations.ipynb)
- [ADR-0001](../../decisions/ADR-0001-angle-computation-formulation.md)
