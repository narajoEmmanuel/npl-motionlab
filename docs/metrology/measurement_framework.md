# Measurement Framework

## Purpose

This document defines the simplified MotionLab measurement framework adopted on
2026-09-16. It preserves the verified mathematical and traceability concepts
from the earlier framework while removing optional reference, uncertainty, and
robustness work from the Core completion path.

## Reported quantity

The Core reported quantity is a **2D projected sagittal-plane knee flexion
angle** in degrees.

For projected hip, knee, and ankle coordinates in the image plane, the Core
computational relationship is:

```math
\theta_{flex} = g(H, K, A; I)
```

where:

- `H` is the projected hip landmark role;
- `K` is the projected knee landmark role;
- `A` is the projected ankle landmark role;
- `I` represents the coordinate domain and image dimensions required for any
  normalized-to-pixel conversion.

The external pose engine determines how landmark coordinates are obtained.
MotionLab remains responsible for mapping those coordinates into its landmark
roles and computing the project-defined angle.

## Angle convention

The verified generic geometry forms the unsigned included angle between the
knee-to-hip and knee-to-ankle vectors. The project flexion convention is the
supplement of that included angle:

```math
\theta_{flex} = 180^\circ - \alpha_{included}
```

This produces 0° for projected full extension and increasing positive values for
projected flexion.

The value remains an image-plane quantity and must not be presented as a full
anatomical 3D knee joint angle.

## Coordinate domains

MotionLab distinguishes:

1. source-video image dimensions;
2. external pose-engine coordinates;
3. pixel coordinates used for authoritative MotionLab geometry;
4. derived included angle;
5. derived projected flexion angle.

If the external engine supplies normalized coordinates, image width and height
must be applied before Euclidean angle geometry unless equivalence is explicitly
demonstrated for that coordinate convention. Pixel-coordinate outputs are
preferred for the simplified Sports2D integration.

## Core measurement chain

```text
controlled squat and fixed camera setup
→ original encoded video
→ source hash and metadata record
→ Sports2D / RTMPose
→ pixel hip / knee / ankle landmarks
→ explicit MotionLab landmark mapping
→ MotionLab included-angle geometry
→ projected knee-flexion angle
→ compact result + technical figure
```

The Core repeated-trial layer then adds:

```text
five independent one-squat videos
→ same frozen processing configuration
→ one predefined event result per trial
→ descriptive summary across trials
→ bounded engineering conclusion
```

## What the Core is designed to demonstrate

The Core can support claims that:

- the MotionLab angle implementation is analytically verified and unit-tested;
- the image-coordinate conversion behaves as documented in the tested cases;
- a fixed source-to-landmark-to-angle workflow can be reproduced with recorded
  software/model versions and configuration;
- five independent controlled trials were processed under one bounded setup;
- observed within-protocol variation and pipeline failures were described.

The Core cannot establish:

- clinical validity;
- anatomical 3D accuracy;
- equivalence to Vicon or other professional systems;
- population-level performance;
- general camera robustness;
- trueness against an error-free reference;
- a complete measurement-uncertainty budget.

## Influence quantities

Influence quantities still matter, but most are controlled rather than fully
characterized in the simplified Core.

| Category | Core treatment |
|---|---|
| Image dimensions / coordinate conversion | Verified and explicitly handled |
| Camera device / mode | Held fixed and recorded |
| Horizontal framing | Centered based on bounded M4-D evidence |
| Camera pose / distance / height | Kept practically consistent, not systematically characterized |
| Lighting | Kept practically consistent and documented |
| Pose model identity/version | Pinned and recorded |
| Landmark semantics | Explicitly mapped and documented |
| Missing landmarks | Preserved/flagged, never silently fabricated |
| Interpolation/filtering/outlier processing | Disabled initially unless a concrete Core problem justifies use |
| Trial independence | One video trial is the independent repeated unit |
| Frame-level observations | Used within a trial, not counted as independent replicates |

## Event-summary rule

The representative-video step in M6 will be used to choose the simplest stable
predefined squat-event rule for the five Core trials. Once selected, the rule is
frozen before the five-trial dataset is processed.

The event rule must be algorithmic or otherwise explicitly documented. It must
not select a frame because its resulting angle looks favorable.

## Core analysis

The Core analysis is descriptive.

At minimum it reports:

- one predefined event result per independent trial;
- mean;
- standard deviation;
- minimum;
- maximum;
- range;
- missing-landmark or pipeline-failure count;
- one representative full angle time series.

Inferential statistics, ICC, ANOVA, Bland-Altman analysis, confidence intervals,
and formal uncertainty propagation are not mandatory for the Core.

## Traceability

Each Core result should be linkable to:

- source-video identifier;
- source checksum;
- decoded image dimensions;
- acquisition configuration record;
- Sports2D version;
- pose model/configuration identity;
- landmark-output artifact;
- MotionLab code revision;
- event-summary rule;
- derived result and figure.

Identifiable raw human video remains private by default.

## Optional Kinovea comparison

After Core completion, a small subset of Core trials may be manually measured in
Kinovea. If performed, the comparison chain is:

```text
same selected Core video/frame
→ documented Kinovea manual procedure
→ manual projected angle
→ paired difference from MotionLab result
```

This optional comparison may describe agreement with the manual procedure. It
does not make Kinovea ground truth and is not necessary to finish MotionLab.

## Optional Advanced MATLAB Verification Appendix

MATLAB may independently reproduce angle geometry, analytical cases,
deterministic perturbation studies, selected experimental analysis, and
Python-to-MATLAB consistency checks. This appendix supports software/modeling
verification only and does not extend Core biomechanical claims.

## Deferred advanced questions

The following require a later scope decision:

- intrinsic/lens calibration;
- systematic camera perturbation studies;
- multiple pose engines;
- multiple participants;
- manual-reference validation as a main endpoint;
- full uncertainty budgets;
- Monte Carlo propagation;
- robustness matrices;
- 3D reconstruction or musculoskeletal modeling.

## Scope principle

The simplified framework favors a small traceable result over a broad unfinished
validation program. New complexity must demonstrate direct value to the Core
conclusion before it becomes mandatory.
