# Engineering Requirements

## Purpose and interpretation

This document translates the project charter into a traceable baseline. `Shall`
denotes a required property. Verification milestones identify when evidence is
expected; they do not imply that the requirement is already satisfied.

Status values are **Defined**, **Verified**, and **Deferred**. All Core
requirements are currently Defined unless explicitly stated otherwise. Evidence
will be linked as later milestones are completed.

## Scope and measurand

| ID | Requirement | Rationale | Verification | Target |
|---|---|---|---|---|
| ML-SCP-001 | The Core system shall estimate one principal measurand: 2D projected sagittal-plane knee flexion angle. | Protects depth and interpretability. | Charter and design inspection | M1 |
| ML-SCP-002 | The Core movement shall be a controlled bodyweight squat recorded using a standardized single-camera setup. | Bounds the initial intended use. | Protocol inspection | M10 |
| ML-SCP-003 | Project outputs shall describe the measurand as projected and two-dimensional wherever omission could imply an anatomical 3D angle. | Prevents claim inflation. | Terminology and publication review | M1, M22 |
| ML-SCP-004 | Clinical, diagnostic, injury, rehabilitation, and professional-motion-capture-equivalence claims shall remain outside the validated use. | Evidence cannot support these uses. | Claims audit | M16, M22 |

## Measurement model and software

| ID | Requirement | Rationale | Verification | Target |
|---|---|---|---|---|
| ML-MOD-001 | The measurement model shall define projected proximal, knee, and distal points; segment vectors; angle convention; coordinate system; units; and invalid geometries. | Makes the measurand operational. | Technical review | M3 |
| ML-MOD-002 | Normalized image coordinates shall be converted using image width and height before Euclidean angle geometry is evaluated. | Avoids anisotropic normalized-coordinate error. | Analytical cases and unit tests | M3–M4 |
| ML-MOD-003 | The numerical implementation shall handle zero-length segments explicitly and constrain inverse-cosine input against floating-point excursion. | Prevents undefined or unstable results. | Edge-case tests | M3 |
| ML-MOD-004 | Known-angle tests shall include 30°, 45°, 60°, 90°, 120°, and 180° geometries within a documented numerical tolerance. | Verifies the core geometry. | Automated unit tests | M3 |
| ML-SW-001 | Scientific code shall be modular, testable, typed where useful, and separated from notebooks. | Supports review and reuse. | Code review and tests | M3 onward |
| ML-SW-002 | Important software, model, and processing versions shall be recorded with derived outputs. | Supports reproducibility. | Metadata inspection | M6–M8 |
| ML-SW-003 | Raw landmarks and raw angles shall be preserved before optional filtering or smoothing. | Protects evidence and reanalysis. | Pipeline and data audit | M6–M8 |

## Camera and reference method

| ID | Requirement | Rationale | Verification | Target |
|---|---|---|---|---|
| ML-CAM-001 | Acquisition records shall identify resolution, image dimensions, orientation, and relevant camera configuration. | Camera geometry is part of the instrument. | Metadata inspection | M4, M8 |
| ML-CAM-002 | Baseline acquisition shall control or record camera position, height, orientation, distance, subject orientation, resolution, and lighting. | Limits uncontrolled variation. | Protocol and trial-record audit | M10–M11 |
| ML-REF-001 | The reference measurement shall be derived independently from manually digitized visible reference markers in the same video unless a documented decision selects a superior accessible method. | Enables synchronized comparison without claiming unavailable instrumentation. | Method inspection and ADR | M7 |
| ML-REF-002 | Reference characterization shall address placement, visibility, digitization, resolution, operator repeatability, and semantic mismatch. | The reference is not automatically ground truth. | Reference study report | M7 |
| ML-REF-003 | Reference uncertainty shall be quantified or explicitly listed as unquantified before the final engineering decision. | Prevents overstated conclusions. | Uncertainty budget review | M13, M16 |

## Experimental design and statistics

| ID | Requirement | Rationale | Verification | Target |
|---|---|---|---|---|
| ML-EXP-001 | The analysis shall identify the experimental unit and account for the subject–session–trial–frame hierarchy. | Avoids pseudoreplication. | Protocol and SAP review | M10 |
| ML-EXP-002 | Independent repeated trials shall support repeatability or agreement claims; frame count alone shall not be represented as independent sample size. | Aligns evidence with the question. | Dataset and analysis audit | M11–M12 |
| ML-EXP-003 | Pilot data shall remain distinguishable from confirmatory data. | Prevents data-dependent confirmation. | Dataset provenance audit | M9–M11 |
| ML-EXP-004 | The protocol, statistical analysis plan, exclusions, and acceptance criterion shall be frozen before confirmatory analysis. | Limits post hoc bias. | Versioned freeze records | M10 |
| ML-STA-001 | Primary metrics shall answer predefined engineering questions about error, agreement, repeatability, failure, or uncertainty. | Avoids statistical theater. | SAP traceability review | M10 |
| ML-STA-002 | Correlation or R² shall not be used as evidence of agreement, and statistical significance shall not substitute for engineering relevance. | Prevents common interpretation errors. | Analysis review | M12 |
| ML-STA-003 | Confirmatory estimates shall include uncertainty intervals when justified by the design and assumptions. | Communicates estimation precision. | Analysis and assumptions review | M12–M13 |

## Uncertainty and engineering decision

| ID | Requirement | Rationale | Verification | Target |
|---|---|---|---|---|
| ML-UNC-001 | Each uncertainty contribution shall be labeled as experimentally quantified, literature informed, instrument specified, estimated, modeled, exploratory, or unquantified. | Makes evidential strength visible. | Uncertainty-budget audit | M13 |
| ML-UNC-002 | Exploratory Monte Carlo inputs shall not be presented as measured uncertainty. | Prevents modeled assumptions becoming facts. | Simulation report review | M14 |
| ML-DEC-001 | Acceptance criteria shall distinguish literature-informed, project-defined engineering, and exploratory origins. | Makes criterion provenance explicit. | Decision record review | M10, M16 |
| ML-DEC-002 | The final decision shall state acceptable, conditionally acceptable, or unacceptable for the bounded intended use and shall document accepted and rejected uses. | Forces an actionable, limited conclusion. | Decision report inspection | M16 |

## Data governance and reproducibility

| ID | Requirement | Rationale | Verification | Target |
|---|---|---|---|---|
| ML-DAT-001 | Raw data shall be immutable and traceable to reference, interim, processed, and public or synthetic derivatives. | Preserves provenance. | Data-layout and checksum audit | M8 |
| ML-DAT-002 | Session, trial, source video, reference data, configuration, software/model version, output, and figure identifiers shall be linkable. | Enables reproduction and investigation. | Traceability audit | M8 |
| ML-DAT-003 | Identifiable human video and private metadata shall not be committed or published by default. | Protects privacy. | Git and release audit | M0 onward |
| ML-REP-001 | `pyproject.toml` shall remain the primary dependency declaration, with an exact resolved environment recorded at reproducibility checkpoints. | Avoids contradictory environments. | Configuration inspection | M0 onward |
| ML-REP-002 | Automated tests shall accompany mathematical and software claims. | Connects claims to evidence. | Test and evidence review | M3 onward |
| ML-REP-003 | Public results shall be reproducible from documented inputs, configurations, code versions, and procedures, subject to privacy restrictions. | Supports independent engineering review. | Reproduction exercise | M22 |

## Deferred Advanced requirements

Hip and ankle angles, multiple participants or devices, multiple raters,
factorial robustness designs, advanced filtering comparisons, and additional
movements are not Core requirements. They require a documented scope change and
must not delay the Core evidence chain.

## Requirement-change control

A material requirement change shall record its context, rationale, consequences,
and affected evidence. After the M10 freeze, changes affecting confirmatory
interpretation shall be versioned and disclosed rather than silently replacing
the frozen plan.
