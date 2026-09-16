# ADR-0003: Simplified Core scope and completion path

## Document control

| Field | Value |
|---|---|
| Status | Accepted |
| Decision date | 2026-09-16 |
| Scope | Core project completion strategy |
| Supersedes | Parts of ADR-0002 that made manual reference, extended camera characterization, and later uncertainty/robustness work part of the critical path |

## Context

MotionLab has already completed its environment, requirements baseline,
literature framing, mathematical verification, and a bounded camera/image
characterization sequence. The project also has a verified angle implementation,
image-coordinate handling, source-video metadata inspection, and M4-D evidence
supporting centered horizontal framing under the tested setup.

The previous roadmap continued toward a large validation program involving a
mandatory manual reference workflow, extensive camera-factor characterization,
full uncertainty analysis, Monte Carlo propagation, and robustness experiments.
Those activities can be scientifically useful, but they are not necessary to
answer the narrower engineering question now selected for the Core project.

Mature external tools already provide pose estimation, tracking, video handling,
and related processing. Rebuilding those capabilities would add complexity
without materially improving the Core conclusion.

## Decision

MotionLab is reduced to a compact measurement-engineering integration and
characterization project.

The Core shall:

1. preserve source-video provenance and acquisition metadata;
2. reuse one pinned Sports2D/RTMPose workflow to obtain pixel landmarks;
3. map hip, knee, and ankle outputs into MotionLab landmark roles;
4. compute the authoritative project angle with verified MotionLab geometry;
5. demonstrate one complete representative-video workflow;
6. process a small controlled set of five independent one-squat video trials;
7. summarize observed within-protocol behavior with simple descriptive metrics;
8. publish a bounded engineering conclusion and reproducible release.

The Core shall not require a second pose engine, a manual-reference method,
general camera calibration, a full uncertainty budget, Monte Carlo propagation,
or robustness-factor experiments.

## M4 closure

M4 is considered complete under the simplified scope. Existing evidence is
sufficient to support one fixed baseline configuration for the bounded Core
experiment. The evidence supports only the tested image-coordinate behavior and
a provisional preference for centered horizontal framing. It does not establish
general camera accuracy or setup robustness.

## Sports2D role

Sports2D is the selected external pose-engine workflow for the next milestone.
Its detector, tracker, video processing, visualization, interpolation,
outlier-handling, and filtering capabilities are external implementation details
unless a specific Core problem requires one of them.

MotionLab remains responsible for:

- version/configuration provenance;
- explicit landmark-role mapping;
- preserving pixel coordinate meaning;
- missing/invalid landmark handling;
- the authoritative project angle calculation;
- project-specific outputs and interpretation.

The initial workflow should avoid optional processing unless it is needed to
produce a stable, interpretable Core result.

## Kinovea decision

Kinovea is no longer a mandatory reference milestone.

A small Kinovea comparison may be performed only after the Core is complete if
it materially improves the technical report or portfolio evidence. If used, it
remains a characterized manual comparison method, not ground truth.

## MATLAB decision

The MATLAB work is retained as an **Optional Advanced Verification Appendix**.
The separate MATLAB branch and its independent angle implementation,
sensitivity code, experimental-analysis code, and Python-to-MATLAB
cross-verification framework may be completed later.

MATLAB runtime execution is not required for the Core release and must not block
M5 through M9.

## Deferred work

The following are explicitly outside the Core critical path:

- generalized intrinsic/lens calibration;
- systematic yaw, pitch, roll, height, distance, and multi-device studies;
- multiple pose-engine benchmarking;
- multiple participants or population inference;
- full manual-reference validation;
- full GUM-style uncertainty budgets;
- Monte Carlo uncertainty propagation;
- robustness matrices;
- 3D or multi-camera reconstruction;
- OpenSim or inverse-kinematics workflows;
- clinical or diagnostic interpretation;
- accreditation and teaching-module expansion.

These may be added only through a new documented scope decision.

## Consequences

### Positive

- the project can reach a technically coherent conclusion with much less custom
  software and experimental overhead;
- existing verified MotionLab code retains a clear purpose;
- external mature tools are reused instead of duplicated;
- the final claim becomes easier to defend because it is narrower;
- optional advanced work remains available without blocking completion.

### Trade-offs

- the Core will not establish agreement with an independent reference method;
- the Core will not establish general camera robustness;
- the Core will not support a full measurement-uncertainty claim;
- the final result must therefore be described as a bounded engineering
  characterization of one controlled workflow, not a validation against truth.

## Scope-control rule

A new task enters the Core only when it is required to run or interpret the
end-to-end workflow, cannot reasonably be supplied by an existing mature tool,
and would materially weaken the final conclusion if omitted.

Otherwise it remains optional or future work.
