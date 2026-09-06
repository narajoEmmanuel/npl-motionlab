# M2 Targeted Literature Review

## Document control

| Field | Value |
|---|---|
| Milestone | M2 — Literature & Measurement Framework |
| Review type | Targeted engineering scoping review |
| Search date | 2026-09-06 |
| Status | M2 evidence baseline |

## Review purpose

This review informs the initial measurand, reference strategy, camera controls,
validation hierarchy, statistical direction, and uncertainty framework. It is
not a systematic review and does not claim exhaustive coverage.

## Search approach

Sources were located through PubMed, PubMed Central, publisher records, DOI
records, and official Joint Committee for Guides in Metrology (JCGM/BIPM)
publications. Searches combined terms for markerless motion capture, 2D video,
knee flexion, squat, sagittal plane, manual digitization, camera viewpoint,
agreement, repeated observations, and measurement uncertainty.

Priority was given to:

1. official metrology guidance;
2. peer-reviewed systematic reviews;
3. peer-reviewed validation or reliability studies close to the intended task;
4. foundational method-comparison papers.

The traceable extraction is stored in
[`references/literature_matrix.csv`](../references/literature_matrix.csv), and
bibliographic metadata is stored in
[`references/references.bib`](../references/references.bib).

## Findings

### Markerless performance is context dependent

The 2025 systematic review by Yoma et al. found large variation across systems,
tasks, planes, joints, and statistical methods. Squat and landing tasks often
showed favorable reliability, while between-technology differences remained
variable. Chougule et al. similarly reported better performance for several
sagittal-plane lower-limb measures than for other contexts, while emphasizing
that further validation is required.

**MotionLab implication:** evidence from another model, task, population, or
output cannot be transferred as proof. The selected pipeline must be validated
for this exact projected measurand and controlled squat protocol.

### A 2D projected measurand is defensible but deliberately limited

Leporace et al. found that 2D video measurements can be reliable, but agreement
with 3D systems varies and is generally weaker outside the sagittal plane.
Peebles et al. demonstrated that low-cost continuous 2D sagittal kinematics can
be useful while still showing participant-dependent disagreement from 3D
motion capture. This is consistent with defining the output as an image-plane
quantity instead of treating it as an anatomical 3D joint angle.

**MotionLab implication:** retain the 2D projected sagittal-plane knee-flexion
measurand and prohibit unqualified 3D or clinical interpretations.

### The reference procedure needs its own experiment

Ross et al. found that single-camera manually digitized sagittal angles can have
useful reliability, but performance depended on rater experience, marker use,
joint, and gait event. Krause et al. reported high test-retest reliability for a
2D deep-squat application while still observing systematic differences from a
3D system, particularly at the hip. Reliability therefore does not establish
agreement or trueness.

**MotionLab implication:** visible-marker digitization remains a plausible
accessible reference candidate, but M7 must characterize placement,
digitization, operator repeatability, resolution, and semantic mismatch before
the method supports validation claims.

### Camera configuration is an influence quantity

Baldinger et al. demonstrated that camera viewpoint can materially change
OpenPose-derived joint angles even when the underlying landmark estimates appear
plausible. The study concerns a particular model and task, so its numerical
results are not transferable to MotionLab; the physical conclusion that
projection and occlusion matter is transferable.

**MotionLab implication:** baseline camera pose and participant orientation must
be controlled. Camera yaw, height, distance, and resolution are candidates for
later verification or robustness work, not simultaneous factors in the first
baseline experiment.

### Agreement is not correlation

Bland and Altman established that correlation is unsuitable as evidence that two
measurement methods agree. Their difference-based framework estimates bias and
limits of agreement, but the simple formulation assumes independent pairs. Their
later work addresses multiple observations per individual.

**MotionLab implication:** differences are primary. Any limits-of-agreement
analysis must reflect the subject/session/trial/frame hierarchy; treating frames
as independent pairs would be pseudoreplication.

### A result requires a measurement model and uncertainty statement

JCGM 200 provides the vocabulary for measurand, measurement result, procedure,
and uncertainty. JCGM 100 provides the general framework for expressing
measurement uncertainty, and JCGM 101 covers propagation of distributions by
Monte Carlo methods.

**MotionLab implication:** uncertainty work must start from a documented
measurement model and evidence-classified inputs. Monte Carlo is appropriate
only after its input distributions and correlations are justified; hypothetical
pixel errors remain sensitivity scenarios, not measured uncertainty.

## M2 engineering decisions

1. **Retain the intended use and single measurand.** The literature supports
   studying sagittal knee kinematics but does not support broader validity.
2. **Retain same-video manual marker digitization as the preferred candidate
   reference.** This is not yet a frozen reference procedure or ground truth.
3. **Use a controlled sagittal baseline before robustness factors.** Projection
   and occlusion make unconstrained camera placement indefensible.
4. **Carry difference-based metrics forward as candidates.** Signed error,
   absolute error, bias, MAE, RMSE, failure rate, and appropriately structured
   limits of agreement remain candidates for M10; none is yet designated as a
   frozen primary metric.
5. **Treat repeated frames as clustered observations.** The statistical unit
   must be selected from the experimental question, not from frame count.
6. **Adopt JCGM vocabulary and uncertainty logic.** Numerical distributions and
   budgets are deferred until evidence exists.

## Evidence gaps

- no reviewed source validates the exact future MotionLab implementation;
- results from 3D or multi-camera systems do not establish single-camera 2D
  performance;
- model-landmark semantics may not coincide with visible anatomical markers;
- a smartphone's lens, processing, variable frame rate, and metadata behavior
  remain uncharacterized;
- operator repeatability for the planned reference procedure is unknown;
- an engineering acceptance threshold with appropriate provenance has not been
  identified;
- the appropriate unit and repeated-measures model depend on the final protocol.

## M2 acceptance criteria

- sources are real, traceable, and classified by type;
- findings are separated from MotionLab decisions and untested assumptions;
- no literature result is represented as validation of MotionLab;
- the measurement framework identifies inputs, outputs, influence quantities,
  traceability, and evidence boundaries;
- gaps and deferred decisions are explicit;
- no acceptance threshold is invented.

## Risks

- targeted searching can miss relevant literature;
- rapidly evolving pose-estimation evidence can become outdated;
- heterogeneous definitions of joint angle and validity limit comparison;
- published reliability may conceal poor agreement or systematic bias;
- numerical findings may be overgeneralized beyond their study conditions.

M5 must refresh model-specific evidence before technology selection, and M10
must refresh statistical guidance before the analysis-plan freeze.
