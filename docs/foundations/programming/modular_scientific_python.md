# Modular Scientific Python

## Purpose

MotionLab separates reusable computation from exploratory explanation so tests,
notebooks, and future pipelines consume one authoritative implementation.

## Core Concept

A **function** is a named operation. A **module** is a Python file containing
related definitions. A **package** organizes importable modules. Public
functions form supported behavior; internal helpers are implementation details.

## Intuition

The module is laboratory equipment; a notebook is the demonstration and lab
record. Copying the equipment design into every notebook creates divergent
versions. Importing it ensures every demonstration uses the tested instrument.

## Mathematical or Scientific Foundation

Separation of concerns assigns one responsibility to each layer:

```text
src/motionlab/geometry.py  -> reusable generic geometry
tests/                     -> executable expectations and failure contracts
notebooks/                 -> explanation and reproducible demonstrations
docs/                      -> durable concepts, decisions, and claim limits
```

## Worked Example

`angle_from_points_deg(a, b, c)` exposes the three-point operation. It delegates
to `angle_between_vectors_deg(u, v)`. `_as_finite_2d_array` and
`_vector_norm_2d` begin with underscores, the Python convention signaling that
they are internal rather than public API.

## Connection to MotionLab

[geometry.py](../../../src/motionlab/geometry.py) contains typed signatures and
NumPy-style docstrings. The [notebook](../../../notebooks/01_geometry_foundations.ipynb)
imports these functions instead of copying them. Generic geometry intentionally
contains no hip, knee, ankle, camera, or pose-estimator logic.

## Assumptions

- Consumers install the `motionlab` package correctly.
- Public behavior is represented by the two non-underscored functions.
- Type hints aid review and tools but do not replace runtime validation.

## Limitations

Modularity improves reviewability and reuse; it does not prove scientific
validity. A well-structured function can still encode the wrong measurand.

## Common Mistakes

- Duplicating production algorithms inside notebooks.
- Treating a leading underscore as access control rather than convention.
- Assuming type hints enforce values at runtime.
- Mixing generic geometry with unverified biomechanics.
- Allowing documentation examples to become a second source of truth.

## Implementation

The module-level docstring states the scope. Public docstrings define inputs,
outputs, range, errors, and formulation. Internal helpers centralize validation
and norm computation. `ArrayLike` documents flexible inputs while validation
enforces the actual 2D finite domain.

## Verification

Tests import the installed package API, not a file by path. The executed
notebook imports the same API. This verifies that demonstrations and tests use
the production implementation.

## Evidence Status

- **V1:** responsibilities and API behavior were inspected against the design.
- **V2:** the installed public functions are exercised by unit tests.

## Interview Explanation

“I keep generic geometry in an importable module and use notebooks only for
explanation and experiments. Public functions define the supported contract;
underscored helpers isolate internal validation. That avoids duplicated
algorithms and keeps biomechanics out until its model is defined.”

## Knowledge Check

1. How do function, module, and package differ?
2. What does a leading underscore communicate?
3. Why do type hints not replace runtime validation?
4. Why should notebooks import production code?
5. Why does `geometry.py` avoid anatomical names?

## References

- [Geometry module](../../../src/motionlab/geometry.py)
- [Unit tests](../../../tests/unit/test_geometry.py)
- [Executable notebook](../../../notebooks/01_geometry_foundations.ipynb)
