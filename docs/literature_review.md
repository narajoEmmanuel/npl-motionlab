# M2 Targeted Literature Review

## Document control

| Field | Value |
|---|---|
| Milestone | M2, Literature & Measurement Framework |
| Review type | Targeted engineering scoping review |
| Original search date | 2026-09-06 |
| Scope interpretation updated | 2026-09-16 |
| Status | Evidence baseline, interpreted under simplified Core scope |

## Review purpose

This review informed the original measurand, camera controls, reference options,
agreement concepts, and uncertainty framing. The evidence remains useful, but
the Core project was later simplified so that manual-reference validation,
formal uncertainty analysis, and robustness experiments are no longer blocking
milestones.

The traceable extraction remains in
[`references/literature_matrix.csv`](../references/literature_matrix.csv), and
bibliographic metadata remains in
[`references/references.bib`](../references/references.bib).

## Findings retained from the original review

### Markerless performance is context dependent

The reviewed literature shows substantial variation across pose systems, tasks,
planes, joints, camera configurations, and statistical methods. Favorable
results from one system or study cannot be transferred as proof of MotionLab
performance.

**Current MotionLab implication:** keep the project claim narrow. MotionLab will
characterize only the explicitly selected Sports2D-based workflow under one
controlled single-camera squat setup.

### A 2D projected measurand is defensible but deliberately limited

Reviewed work supports the usefulness of low-cost 2D sagittal measurements in
bounded settings while also showing that they are not interchangeable with 3D
motion capture.

**Current MotionLab implication:** retain the 2D projected sagittal-plane knee
flexion angle and prohibit unqualified anatomical 3D or clinical claims.

### Manual video measurement can be useful, but it is not ground truth

The reviewed manual-digitization literature indicates that same-video 2D manual
measurements can be repeatable under defined conditions, while operator,
landmark, placement, resolution, and semantic choices can still contribute to
differences.

**Current MotionLab implication:** Kinovea remains a reasonable optional manual
comparison method, but a manual-reference experiment is no longer required to
finish the Core project.

### Camera configuration is an influence quantity

The literature supports the general conclusion that camera viewpoint,
projection, occlusion, and acquisition conditions can affect derived 2D joint
angles.

**Current MotionLab implication:** use one fixed practical baseline rather than
attempting to validate all camera conditions. Existing M4 evidence supports
centered horizontal framing under the tested setup. Systematic robustness work
is deferred.

### Agreement is not correlation

Difference-based comparison remains the correct conceptual approach if MotionLab
later compares its output with an independent manual method. Correlation alone
would not establish agreement.

**Current MotionLab implication:** this principle is retained for the optional
Kinovea appendix. It does not create a mandatory Bland-Altman or agreement
analysis requirement for the Core.

### Formal uncertainty analysis requires justified inputs

JCGM guidance remains relevant to any future full uncertainty study. Monte Carlo
propagation is only meaningful when input distributions and dependencies are
justified.

**Current MotionLab implication:** full GUM-style uncertainty and Monte Carlo
work are deferred. Hypothetical pixel perturbations may be used as optional
sensitivity demonstrations but must not be presented as measured uncertainty.

## Updated M2 engineering decisions

1. **Retain one narrow measurand.** The project remains centered on the 2D
   projected sagittal-plane knee flexion angle.
2. **Reuse a mature pose engine.** MotionLab should not build pose estimation
   from scratch when Sports2D/RTMPose already supplies that capability.
3. **Keep the camera setup fixed instead of fully characterizing it.** Existing
   M4 evidence is enough to select a practical centered baseline for the Core.
4. **Make Kinovea optional.** Manual same-video comparison may be added after
   Core completion if it provides additional value.
5. **Keep the Core analysis descriptive.** Five independent controlled trials
   are sufficient for the bounded engineering demonstration now selected.
6. **Defer uncertainty and robustness programs.** They remain scientifically
   valid future extensions but are not needed to complete MotionLab.

## Evidence gaps that remain acceptable under the simplified scope

- the exact future Sports2D configuration has not yet been integrated;
- no Core human squat dataset has yet been processed end to end;
- no independent reference comparison is required or currently available;
- camera behavior outside the selected bounded setup is not characterized;
- no full uncertainty budget exists;
- no population-level inference is intended.

These are limitations to report, not reasons to keep expanding the Core.

## Current evidence boundary

The literature does not validate MotionLab itself. It supports the design logic
for a narrow single-camera 2D engineering workflow and justifies conservative
claim boundaries.

The final MotionLab conclusion must be based on the repository's own verified
software and the controlled trials actually executed, while clearly separating
those results from external literature.

## Relationship to the roadmap

The current completion plan is defined in [`roadmap.md`](roadmap.md) and
[`ADR-0003-simplified-core-scope.md`](decisions/ADR-0003-simplified-core-scope.md).
Where the original M2 plan expected mandatory manual-reference, uncertainty, or
robustness milestones, the later accepted scope decision governs.
