# Unit Testing and Verification

## Purpose

MotionLab uses tests to make mathematical and software claims inspectable and
repeatable. M3 tests define what the generic geometry must calculate, reject,
and preserve.

## Core Concept

A **unit test** exercises a small behavior against an expected result. A
**failure contract** defines invalid inputs and the expected exception. A
**regression test** preserves behavior discovered during investigation so a
future change cannot silently reintroduce the defect.

## Intuition

An example says “this worked once.” A unit test says “this behavior is part of
the contract and must continue working whenever the suite runs.” Tests are
strongest when expected values come from an independent analytical argument.

## Mathematical or Scientific Foundation

For an analytical expected angle $\theta_e$ and computed value $\theta_c$, a
test may require

$$
|\theta_c-\theta_e|\leq\varepsilon,
$$

where $\varepsilon$ is a numerical test tolerance. This is not an experimental
acceptance limit. `pytest.approx` expresses such comparison explicitly.

Property-oriented tests check relations rather than one value, for example

$$
\theta(A+t,B+t,C+t)\approx\theta(A,B,C)
$$

and $\theta(u,v)\approx\theta(v,u)$ for the unsigned definition.

## Worked Example

One parametrized test supplies six expected angles—30, 45, 60, 90, 120, and
180 degrees—to the same assertion. Separate tests expect `ValueError` for zero
vectors, coincident vertex points, wrong dimension, NaN, and infinity. The
near-zero regression asserts both proximity to the analytical value and that
the result remains greater than zero.

## Connection to MotionLab

The complete M3 categories are visible in
[`tests/unit/test_geometry.py`](../../../tests/unit/test_geometry.py):

- known analytical angles;
- invalid domain and failure contracts;
- translation and positive uniform-scale invariance;
- unsigned-angle symmetry;
- near-0 and near-180 numerical regressions;
- extremely small and large finite vectors.

## Assumptions

- Expected results are derived independently of the production function.
- Tolerances match the numerical question being tested.
- The environment installs the same package that tests import.

## Limitations

Passing tests is verification, not experimental validation. Tests do not show
that a camera observes correct points, that landmarks represent anatomy, or
that results agree with a reference method. They cover selected cases, not
every possible floating-point input.

## Common Mistakes

- Calling unit tests validation of the full measurement system.
- Recomputing the expected value with the same production algorithm.
- Testing only valid inputs and omitting failure behavior.
- Using exact float equality without justification.
- Mistaking parametrization for independent experimental replication.

## Implementation

`pytest.mark.parametrize` reduces repeated test structure while retaining
individual cases. `pytest.raises` checks failure contracts, and
`pytest.approx` handles justified numerical tolerances. Descriptive test names
state the behavior or property rather than implementation steps.

## Verification

The M3 suite contains 21 geometry tests; together with 9 environment tests the
repository baseline is 30 passing tests. The suite was rerun after the `atan2`
refactor and after notebook execution.

## Evidence Status

- **V1 — analytically verified:** known synthetic answers and properties were
  reasoned about independently.
- **V2 — unit-tested:** those expectations and regressions execute automatically.

V2 does not imply V3–V6.

## Interview Explanation

“I separate analytical verification from automated unit testing. Known
geometries give independent expected values, property tests cover invariances,
and failure tests define invalid input. Passing them verifies the geometry
software, not camera or experimental accuracy.”

## Knowledge Check

1. How does a regression test differ from an ordinary example?
2. Why should expected results be independent of production code?
3. What does `pytest.approx` express?
4. Which invalid-domain cases does M3 test?
5. Why are 30 passing tests not experimental validation?

## References

- [M3 geometry tests](../../../tests/unit/test_geometry.py)
- [Geometry implementation](../../../src/motionlab/geometry.py)
- [Project requirements](../../requirements.md)
