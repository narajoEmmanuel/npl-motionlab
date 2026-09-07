# MotionLab Engineering Foundations

## Purpose

This section explains the scientific-computing ideas that support MotionLab.
Each topic connects theory to the repository's implementation and evidence. It
is intentionally narrower than a general tutorial: concepts are documented
when MotionLab has used or investigated them.

## Knowledge areas

Current foundation:

- **Mathematics:** coordinates, vectors, norms, angles, radians, and degrees.
- **Numerical Methods:** floating-point behavior and angle formulation.
- **Programming:** NumPy arrays and modular scientific Python.
- **Software Engineering:** unit verification and reproducible packaging.

Future roadmap entries, to be documented only when studied in their milestone:

- Physics and Camera Optics
- Computer Vision
- Biomechanics
- Metrology
- Experimental Design
- Statistics and Agreement
- Measurement Uncertainty
- Monte Carlo Simulation
- Sensitivity Analysis
- Engineering Education

## Relationship to project milestones

The current documents explain **M3 — Mathematical Verification**. M3 created a
generic 2D angle implementation, verified analytical geometries, investigated
numerical boundaries, and protected behavior with unit tests. It does not yet
process images, landmarks, cameras, or human movement. Later milestones will
extend this knowledge base after those subjects are studied. Project scope and
validation layers remain in the [project charter](../project_charter.md) and
[measurement framework](../metrology/measurement_framework.md).

## Evidence rule

Documentation is not validation. A derivation can establish mathematical
validity, an experiment can characterize numerical behavior, and a test can
verify software behavior. None proves camera validity, measurement accuracy,
biomechanical validity, or experimental agreement. Current evidence is limited
to **V1 — analytically verified** and **V2 — unit-tested**; no V3–V6 claim is
made here.

## Suggested learning order

1. [Coordinate systems and vectors](mathematics/coordinate_systems_and_vectors.md)
2. [Vector magnitude and normalization](mathematics/vector_magnitude_and_normalization.md)
3. [Dot product and angle geometry](mathematics/dot_product_and_angle_geometry.md)
4. [Radians, degrees, and inverse trigonometry](mathematics/radians_degrees_and_inverse_trigonometry.md)
5. [Floating-point arithmetic](numerical_methods/floating_point_arithmetic.md)
6. [`atan2` versus `arccos`](numerical_methods/atan2_vs_arccos.md)
7. [NumPy and scientific arrays](programming/numpy_and_scientific_arrays.md)
8. [Modular scientific Python](programming/modular_scientific_python.md)
9. [Unit testing and verification](software_engineering/unit_testing_and_verification.md)
10. [Reproducible Python packages](software_engineering/reproducible_python_packages.md)

## Primary M3 evidence

- [Geometry implementation](../../src/motionlab/geometry.py)
- [Geometry unit tests](../../tests/unit/test_geometry.py)
- [Executable geometry notebook](../../notebooks/01_geometry_foundations.ipynb)
- [ADR-0001](../decisions/ADR-0001-angle-computation-formulation.md)
