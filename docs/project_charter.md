# Project Charter

## Document control

| Field | Value |
|---|---|
| Project | NPL MotionLab |
| Milestone | M1 — Charter, Scope & Requirements |
| Status | Baseline definition |
| Owner | Emmanuel Naranjo Blanco |
| Last updated | 2026-09-06 |

## Objective

Build and validate a reproducible engineering measurement system that estimates
a two-dimensional projected sagittal-plane knee flexion angle from standardized
single-camera smartphone video during a controlled bodyweight squat.

The project will determine whether the resulting markerless measurement has
sufficient agreement, repeatability, and robustness for a narrowly defined
engineering education and movement-analysis laboratory use case. Suitability
will be decided against criteria whose provenance is documented and whose
values are frozen before confirmatory analysis.

## Engineering question

Under a controlled baseline camera and movement protocol, how closely and how
repeatably does a markerless estimate of projected knee flexion agree with a
characterized, same-video, manually digitized 2D reference measurement?

## Intended use

MotionLab is intended for controlled engineering measurement, experimentation,
and education. Its initial use is to teach and demonstrate measurement-model
definition, analytical and software verification, camera effects, reference
method characterization, agreement analysis, uncertainty, and engineering
decision-making.

## Primary measurand

The primary measurand is the **2D projected sagittal-plane knee flexion angle**
derived from projected thigh and shank segment geometry in the image plane.
The working landmark roles are:

- proximal point: projected lateral hip reference;
- vertex: projected lateral knee reference;
- distal point: projected lateral ankle reference.

The working convention assigns 0° to projected full extension and increasing
positive values to projected flexion. M3 must formally derive this convention,
define coordinates and edge cases, and verify known-angle geometries before the
implementation is treated as verified.

This is an image-plane measurand. It is not a full anatomical three-dimensional
knee joint angle.

## Measurement-system boundary

The system boundary begins with a source video and its acquisition metadata. It
includes camera geometry, image dimensions, timing, pose-engine outputs,
landmark semantics, coordinate conversion, quality handling, angle calculation,
optional predefined processing, reference digitization, configuration, and
derived results. It ends with traceable measurement outputs and an engineering
decision for the stated intended use.

The participant, movement instructions, camera placement, lighting, reference
markers, and operator decisions are external inputs that can affect the
measurement and therefore must be controlled, recorded, or characterized.

## Validation architecture

1. **Layer A — Analytical and software verification:** synthetic coordinates,
   known angles, edge cases, and unit tests.
2. **Layer B — Physical geometry and camera verification:** planar reference
   geometry, pixel conversion, projection, perspective, and image sensitivity.
3. **Layer C — Human-compatible reference characterization:** same-video manual
   digitization of visible standardized lateral reference markers, including
   operator and semantic limitations.
4. **Layer D — Controlled baseline validation:** independent squat trials under
   a fixed acquisition protocol, comparing markerless and reference estimates.
5. **Layer E — Robustness experiments:** selected factors evaluated only after
   baseline performance is understood.

Each layer supports different claims. Passing a lower layer does not establish
validity at a higher layer.

## In scope

- one principal 2D projected knee-flexion measurand;
- standardized single-camera smartphone video;
- controlled bodyweight squats;
- analytical and software verification;
- camera/image-coordinate verification;
- characterization of an accessible same-video 2D reference method;
- independent pilot and confirmatory datasets;
- agreement, error, repeatability, uncertainty, and selected robustness work;
- raw-first data handling and traceability;
- an explicit engineering decision for the intended use;
- educational translation after the measurement decision is complete.

## Out of scope for the Core project

- clinical or diagnostic use;
- injury detection, risk prediction, or rehabilitation assessment;
- claims of anatomical 3D joint-angle measurement;
- equivalence to Vicon or professional marker-based motion capture;
- replacement of clinical or research-grade motion-capture systems;
- population-level or athlete-performance claims;
- simultaneous expansion to hip and ankle measurands;
- unnecessary cloud, database, distributed, or ML-training infrastructure.

Advanced extensions require completion of the Core evidence chain and a
documented scope decision.

## Stakeholders and audiences

- project owner and primary learner: Emmanuel Naranjo Blanco;
- engineering and biomechanics reviewers;
- measurement, statistics, and laboratory specialists;
- engineering educators and accreditation-aware evaluators;
- engineering recruiters;
- future Naranjo Performance Lab audiences.

## Governing principles

- measurement problem first; pose technology is a component, not the project;
- raw information is preserved and derived transformations are traceable;
- frames are observations, not automatically independent experimental units;
- pilot and confirmatory data remain separate;
- acceptance criteria are frozen before confirmatory analysis;
- correlation does not establish agreement;
- the reference method is characterized rather than called ground truth;
- uncertainty sources are labeled by their evidential basis;
- negative results are acceptable;
- public claims do not exceed the available evidence.

## M1 deliverables

- this project charter;
- a uniquely identified, testable requirements baseline;
- a controlled terminology baseline;
- README links to the project-definition documents.

## M1 acceptance criteria

- intended use, engineering question, measurand, system boundary, scope, and
  exclusions are explicit and mutually consistent;
- requirements use unique identifiers and name a verification method and target
  milestone;
- terminology distinguishes error, agreement, repeatability, uncertainty,
  reference measurement, and projected angle concepts;
- no numerical performance threshold or unsupported validity claim is invented;
- M0 tests continue to pass and the documentation passes repository checks.

## Risks and controls

| Risk | Consequence | Current control |
|---|---|---|
| Scope expansion | Core evidence becomes shallow | One measurand; advanced work deferred |
| Semantic landmark mismatch | Systematic disagreement | Characterize reference and model landmark meanings |
| Pseudoreplication | Overstated precision | Define the experimental unit before analysis |
| Reference treated as truth | Unsupported accuracy claim | Quantify and report reference limitations |
| Data leakage or privacy loss | Ethical and reputational harm | Local raw data, Git exclusions, sanitized public samples |
| Post hoc success criteria | Biased decision | Freeze protocol, SAP, and criterion before confirmation |
| Tool-driven design | Measurement purpose becomes secondary | Maintain technology-independent requirements |

## Git checkpoint

The planned coherent checkpoint is:

```text
docs: define MotionLab charter and requirements
```

M2 must not begin until this M1 baseline is reviewed and committed.
