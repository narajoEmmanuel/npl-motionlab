# Engineering Requirements

## Purpose

This document defines the simplified Core requirements adopted on 2026-09-16.
Requirements that belonged to the previous larger validation program are now
optional or deferred unless explicitly listed here.

Status values are **Defined**, **Verified**, **Deferred**, and **Optional**.

## Scope and measurand

| ID | Requirement | Verification | Target | Status |
|---|---|---|---|---|
| ML-SCP-001 | The Core system shall estimate one principal measurand: 2D projected sagittal-plane knee flexion angle. | Charter and design inspection | M1 | Verified |
| ML-SCP-002 | The Core movement shall be a controlled bodyweight squat recorded with one standardized single-camera setup. | Protocol inspection | M7 | Defined |
| ML-SCP-003 | Public outputs shall identify the measurand as projected and two-dimensional wherever omission could imply anatomical 3D kinematics. | Claims audit | M9 | Defined |
| ML-SCP-004 | Clinical, diagnostic, injury-risk, rehabilitation, and professional-motion-capture-equivalence claims shall remain outside the Core. | Claims audit | M9 | Defined |

## Mathematical and software layer

| ID | Requirement | Verification | Target | Status |
|---|---|---|---|---|
| ML-MOD-001 | MotionLab shall define proximal/hip, knee, and distal/ankle landmark roles, segment vectors, angle convention, units, and invalid geometries. | Technical review | M3 | Verified |
| ML-MOD-002 | Normalized image coordinates shall be converted using image width and height before Euclidean angle geometry when normalized coordinates are used. | Analytical cases and tests | M3-M4 | Verified |
| ML-MOD-003 | The numerical implementation shall reject degenerate zero-length segments and use a numerically stable included-angle formulation. | Edge-case tests | M3 | Verified |
| ML-MOD-004 | Known-angle automated tests shall cover representative acute, right, obtuse, and straight geometries within documented tolerance. | Automated tests | M3 | Verified |
| ML-SW-001 | Project-specific scientific code shall remain modular and testable. | Code review and tests | Ongoing | Verified |
| ML-SW-002 | Important MotionLab, Sports2D, pose-model, and processing versions/configuration shall be recorded with derived outputs. | Output/configuration audit | M5-M9 | Defined |
| ML-SW-003 | Sports2D landmark outputs shall be treated as external inputs and explicitly mapped into MotionLab landmark roles. | Adapter tests and inspection | M5 | Defined |
| ML-SW-004 | MotionLab, not Sports2D, shall compute the authoritative project angle used in Core results. | Pipeline inspection and tests | M5-M6 | Defined |
| ML-SW-005 | Missing or invalid landmarks shall not be silently replaced with fabricated coordinates. | Adapter/pipeline tests | M5-M6 | Defined |

## Acquisition and provenance

| ID | Requirement | Verification | Target | Status |
|---|---|---|---|---|
| ML-CAM-001 | Source-video records shall retain file identity, decoded image dimensions, and available camera/video metadata relevant to interpretation. | Metadata inspection | M4 onward | Verified |
| ML-CAM-002 | The Core repeated-trial dataset shall use one fixed practical acquisition configuration and centered framing based on the bounded M4 evidence. | Protocol and dataset audit | M7 | Defined |
| ML-DAT-001 | Original identifiable videos shall remain private by default and shall not be committed to the public repository. | Git/release audit | Ongoing | Verified |
| ML-DAT-002 | Each derived result shall remain linkable to its source video identifier, engine/configuration version, and code revision. | M6 provenance JSON with source/boundary/code hashes; retain for M7-M9 | M6-M9 | Verified |

## Sports2D integration

| ID | Requirement | Verification | Target | Status |
|---|---|---|---|---|
| ML-POSE-001 | The Core shall use one explicitly pinned Sports2D/RTMPose workflow rather than multiple pose engines. | Environment/config inspection | M5 | Defined |
| ML-POSE-002 | The integration shall preserve pixel-coordinate meaning or document and test any required coordinate conversion. | Adapter test | M5 | Defined |
| ML-POSE-003 | Hip, knee, and ankle output columns shall be mapped explicitly to MotionLab landmark roles. | Known-record adapter test | M5 | Defined |
| ML-POSE-004 | Optional interpolation, filtering, or outlier processing shall remain disabled unless a concrete Core problem justifies enabling it. | Config inspection | M5-M6 | Defined |

## Core experiment

| ID | Requirement | Verification | Target | Status |
|---|---|---|---|---|
| ML-EXP-001 | One representative video shall demonstrate the complete source-to-angle workflow before the Core dataset is processed. | M6 documented local end-to-end run | M6 | Verified |
| ML-EXP-002 | The Core dataset shall contain five independent one-squat video trials under the same fixed practical setup. | Dataset audit | M7 | Defined |
| ML-EXP-003 | One predefined event-summary rule shall be frozen before processing the five Core trials. | Protocol/version inspection | M6-M7 | Defined |
| ML-EXP-004 | Frame count shall not be represented as independent replicate count. | Analysis review | M8 | Defined |

## Core analysis and conclusion

| ID | Requirement | Verification | Target | Status |
|---|---|---|---|---|
| ML-STA-001 | The Core analysis shall remain descriptive unless a specific later question requires inferential statistics. | Analysis review | M8 | Defined |
| ML-STA-002 | At minimum the Core shall report one predefined event result per trial, mean, standard deviation, minimum, maximum, range, and processing failure/missing-landmark count. | Results audit | M8 | Defined |
| ML-STA-003 | At least one representative full angle time series shall be retained as technical evidence of the workflow. | Figure/result inspection | M8 | Defined |
| ML-DEC-001 | The final conclusion shall apply only to the tested single-camera configuration and workflow. | Technical report review | M9 | Defined |
| ML-DEC-002 | Project completion shall not depend on achieving a favorable numeric result. | Decision/report review | M9 | Defined |
| ML-REP-001 | The public repository shall document how to reproduce the Core computational workflow subject to privacy restrictions on source videos. | Reproduction review | M9 | Defined |

## Optional requirements

### Kinovea manual reference appendix

| ID | Requirement | Verification | Status |
|---|---|---|---|
| ML-OPT-KIN-001 | If a Kinovea appendix is performed, the software version, manual procedure, selected Core trials, and paired-difference convention shall be documented. | Appendix inspection | Optional |
| ML-OPT-KIN-002 | Kinovea shall not be called ground truth. | Claims audit | Optional |

### Optional Advanced MATLAB Verification Appendix

| ID | Requirement | Verification | Status |
|---|---|---|---|
| ML-OPT-MAT-001 | If the MATLAB appendix is completed, its implementation and runtime/version shall be recorded separately from Core claims. | Appendix inspection | Optional |
| ML-OPT-MAT-002 | Python-to-MATLAB agreement may support implementation-consistency claims only, not pose or biomechanical validity. | Claims audit | Optional |

## Deferred advanced work

The following are not Core requirements:

- full camera intrinsic/lens calibration;
- systematic yaw, pitch, roll, height, distance, and multi-device studies;
- multiple pose-engine benchmarking;
- multiple participants or population inference;
- mandatory manual-reference validation;
- full GUM-style uncertainty budgets;
- Monte Carlo uncertainty propagation;
- robustness matrices;
- 3D, multi-camera, OpenSim, or inverse-kinematics workflows;
- accreditation or teaching-module expansion.

## Requirement-change control

A new mandatory requirement shall be added only when it is necessary to run or
interpret the end-to-end Core workflow, cannot reasonably be supplied by an
existing mature tool, and would materially weaken the final bounded conclusion
if omitted.
