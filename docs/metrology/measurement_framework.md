# Measurement Framework

## Purpose

This document defines the conceptual measurement model for M2. It establishes
what enters the system, what is reported, which quantities can influence the
result, and which claims each validation layer may support. M3 will provide the
formal geometric derivation and verified numerical implementation.

## Measurement result

The reported quantity is a 2D projected sagittal-plane knee flexion angle in
degrees, accompanied eventually by relevant quality information and an
uncertainty statement appropriate to the intended use.

For image-plane hip, knee, and ankle coordinates, the conceptual model is:

```math
\theta_{flex} = f(x_H, y_H, x_K, y_K, x_A, y_A; I, C, P, M, R)
```

where:

- `H`, `K`, and `A` are projected proximal, knee, and distal landmark roles;
- `I` represents image dimensions and coordinate conversion;
- `C` represents camera and projection conditions;
- `P` represents processing and frame-selection decisions;
- `M` represents pose-model identity, version, and landmark semantics;
- `R` represents the reference procedure when a comparison is reported.

The six point coordinates are direct computational inputs, but they are not the
complete measurement model. The additional quantities determine how those
coordinates arose and how the result can be interpreted.

## Coordinate domains

MotionLab shall distinguish:

1. normalized model coordinates;
2. pixel coordinates tied to image width and height;
3. optional corrected image coordinates if lens correction is later justified;
4. derived segment vectors and angles;
5. reference-marker coordinates acquired independently from the same frame.

Normalized `x` and `y` values cannot be treated as isotropically scaled unless
that property is demonstrated. The default computational route converts them
to pixel coordinates before Euclidean geometry. M3–M4 will verify this with
analytical and image-based cases.

## Working angle convention

The geometric included angle is formed by vectors from the projected knee point
to the projected hip and ankle points. The reported flexion angle is the
supplement of that included angle, giving 0° in projected full extension and
increasing positive flexion.

This convention is documented but not yet V1/V2 verified. M3 must derive it,
define its range, set numerical tolerances, and handle degenerate segments.

## Measurement chain

```text
controlled movement and camera configuration
→ encoded source video and metadata
→ decoded frame and image dimensions
→ raw markerless landmarks
→ coordinate-domain conversion
→ raw projected angle and quality flags
→ predefined optional processing
→ traceable reported markerless result
```

The independent comparison chain is:

```text
same source video and frame
→ visible reference-marker digitization
→ reference coordinates
→ identical verified angle convention
→ characterized reference result
→ paired difference: markerless − reference
```

Using the same video controls timing and camera realization, but does not remove
landmark-semantic mismatch, digitization error, placement error, or shared
projection limitations.

## Influence quantities and current evidence state

| Category | Examples | Current state | Planned treatment |
|---|---|---|---|
| Landmark localization | coordinate noise, occlusion, model confidence | Unquantified | M6 pilot characterization |
| Landmark semantics | model joint definition versus visible marker center | Unquantified | M5–M7 mapping and sensitivity |
| Image geometry | width, height, aspect ratio, crop, rotation | Defined, unverified | M3–M4 analytical/image tests |
| Camera pose | yaw, pitch, roll, height, distance | Literature-supported influence | M4 control; M15 selected robustness |
| Optics | lens, distortion, digital zoom, stabilization | Uncharacterized | M4 device inspection and tests |
| Timing | frame rate, variable frame rate, timestamps, frame selection | Uncharacterized | M4 and M8 metadata handling |
| Processing | missing data, interpolation, smoothing, event selection | Not selected | Predefine after pilot; preserve raw |
| Reference | placement, center identification, rater, resolution | Candidate only | M7 repeatability and uncertainty |
| Trial hierarchy | subject, session, trial, frame | Conceptually defined | M9 pilot; M10 SAP freeze |

No numerical probability distribution is assigned at M2.

## Validation claim boundaries

| Layer | Evidence produced | Claims allowed | Claims not allowed |
|---|---|---|---|
| A — analytical/software | known geometry and unit-test results | Formula and implementation correctness | Camera, pose, or human validity |
| B — physical/camera | known planar geometry under image acquisition | Camera/image behavior for tested conditions | Human landmark validity |
| C — reference | repeatability and limitations of manual reference | Reference fitness for stated comparison | Error-free ground truth |
| D — baseline | paired controlled human trials | Agreement and repeatability for tested baseline | Robustness or general clinical validity |
| E — robustness | controlled factor variations | Sensitivity within tested levels | Performance outside tested ranges |

## Candidate comparison quantities

For paired markerless estimate `m_i` and reference result `r_i`, define the
signed difference conceptually as:

```math
d_i = m_i - r_i
```

Candidate summaries include signed error, absolute error, bias, MAE, RMSE,
standard deviation of differences, failure rate, and limits of agreement.
Selection, estimands, confidence intervals, clustering, and interpretation are
deferred to the M10 statistical analysis plan. Correlation and R² may describe
association but cannot establish agreement.

## Traceability model

Every future reported value should be traceable to:

- subject or synthetic-object identifier;
- session and independent trial;
- source-video identifier and file checksum;
- frame number and timestamp where available;
- acquisition configuration and device metadata;
- pose engine, model, and software versions;
- raw landmark record and quality state;
- reference record and operator where applicable;
- processing configuration and code revision;
- derived result, figure, or table identifier.

The specific schemas and file layout belong to M8.

## Uncertainty strategy

M13 will construct an uncertainty budget consistent with JCGM guidance. Each
contribution must be classified as experimentally quantified, literature
informed, instrument specified, estimated, modeled, exploratory, or
unquantified. Correlation among inputs and systematic effects must be considered.

M14 may use Monte Carlo propagation for nonlinear geometry or non-Gaussian
inputs. Until empirical inputs exist, pixel-error simulations are labeled
exploratory sensitivity analyses and cannot support a V5 claim.

## Deferred decisions

- pose-estimation technology and model configuration: M5;
- final landmark-to-reference semantic mapping: M5–M7;
- exact camera baseline and allowable setup tolerances: M4, then M10;
- missing-landmark and smoothing policy: M6 and pilot, frozen at M10;
- event or frame-selection rule: pilot and M10;
- statistical estimands and primary metrics: M10;
- numerical acceptance criterion: M10 with documented provenance;
- robustness factors and levels: after baseline evidence, M15.

## Failure modes to carry forward

- zero-length or coincident landmark segments;
- incorrect normalized-to-pixel conversion;
- rotation or aspect-ratio metadata ignored;
- out-of-plane movement and perspective bias;
- left/right identity swaps or occlusion;
- reference marker/model landmark semantic mismatch;
- rater-dependent marker center selection;
- frames treated as independent replicates;
- filtering selected after inspecting favorable results;
- reference differences mislabeled as error against truth.
