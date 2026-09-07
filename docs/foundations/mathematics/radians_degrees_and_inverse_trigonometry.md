# Radians, Degrees, and Inverse Trigonometry

## Purpose

NumPy evaluates trigonometric functions in radians, while MotionLab's public
angle functions report degrees. Understanding conversion prevents unit errors.

## Core Concept

A degree divides a revolution into 360 parts. A radian is arc length divided by
radius. Inverse trigonometric functions recover an angle from a ratio.

## Intuition

Degrees communicate angles conveniently; radians connect them directly to
circle geometry. They express the same opening in different units.

## Mathematical Foundation

For arc length $s$ and radius $r$, $\theta_{rad}=s/r$. Therefore

$$
\pi\ \text{radians}=180^\circ,\qquad
\theta_{deg}=\theta_{rad}\frac{180}{\pi}.
$$

Real-valued `arccos` accepts $[-1,1]$ and returns $[0,\pi]$. `atan2(y,x)`
uses two signed components to select the appropriate quadrant.

## Worked Example

$$
\arccos(0.5)=\pi/3\approx1.0472\ \text{radians}=60^\circ.
$$

Thus `np.arccos(0.5)` does not directly return 60; `np.degrees` converts it.

## Connection to MotionLab

The [geometry function](../../../src/motionlab/geometry.py) calculates
`np.arctan2(abs(determinant), dot_product)` and calls `np.degrees`. The `_deg`
suffix makes the output unit explicit. The [notebook](../../../notebooks/01_geometry_foundations.ipynb)
reconstructs `arccos` for comparison.

## Assumptions

- NumPy trigonometric inputs and outputs use radians.
- The current public API reports unsigned degrees.

## Limitations

Converting units changes representation, not validity or accuracy. It cannot
repair invalid vectors, image coordinates, or biomechanical interpretation.

## Common Mistakes

- Expecting `np.arccos(0.5)` to return 60.
- Supplying degrees where radians are expected.
- Passing values outside the real `arccos` domain.
- Omitting units from names or reports.

## Implementation

MotionLab retains radians through `atan2` and converts once at the API boundary,
following NumPy's convention while reporting the project's chosen unit.

## Verification

M3 checked cosine values 1, 0.5, 0, -0.5, and -1 against familiar angles. Unit
tests compare degree outputs with six analytical geometries.

## Evidence Status

- **V1:** known inverse-trigonometric values and conversion were checked.
- **V2:** public degree outputs are unit-tested.

## Interview Explanation

“NumPy uses radians because they are the natural mathematical unit. MotionLab
calculates in radians, converts once with `np.degrees`, and makes the reporting
unit visible in the `_deg` API name.”

## Knowledge Check

1. Why does $\pi$ radians equal 180 degrees?
2. What is the real domain of `arccos`?
3. Why is `np.arccos(0.5)` approximately 1.0472?
4. Why does degree conversion not establish measurement validity?

## References

- [Geometry implementation](../../../src/motionlab/geometry.py)
- [M3 notebook](../../../notebooks/01_geometry_foundations.ipynb)
- [ADR-0001](../../decisions/ADR-0001-angle-computation-formulation.md)
