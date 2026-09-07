# Coordinate Systems and Vectors

## Purpose

MotionLab calculates an angle from three 2D points. Those positions must first
be converted into the two directed segments meeting at the vertex.

## Core Concept

A Cartesian coordinate system represents a point as $P=(x,y)$ relative to an
origin $(0,0)$. A point describes *where*; a vector describes displacement and
direction. Identical components can represent either, but their meanings differ.

## Intuition

Two pins are absolute positions. “Move from pin B to pin A” is a vector. Moving
the entire drawing changes the point coordinates but not that instruction.

## Mathematical Foundation

For $A=(A_x,A_y)$ and $B=(B_x,B_y)$, the vector from B to A is

$$
\vec{u}=A-B=(A_x-B_x,\ A_y-B_y).
$$

For angle (ABC), with B as vertex:

$$
\vec{u}=A-B,\qquad \vec{v}=C-B.
$$

Order matters: $A-B$ points from B toward A; $B-A=-\vec{u}$. Under a
common translation $t$,

$$
(A+t)-(B+t)=A-B,
$$

so absolute position is irrelevant to the ideal included angle.

## Worked Example

With $A=(4,3)$, $B=(1,1)$, and $C=(1,5)$:

$$
A-B=(3,2),\qquad C-B=(0,4).
$$

The origin need not equal B; subtraction creates vertex-relative directions.

## Connection to MotionLab

[`angle_from_points_deg`](../../../src/motionlab/geometry.py) validates points,
calculates `a_array - b_array` and `c_array - b_array`, then delegates the angle
calculation. The [M3 notebook](../../../notebooks/01_geometry_foundations.ipynb)
executes this example, and the [tests](../../../tests/unit/test_geometry.py)
check translation invariance.

## Assumptions

- Points share one 2D coordinate system and compatible axis units.
- B is intentionally the vertex.
- Both vertex-to-endpoint segments are nonzero.

## Limitations

Digital images commonly use a corner origin and downward-positive y. Normalized
image axes may also have unequal scale. Those M4 conventions are not established
by M3 translation invariance.

## Common Mistakes

- Confusing a point with a vector.
- Saying `A - B` points from A to B.
- Requiring B to be the origin.
- Translating only one point and expecting invariance.
- Assuming normalized image coordinates are automatically isotropic.

## Implementation

Production code converts inputs to finite float arrays of shape `(2,)`, then
uses NumPy element-wise subtraction. Generic names keep geometry separate from
future landmark semantics.

## Verification

The translated 60-degree example differed from baseline by about
$2.842\times10^{-13}$ degrees due to finite-precision subtraction. The unit
test uses an absolute $10^{-12}$-degree tolerance.

## Evidence Status

- **V1:** construction and translation invariance were analytically checked.
- **V2:** known geometries and translation invariance are unit-tested.

No camera, measurement, biomechanical, or experimental validity is claimed.

## Interview Explanation

“For an angle at B, I subtract B from both endpoints. This creates B-to-A and
B-to-C directions. A common translation cancels algebraically, so ideal angle
geometry does not depend on absolute position.”

## Knowledge Check

1. Why does $A-B$ point from B to A?
2. What happens when subtraction order is reversed?
3. Why is the origin irrelevant after subtracting B?
4. Why does translation invariance not prove camera validity?

## References

- [Geometry implementation](../../../src/motionlab/geometry.py)
- [M3 notebook](../../../notebooks/01_geometry_foundations.ipynb)
- [Measurement framework](../../metrology/measurement_framework.md)
