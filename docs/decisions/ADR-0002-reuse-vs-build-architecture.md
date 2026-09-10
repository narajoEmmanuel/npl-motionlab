# ADR-0002: Reuse-versus-build architecture for the MotionLab pipeline

## Document control

| Field | Value |
|---|---|
| Status | Proposed; no integration authorized by this record |
| Decision date | 2026-09-09 |
| Scope | Architecture review between M4 and M5 |
| Evidence boundary | Repository inspection and primary-source technology review |
| Excluded work | M5 implementation, new M4 experiments, changes to existing evidence |

## 1. Decision summary

MotionLab should be an integration and measurement-validation system, not a new
pose-estimation or camera-calibration library.

The recommended architecture is:

```text
immutable source video
        |
        v
MotionLab provenance, metadata, timebase, and acquisition QC
        |
        +--------------------> immutable original frames
        |
        v
matched OpenCV camera calibration
        |
        v
Sports2D pose engine behind a versioned adapter boundary
        |
        v
raw engine keypoints, scores, identities, and frame links
        |
        v
MotionLab coordinate adapter and optional OpenCV point rectification
        |
        v
MotionLab verified angle geometry
        |
        v
MotionLab squat segmentation, QC, exclusions, statistics, and reporting

Kinovea (separate workflow) --> independent M7 reference evidence
```

Sports2D is the strongest current automatic workflow candidate, but MotionLab
should use **Option B: Sports2D keypoints -> MotionLab geometry**, not accept
Sports2D angles as the authoritative measurand. This preserves the verified
MotionLab angle convention, exposes semantic and coordinate transformations,
and permits independent tests.

Sports2D should initially be **wrapped in an isolated, pinned execution
environment**, rather than copied or tightly imported into the core package.
This isolates its fast-moving model stack, a Git-pinned transitive dependency,
and current process-wide configuration side effects. Kinovea should remain an
external reference tool. OpenCV should remain a direct dependency and provide
the calibration mathematics. MediaPipe is a useful alternate-engine candidate,
not a second mandatory production engine.

This record proposes architecture. It does not complete M4, begin M5, select a
validated pose model, or establish measurement performance.

## 2. Repository state and tests

The review began on `main`, aligned with `origin/main`, at commit `c400f04`
(`feat: complete M4-D horizontal position analysis`). The only working-tree
item was the pre-existing untracked file `scripts/manual_digitize_m4.py`; it was
not modified or staged. The complete existing suite passed: **59 tests passed**.

Existing M4 evidence remains intact. It supports physical-image verification
and a provisional preference for centered framing under the tested setup. It
does not validate a pose engine, establish camera accuracy or total uncertainty,
or close M4.

## 3. Existing MotionLab capabilities that should remain

| Existing asset | Responsibility to retain |
|---|---|
| `motionlab.geometry` | Verified generic included-angle geometry and explicit invalid-geometry handling |
| `motionlab.image_geometry` | Explicit normalized-to-pixel conversion using decoded width and height |
| `motionlab.video_metadata` | Source hashing and conservative OpenCV metadata inspection with documented limits |
| M4 acquisition records and reports | Physical evidence, immutable provenance, setup limitations, and camera/image-position observations |
| Requirements and project charter | Measurand, raw-first policy, evidence layers, privacy, and claim boundaries |
| Test conventions | Executable support for mathematical and software claims |

These components are small, project-specific, already verified, and provide the
traceability boundary that general-purpose tools do not.

## 4. Technologies investigated

The primary review covered Sports2D, Kinovea, OpenCV, and MediaPipe. RTMLib and
Pose2Sim were also examined because they are mature, directly relevant members
of the Sports2D dependency and biomechanics ecosystem. Small demonstration
repositories were intentionally excluded.

The source state described here is the state observable on 2026-09-09. Exact
versions, commits, model files, and resolved dependencies must be frozen again
at any implementation checkpoint.

## 5. Capability comparison

Legend: **Yes** means native support; **Partial** means limited or indirect;
**No** means it is outside the project's practical role.

| Capability | Sports2D | Kinovea | OpenCV | MediaPipe Pose Landmarker |
|---|---:|---:|---:|---:|
| Video ingestion | Yes | Yes | Yes | Adapter required |
| Metadata inspection | Partial | Partial | Yes, backend-dependent | No |
| Intrinsic calibration | No | Yes, GUI workflow | Yes | No |
| Radial/tangential correction | No | Yes, GUI workflow | Yes | No |
| Planar/perspective calibration | No | Yes, GUI workflow | Yes | No |
| Automatic pose estimation | Yes | No | No | Yes |
| Hip/knee/ankle keypoints | Yes | Manual/tracked points | No | Yes |
| Joint angles/time series | Yes | Yes | Geometry primitives only | No final biomechanics convention |
| Multiple people | Yes | Manual/tracking workflow | No | Configurable pose count |
| Tracking | Yes | Yes | Generic primitives | Video/live tracking |
| Filtering/smoothing | Yes | Yes | Generic signal primitives | Internal tracking; no MotionLab policy |
| Annotated video | Yes | Yes | Building blocks | Landmarks returned for rendering |
| CSV export | Yes | Yes | No domain export | Adapter required |
| JSON export | Config/adapter required | KVA is XML | Adapter required | In-memory result objects |
| Direct Python API | Yes | No | Yes | Yes |
| CLI automation | Yes | Launch-oriented only | Library/sample tools | Adapter required |
| Manual reference measurement | No | Yes | Building blocks only | No |
| Headless pipeline suitability | Yes | Poor | Yes | Yes |

Sources: Sports2D documents `Sports2D.process(config_dict)`, TOML configuration,
CLI operation, models, exports, and headless display controls.[^sports2d-readme]
Kinovea documents its measurement, calibration, trajectory, export, and limited
launch command line.[^kinovea-features][^kinovea-cli] OpenCV documents its
calibration and transformation APIs.[^opencv-calibration][^opencv-transform]
MediaPipe documents image, video, and live-stream modes plus timestamped video
calls and landmark outputs.[^mediapipe-pose]

## 6. Automation classification

| Technology | Classification | MotionLab use |
|---|---|---|
| Sports2D | Direct Python dependency **and** CLI; recommend isolated wrapper first | Automatic pose-engine candidate |
| OpenCV | Direct Python dependency | Decode support, calibration, rectification, transforms |
| MediaPipe | Direct Python dependency if environment compatibility is proven | Alternate pose adapter or benchmark |
| RTMLib | Direct Python dependency | Lower-level fallback if Sports2D policy/output constraints dominate |
| Pose2Sim | Direct Python/CLI package, but designed primarily for multi-camera 3D | Transitive Sports2D component; not a direct Core dependency |
| Kinovea | Windows GUI application with launch parameters, not a headless measurement API | Independent manual/reference workflow |

Kinovea's documented command line opens videos or workspaces and controls
presentation options; it does not expose headless point placement, measurement,
or data export.[^kinovea-cli] Automatic use would therefore require brittle GUI
automation, undocumented KVA manipulation, or source integration. None is
justified for the Core workflow.

## 7. Sports2D deep dive

### 7.1 Models and pose stack

Sports2D currently delegates pose inference to RTMLib/RTMPose and exposes model
families including body, body-with-feet, lower-body, whole-body, and
whole-body-wrist configurations, with backend and device selection. It can also
accept a deployed MMPose model.[^sports2d-readme] Its declared package metadata
supports Python 3.11 and newer and currently pins Pose2Sim from a specific Git
commit rather than solely through a released package.[^sports2d-pyproject]

This is useful functionality but a reproducibility and installation boundary:
MotionLab must pin the Sports2D release/commit, RTMLib, inference backend, model
name, model-file hash, model configuration, and resolved environment.

### 7.2 Programmatic use and configuration

Sports2D supports both:

```python
from Sports2D import Sports2D

Sports2D.process(config_dict)
```

and a TOML/CLI workflow. Configuration covers video input, frame selection,
pose model/mode/backend/device, requested keypoints and angles, interpolation,
outlier rejection, filtering, visualization, and output types.[^sports2d-readme]
It can run without realtime windows or graphs. MotionLab can therefore generate
a frozen configuration and invoke it automatically after upload.

For the first integration, subprocess isolation is preferable to an in-process
import. The current source modifies the process-wide HTTPS context while
handling model downloads, and the processing entry point combines many policies
in one workflow.[^sports2d-entry] Isolation limits dependency and global-state
effects. Model artifacts should be acquired and verified deliberately rather
than downloaded implicitly during a measurement run.

### 7.3 Keypoints, confidence, missingness, and traceability

Sports2D internally obtains per-frame keypoint coordinates and scores, rejects
low-confidence points as missing, and filters persons using configurable point
counts and average confidence. It also tracks people and can interpolate,
reject outliers, and filter trajectories.[^sports2d-process]

Default file outputs are not sufficient by themselves for the MotionLab raw-first
requirement:

- TRC contains coordinate trajectories, not a complete confidence sidecar.
- Coordinates normally reach export after configured processing.
- Confidence scores exist internally but are not a complete documented standard
  output contract.
- Sports2D constructs output time from frame range and an OpenCV-reported,
  rounded FPS; that is not authoritative per-frame timing for variable-frame-rate
  or metadata-problematic phone files.[^sports2d-process][^sports2d-entry]

The adapter must therefore prove how it captures **pre-interpolation,
pre-filtering coordinates and confidence**, records every missing value and
person identity, and links them to MotionLab's frame index and validated time
record. Until that proof exists, Sports2D TRC/MOT output is a useful diagnostic,
not the canonical raw record.

### 7.4 Filtering and smoothing

Sports2D offers interpolation, Hampel-style outlier handling, Butterworth,
Kalman, one-euro, spline, Gaussian, LOESS, median, and related filtering
choices.[^sports2d-readme][^sports2d-process] These should be reused where a
predefined pilot shows that their exact implementation satisfies MotionLab's
requirements. They must not overwrite raw keypoints or raw angles. Configuration
defaults have changed across releases, so MotionLab must set every relied-upon
parameter explicitly rather than inherit defaults.

### 7.5 Knee-angle definition

Sports2D delegates angle definitions and point-to-angle processing to Pose2Sim.
The current definitions use ankle-knee-hip triples for right and left knee
flexion, a signed two-dimensional `atan2(cross, dot)` angle, a `-180` offset,
and wrapping into a signed interval.[^pose2sim-common] Sports2D also applies
image-side/direction transformations before angle evaluation.[^sports2d-process]

That is close in purpose but is not automatically equivalent to MotionLab's
verified unsigned included angle followed by the project-defined flexion
convention. Sign, mirroring, side selection, anatomical landmark semantics,
and the supplement convention are all material.

**Decision: choose Option B.** Preserve Sports2D's calculated angles only as a
diagnostic comparator. Use its raw hip/knee/ankle keypoints through a documented
adapter, then apply `motionlab.geometry` for the authoritative angle. Equivalence
tests with known coordinates and mirrored cases must precede use on validation
data.

### 7.6 Calibration and outputs

Sports2D produces annotated video/images, TRC coordinates, MOT angles, plots,
and optional C3D/OpenSim-oriented artifacts.[^sports2d-readme] It does not supply
the required intrinsic lens-calibration workflow, and its documentation flags
lens-distortion handling as future work. Camera correction remains an OpenCV and
MotionLab responsibility.

## 8. Kinovea deep dive

Kinovea is a mature Windows desktop application for video observation and
measurement. It provides point/line/angle tools, trajectories, calibration,
perspective grids, lens-distortion calibration, annotated video, KVA analysis
files, and spreadsheet exports.[^kinovea-features][^kinovea-calibration]

Its lens workflow stores a camera profile and corrects measured coordinates;
the documentation emphasizes matching camera, lens, resolution, and zoom, and
notes that the displayed image itself is not necessarily redrawn corrected.[^kinovea-lens]
KVA is its native XML-based analysis representation; CSV/spreadsheet export is
available through the GUI, with an important distinction between filtered
kinematics exports and raw-coordinate conversion.[^kinovea-export]

Recommended role:

- **M7:** external independent manual/reference system.
- **M8:** export KVA/CSV evidence into a MotionLab import-and-agreement workflow.
- **Automated production:** no role unless a later requirement justifies the
  cost and licensing review of deeper integration.

The reference protocol must freeze Kinovea version, display scale, landmark
definition, side, frame selection, calibration state, filtering state, operator,
and export route. Private KVA files should be preserved with source-video and
export hashes. Kinovea is a characterized reference method, not ground truth.

## 9. OpenCV camera-calibration recommendation

MotionLab should reuse OpenCV rather than implement camera calibration math.
The relevant maintained APIs include:

| Need | OpenCV function/class | MotionLab adaptation |
|---|---|---|
| Checkerboard detection | `findChessboardCornersSB` | Board definition, image QC, provenance |
| Circle-grid detection | `findCirclesGrid` | Optional board alternative, not required now |
| Subpixel refinement | `cornerSubPix` | Explicit termination criteria and retained inputs |
| Intrinsic calibration | `calibrateCameraExtended` | Persist outputs, diagnostics, and accepted views |
| Reprojection diagnostics | `projectPoints` and per-view errors | Report without inventing a final threshold |
| Sparse point rectification | `undistortPoints` | Preserve original and corrected coordinates |
| Raster undistortion | `undistort` or `initUndistortRectifyMap` + `remap` | Derived visualization/inference comparison only |
| Planar mapping | `getPerspectiveTransform`, `findHomography`, `perspectiveTransform` | Planar M4 target/reference applications only |

These APIs and the underlying camera model are documented by OpenCV.[^opencv-calibration][^opencv-calib3d][^opencv-transform]

A calibration artifact must be a MotionLab record, not an undocumented matrix
file. It should link device, camera, lens/zoom mode, resolution, orientation,
capture application/configuration, board specification, source-image hashes,
OpenCV version and flags, accepted/rejected views, camera matrix, distortion
coefficients/model, extrinsics where retained, per-view errors, aggregate RMS,
and the artifact hash. Thresholds must be justified later from intended use and
evidence, not copied from a tutorial.

For measurement geometry, prefer **sparse keypoint rectification** after pose
inference because it preserves immutable original frames and avoids a second
raster interpolation. Preserve both raw and rectified coordinates. A later
predefined M6 pilot may compare pose inference on original versus undistorted
frames because raster correction can affect model detection.

A planar homography is not a universal correction for a squatting person:
hip, knee, and ankle are not guaranteed to occupy the same physical plane, and
out-of-plane motion is part of the projection limitation. Homography remains
valid for a planar calibration target or other points known to share a plane.

## 10. MediaPipe role

MediaPipe Pose Landmarker exposes 33 normalized and world landmarks, visibility
and presence, optional segmentation, multiple-pose configuration, and distinct
image/video/live-stream APIs. Video calls require timestamps and use tracking to
reduce repeated detection work.[^mediapipe-pose]

It is a defensible alternate-engine adapter or benchmark because it has a
smaller application-policy layer than Sports2D and makes timestamped calls and
confidence-like fields explicit. It should not be installed merely for
redundancy. Current package metadata lists tested Python classifiers through
3.12 rather than MotionLab's required 3.13, and its OpenCV package dependency may
conflict with MotionLab's existing OpenCV distribution.[^mediapipe-pypi] A small
isolated compatibility spike is required before selection.

MediaPipe code licensing does not by itself establish the license of every model
asset. Any selected task/model file must have its source, license, version, and
hash recorded separately.

## 11. Additional mature alternatives

### RTMLib

RTMLib is the Apache-2.0 pose-inference layer already used by Sports2D. It offers
high-level pose trackers and lower-level detector/pose classes, including
RTMPose model families.[^rtmlib-readme] Direct use would expose coordinates and
scores with less Sports2D policy, but MotionLab would then need to build video
orchestration, identity handling, export, filtering integration, and annotation.
It is the best fallback if Sports2D's raw-output contract cannot be made
traceable, not a superior end-to-end choice today.

### Pose2Sim

Pose2Sim is an active BSD-3-Clause biomechanics workflow focused on markerless
multi-camera 3D kinematics. Its own documentation directs single-camera 2D use
toward Sports2D.[^pose2sim-readme] It already appears in the Sports2D stack and
does not justify a separate direct Core dependency.

No mature reviewed project replaces the MotionLab-specific combination of
single-camera provenance, verified project measurand, squat protocol, validation
independence, agreement analysis, uncertainty accounting, and reporting.

## 12. Code-reuse findings

| Repository | Module/function | Useful behavior | Decision |
|---|---|---|---|
| Sports2D | `Sports2D.Sports2D.process` | Configured video-to-pose workflow | WRAP; do not copy |
| Sports2D | `Sports2D.process.process_fun` and helpers | Decode, tracking, pose processing, export, annotation | Use through public entry point; inspect only for adapter contract |
| Pose2Sim | `Pose2Sim.common.angle_dict`, `points_to_angles` | Sports2D angle definitions and signed angle conversion | Diagnostic comparison; do not replace verified MotionLab geometry |
| OpenCV | `calibrateCameraExtended`, `projectPoints` | Intrinsics/distortion and reprojection diagnostics | REUSE directly |
| OpenCV | `undistortPoints`, `remap` | Sparse/raster lens correction | REUSE directly behind provenance-aware adapter |
| OpenCV | `findHomography`, `perspectiveTransform` | Planar coordinate mapping | REUSE only for justified planar geometry |
| MediaPipe | `PoseLandmarker` | Alternate timestamped pose inference | Optional WRAP after compatibility spike |
| RTMLib | `PoseTracker`, RTMPose classes | Lower-level detector/pose/tracker | Fallback WRAP if Sports2D cannot expose required raw data |
| Kinovea | Angle, tracking, calibration, KVA/CSV GUI tools | Independent manual measurement | External tool; import exported evidence only |

Importing or wrapping maintained public APIs is preferable to copying source.
Copying would create version drift, attribution work, patch ownership, and—in
Kinovea's case—material copyleft concerns.

## 13. License review

This is an engineering reading of repository license texts, not legal advice.
Model weights, datasets, codecs, and bundled assets require separate review.

| Project | Repository license | Use/import | Modification/copy/distribution implications |
|---|---|---|---|
| Sports2D | BSD 3-Clause[^sports2d-license] | Permissive dependency use | Source/binary redistributions retain copyright, conditions, and disclaimer; names may not endorse derivatives |
| Kinovea | GPL-2.0[^kinovea-license] | Running an unmodified external program is distinct from incorporating its code | Copying, linking, or distributing derivatives can trigger GPL source/license obligations; keep it process- and file-separated and seek legal review before distributed integration |
| OpenCV | Apache-2.0[^opencv-license] | Permissive direct dependency use | Distributed copies/derivatives must retain the license/notices, mark modified files, and handle any NOTICE; includes an express patent license and termination terms |
| MediaPipe | Apache-2.0[^mediapipe-license] | Permissive dependency use | Same Apache-2.0 notice/change/NOTICE obligations; model assets require separate verification |
| RTMLib | Apache-2.0[^rtmlib-license] | Permissive dependency use | Same Apache-2.0 obligations; verify model-weight terms separately |
| Pose2Sim | BSD 3-Clause[^pose2sim-license] | Permissive dependency use | Retain copyright, conditions, disclaimer, and no-endorsement condition |

MotionLab should maintain a dependency-and-model attribution inventory at each
release. This review authorizes no license changes and copies no third-party
code.

## 14. Maintenance and integration risk

| Project | Current maturity signals | Principal risk |
|---|---|---|
| Sports2D | Published JOSS software paper; active releases and repository; documented CLI/API[^sports2d-joss][^sports2d-releases] | Alpha/fast-moving behavior, changing defaults, model downloads, Git-pinned dependency, incomplete canonical raw confidence/timing export |
| Kinovea | Long-running project, extensive user documentation, current Windows releases[^kinovea-repo][^kinovea-download] | GUI-centric automation and GPL boundary; reference settings can silently affect export |
| OpenCV | Widely maintained core computer-vision library with extensive API documentation | Calibration is easy to run but difficult to characterize; mismatched optical mode invalidates reuse |
| MediaPipe | Maintained Google project and Tasks API documentation | Python 3.13/package compatibility, native dependency footprint, model-asset lifecycle |
| RTMLib | Active specialized repository and documented Python interface | Smaller abstraction scope; model/back-end compatibility and asset provenance |
| Pose2Sim | Active releases and domain documentation | Multi-camera scope is broader than the Core need; transitive-stack complexity |

Visible tests and CI are useful maintenance signals but do not establish coverage
of MotionLab's measurement requirements. MotionLab needs contract, regression,
and numerical-equivalence tests at every adapter boundary.

## 15. Build-versus-reuse matrix

| Component | Choice | Selected responsibility |
|---|---|---|
| Video provenance and immutable-source policy | BUILD | MotionLab |
| Metadata inspection | ADAPT | Existing MotionLab + OpenCV backend, with later evidence-driven decoder additions only |
| Authoritative frame/time index | BUILD | MotionLab decoder contract; do not inherit rounded nominal FPS as truth |
| Acquisition QC | BUILD | MotionLab requirements and traceable decisions |
| Checkerboard/circle detection | REUSE | OpenCV |
| Intrinsic calibration and reprojection | REUSE | OpenCV |
| Lens correction | WRAP | OpenCV functions + MotionLab calibration/provenance record |
| Planar calibration/homography | WRAP | OpenCV, only for actually planar targets/points |
| Pose inference | WRAP | Sports2D/RTMLib, pinned and isolated |
| Raw keypoint representation | BUILD | MotionLab canonical schema and adapter |
| Tracking/person identity | ADAPT | Sports2D output with MotionLab identity/QC rules |
| Joint-angle geometry | BUILD/RETAIN | Existing verified MotionLab geometry |
| Generic interpolation/filter algorithms | REUSE | Sports2D or SciPy after policy validation |
| Raw/processed separation and filter policy | BUILD | MotionLab |
| Squat phase/repetition segmentation | BUILD | MotionLab-specific algorithm |
| Measurement QC and exclusions | BUILD | MotionLab-specific requirements |
| Manual reference | REUSE externally | Kinovea |
| Reference import and traceability | BUILD | MotionLab |
| Agreement statistics | ADAPT | Established statistical methods using existing scientific Python stack |
| Uncertainty budget | BUILD | MotionLab evidence model |
| Plots, CSV/JSON, report | BUILD/ADAPT | MotionLab using existing libraries |
| User workflow/UI | BUILD | MotionLab orchestration over stable contracts |

## 16. Recommended data flow and records

1. **Ingest:** copy or reference the uploaded file without mutation; calculate
   SHA-256; assign source, acquisition, session, and trial identifiers.
2. **Inspect:** record decoded dimensions, codec/backend observations,
   orientation metadata, frame count, and timing limitations. Never convert a
   backend nominal FPS into observed timing without evidence.
3. **Acquisition QC:** apply versioned rules and retain pass/fail/warning reasons.
4. **Select calibration:** match the exact device/camera/lens/zoom/resolution/
   orientation mode. If none exists, retain an explicit uncorrected state.
5. **Decode:** retain sequential frame index and a timestamp/source-time record
   from the chosen decoder. Original video and frames remain immutable evidence.
6. **Infer pose:** invoke a pinned Sports2D environment with an explicit generated
   configuration. Capture tool logs, exit state, versions, configuration hash,
   model hashes, keypoints, scores, missingness, and person identity.
7. **Canonicalize:** map engine landmark names and coordinates into a versioned
   MotionLab schema tied to original decoded pixel coordinates. Preserve the
   untouched engine record.
8. **Rectify points when justified:** apply matched OpenCV calibration to a
   derived coordinate set. Preserve both original and rectified coordinates and
   the calibration artifact identifier.
9. **Calculate raw angle:** select the documented hip/knee/ankle roles and use
   MotionLab's verified geometry and flexion convention. Store invalidity reason,
   not a fabricated number.
10. **Process:** apply only frozen missing-data, interpolation, smoothing, and
    squat-segmentation rules. Each derived series links to its raw series and
    configuration.
11. **QC and exclusions:** retain automated flags and human decisions separately;
    never delete failed trials from the evidence chain.
12. **Analyze and report:** respect trial/session/subject hierarchy, compare the
    automatic system with the independent reference, and produce traceable
    JSON/CSV/plots/report without inflating claims.

## 17. Proposed milestone impact

These are proposals requiring explicit roadmap acceptance; they do not silently
change `docs/requirements.md`.

### M4 — camera and physical-image verification

Keep the existing physical evidence. Mature calibration code does not answer
whether the selected smartphone configuration is sufficiently controlled, how
projection behaves in the intended setup, whether a reusable intrinsic profile
can be acquired, or whether correction materially changes the measurand. M4
should close only under its documented acceptance conditions. Do not add a
calibration experiment solely because OpenCV makes one available.

### M5 — pose engine

Reframe as **pose-engine selection, integration, and canonical-adapter
verification**, not pose inference implementation. Deliver a pinned environment,
model and landmark-semantic record, raw-output contract, frame/time traceability,
confidence/missingness contract, and known-coordinate/fixture tests. Sports2D is
the lead candidate; RTMLib and MediaPipe are bounded fallbacks.

### M6 — pose and angle processing

MotionLab must still independently verify landmark mapping, left/right and
mirror behavior, coordinate scaling, timebase, invalid geometry, raw versus
processed preservation, angle convention, confidence/missing-data policies,
filter effects, and repetition segmentation. A third-party angle plot does not
satisfy these requirements.

### M7 — reference characterization

Adopt Kinovea as the preferred manual reference environment if a short protocol
qualification confirms raw-coordinate export and required controls. Characterize
placement, visibility, frame selection, operator repeatability, resolution,
calibration/filter state, and semantic mismatch. Do not call it ground truth.

### M8 — traceability and agreement plumbing

Define and test linkable schemas for source video, frames, engine raw output,
canonical landmarks, calibration, raw/processed angles, Kinovea/KVA/CSV evidence,
configuration, software/model versions, QC, exclusions, and figures. Agreement
must be evaluated at the correct trial/session hierarchy—not by treating frames
as independent trials—and should include signed differences, limits/intervals
appropriate to the frozen design, repeatability, missing/failure behavior, and
predefined engineering criteria. Correlation is not agreement.

### Later milestones

The unique engineering value remains the controlled acquisition protocol,
provenance, canonical data model, semantics, camera-profile governance,
squat-specific segmentation, QC/exclusions, independent validation, uncertainty
budget, reproducible reporting, and bounded engineering decision.

## 18. Risks and limitations

- A high-performing pose model can still disagree systematically with visible
  manual landmarks because the landmark semantics differ.
- Single-camera projection cannot recover unobserved 3D anatomy; calibration
  corrects lens geometry, not out-of-plane movement.
- Sports2D defaults, angle behavior, and left/right handling have changed across
  releases. Pinning and regression fixtures are mandatory.[^sports2d-releases]
- Smartphone timing and orientation metadata can be ambiguous. Sports2D's
  rounded OpenCV FPS-derived timebase is not an evidence-preserving substitute.
- Filtering can make trajectories look plausible while hiding missingness or
  changing extrema. Raw data and policy provenance are mandatory.
- Pose confidence is model-specific and is not a calibrated probability of
  joint-angle correctness.
- Kinovea measurements are operator- and configuration-dependent and are not an
  independent physical truth merely because another program produced them.
- Camera calibration is configuration-specific. Focus, stabilization, cropping,
  digital zoom, resolution, and computational camera processing may undermine
  profile reuse.
- Dependency and model licenses can differ. A release inventory and, where
  appropriate, legal review remain necessary.
- This architecture review establishes feasibility and allocation of
  responsibility, not validated accuracy, agreement, or uncertainty.

## 19. Functionality no longer planned from scratch

Subject to future adapter verification, MotionLab should not build:

- a neural pose estimator or train a pose model;
- generic multiperson detection/tracking;
- intrinsic camera-calibration solvers;
- radial/tangential distortion mathematics;
- generic planar homography solvers;
- generic interpolation or signal-filter algorithms already available in
  maintained dependencies;
- a manual video digitization desktop application;
- a custom video annotation engine before existing render/export facilities are
  evaluated against requirements.

MotionLab should build only the thin interfaces and the measurement-specific
logic listed in the matrix.

## 20. Smallest next implementation step

Do **not** install or integrate Sports2D in this task. After this ADR is reviewed
and M4's documented gate permits proceeding, the smallest M5 step should be a
time-boxed, non-production **adapter-contract spike** in an isolated environment:

1. pin one Sports2D release and commit plus its resolved dependencies and one
   model artifact hash;
2. use a non-private test video and a generated configuration with interpolation,
   outlier rejection, filtering, graphs, and realtime display explicitly off;
3. prove headless invocation and capture the exact raw coordinate, confidence,
   identity, frame-index, and timing fields before any processing;
4. compare Sports2D diagnostic knee angles with MotionLab geometry on synthetic
   known-coordinate and mirrored fixtures;
5. record incompatibilities without changing the authoritative MotionLab
   measurand or consuming validation data.

The spike has a clear stop decision: continue wrapping Sports2D only if raw
coordinates, scores, identities, and frame links can be exported reproducibly.
Otherwise evaluate direct RTMLib before broadening the architecture. This is the
recommended next action, not work performed by this ADR.

## 21. Consequences

Benefits are minimal custom infrastructure, explicit ownership of the
measurement claim, independent reference evidence, and replaceable pose engines.
Costs are an adapter boundary, isolated dependency management, duplicate storage
of raw and derived coordinates, and deliberate validation of third-party policy.
Those costs are necessary for traceability and are smaller than maintaining a
pose or calibration stack.

## Sources

[^sports2d-readme]: Sports2D, [repository README and usage documentation](https://github.com/davidpagnon/Sports2D), accessed 2026-09-09.
[^sports2d-pyproject]: Sports2D, [`pyproject.toml`](https://github.com/davidpagnon/Sports2D/blob/main/pyproject.toml), accessed 2026-09-09.
[^sports2d-entry]: Sports2D, [`Sports2D/Sports2D.py`](https://github.com/davidpagnon/Sports2D/blob/main/Sports2D/Sports2D.py), accessed 2026-09-09.
[^sports2d-process]: Sports2D, [`Sports2D/process.py`](https://github.com/davidpagnon/Sports2D/blob/main/Sports2D/process.py), accessed 2026-09-09.
[^sports2d-license]: Sports2D, [BSD 3-Clause license](https://github.com/davidpagnon/Sports2D/blob/main/LICENSE), accessed 2026-09-09.
[^sports2d-releases]: Sports2D, [release history](https://github.com/davidpagnon/Sports2D/releases), accessed 2026-09-09.
[^sports2d-joss]: Pagnon et al., [“Sports2D: Compute 2D human pose and angles from video”](https://doi.org/10.21105/joss.06849), *Journal of Open Source Software* 9(102), 2024.
[^pose2sim-common]: Pose2Sim, [`Pose2Sim/common.py`](https://github.com/perfanalytics/pose2sim/blob/main/Pose2Sim/common.py), accessed 2026-09-09.
[^pose2sim-readme]: Pose2Sim, [repository README](https://github.com/perfanalytics/pose2sim), accessed 2026-09-09.
[^pose2sim-license]: Pose2Sim, [BSD 3-Clause license](https://github.com/perfanalytics/pose2sim/blob/main/LICENSE), accessed 2026-09-09.
[^kinovea-features]: Kinovea, [Features](https://www.kinovea.org/features.html), accessed 2026-09-09.
[^kinovea-calibration]: Kinovea, [Calibration documentation](https://www.kinovea.org/help/staging/measurement/calibration.html), accessed 2026-09-09.
[^kinovea-lens]: Kinovea, [Lens-distortion documentation](https://www.kinovea.org/help/staging/measurement/lensdistortion.html), accessed 2026-09-09.
[^kinovea-export]: Kinovea, [Data export documentation](https://kinovea.org/help/en/export/data.html), accessed 2026-09-09.
[^kinovea-cli]: Kinovea, [Command-line documentation](https://www.kinovea.org/help/staging/misc/command_line.html), accessed 2026-09-09.
[^kinovea-license]: Kinovea, [GPL-2.0 license](https://github.com/Kinovea/Kinovea/blob/master/license.md), accessed 2026-09-09.
[^kinovea-repo]: Kinovea, [source repository](https://github.com/Kinovea/Kinovea), accessed 2026-09-09.
[^kinovea-download]: Kinovea, [official releases/download page](https://www.kinovea.org/download/), accessed 2026-09-09.
[^opencv-calibration]: OpenCV, [camera calibration tutorial](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html), accessed 2026-09-09.
[^opencv-calib3d]: OpenCV, [`calib3d` API reference](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html), accessed 2026-09-09.
[^opencv-transform]: OpenCV, [geometric image transformations](https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html), accessed 2026-09-09.
[^opencv-license]: OpenCV, [Apache-2.0 license](https://github.com/opencv/opencv/blob/4.x/LICENSE), accessed 2026-09-09.
[^mediapipe-pose]: Google AI Edge, [Pose Landmarker for Python](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python), accessed 2026-09-09.
[^mediapipe-pypi]: Python Package Index, [MediaPipe package metadata](https://pypi.org/project/mediapipe/), accessed 2026-09-09.
[^mediapipe-license]: MediaPipe, [Apache-2.0 license](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE), accessed 2026-09-09.
[^rtmlib-readme]: RTMLib, [repository README](https://github.com/Tau-J/rtmlib), accessed 2026-09-09.
[^rtmlib-license]: RTMLib, [Apache-2.0 license](https://github.com/Tau-J/rtmlib/blob/main/LICENSE), accessed 2026-09-09.
