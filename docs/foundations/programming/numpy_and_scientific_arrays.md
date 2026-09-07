# NumPy and Scientific Arrays

## Purpose

MotionLab uses NumPy to express small scientific vectors, validate numeric
inputs, and call stable numerical primitives. This is the relevant subset of
NumPy—not a general library tutorial.

## Core Concept

A Python list is a general container. A NumPy array is a homogeneous,
multidimensional numeric structure described by a **shape** and **dtype**.
Array operations apply consistently across components without hand-written
loops.

## Intuition

`[4.0, 3.0]` can hold coordinates, but NumPy gives those values an explicit
numeric representation and vector operations. Subtracting two shape-`(2,)`
arrays directly expresses coordinate-wise vector subtraction.

## Mathematical Foundation

For arrays representing $A=(4,3)$ and $B=(1,1)$, vectorized subtraction
evaluates

$$
A-B=(4-1,3-1)=(3,2).
$$

Shape `(2,)` means one axis containing exactly two elements. A floating dtype
supports the division and trigonometry required by normalization and angles.

## Worked Example

`np.asarray((3, 4), dtype=float)` converts a tuple to a float array. `np.hypot`
returns 5; division by 5 produces `(0.6, 0.8)`; `np.dot` compares alignment.
`np.isfinite` rejects NaN and infinities before those values enter geometry.

## Connection to MotionLab

The internal conversion helper in [geometry.py](../../../src/motionlab/geometry.py)
uses `np.asarray`, checks shape and `np.isfinite`, then the public function uses
`np.hypot`, `np.dot`, `np.arctan2`, and `np.degrees`. These calls map directly
to the M3 mathematical model.

## Assumptions

- Inputs are convertible to a numeric array without ambiguous object data.
- The API expects exactly one 2D vector, not a batch.
- Conversion to float is appropriate for this layer.

## Limitations

NumPy does not establish coordinate meaning, camera correctness, or measurement
quality. Vectorization also does not automatically make an algorithm stable;
the chosen formulation still matters.

## Common Mistakes

- Ignoring array shape and accidentally accepting 3D or batched input.
- Allowing NaN or infinity to propagate silently.
- Assuming a Python list supports element-wise scientific arithmetic.
- Believing NumPy removes the need for domain validation.

## Implementation

`np.asarray` accepts array-like public inputs without unnecessary copying when
possible. The private helper centralizes shape and finiteness checks. Each later
primitive has one role: `hypot` for norm, `dot` for cosine alignment,
`arctan2` for angle recovery, and `degrees` for the API unit.

## Verification

Tests pass tuples and arrays through the public API, reject wrong shape and
non-finite coordinates, and exercise extreme finite magnitudes. The notebook
demonstrates vectorized subtraction and norm calculation.

## Evidence Status

- **V1:** NumPy results were compared with manual analytical examples.
- **V2:** input conversion, validation, and numerical operations are unit-tested.

## Interview Explanation

“NumPy gives the geometry layer typed numeric arrays, shape-aware validation,
and reviewed primitives that map cleanly to the equations. I still validate
dimension and finiteness explicitly because a scientific library does not
define my domain contract for me.”

## Knowledge Check

1. How do an array's shape and dtype differ?
2. Why use `np.asarray` at the API boundary?
3. What invalid values does `np.isfinite` detect?
4. Which role does each of `hypot`, `dot`, `arctan2`, and `degrees` play?

## References

- [Geometry implementation](../../../src/motionlab/geometry.py)
- [Geometry tests](../../../tests/unit/test_geometry.py)
- [M3 notebook](../../../notebooks/01_geometry_foundations.ipynb)
