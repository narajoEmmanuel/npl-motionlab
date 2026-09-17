# ADR-0004: MotionLab Interactive post-Core architecture

## Document control

| Field | Value |
|---|---|
| Status | Accepted |
| Decision date | 2026-09-17 |
| Scope | Post-Core interactive application architecture and local session storage |
| Preserves | NPL MotionLab Core v0.1.0 and M0-M9 evidence |
| Supersedes | No frozen Core measurement decision; this decision governs new post-Core application work only |

## Context

NPL MotionLab Core v0.1.0 established a bounded, traceable single-camera workflow for 2D projected knee flexion. The released Core deliberately uses a compact file-oriented pipeline because its purpose is engineering verification and reproducible evidence, not an end-user application.

Post-Core work now has a different objective. MotionLab should become an interactive local measurement workspace in which an operator can import a video, run the existing pose workflow, inspect landmarks, review measurements, manually correct a landmark when necessary, inspect synchronized graphs and tabular results, and export selected artifacts.

The current private working layout contains historical test videos, Core evidence, external-engine outputs, derived tables and rendered video results under several local paths. That structure is acceptable as frozen evidence but becomes difficult to navigate if used as the operating model for an interactive application.

The new application must therefore improve usability and local data organization without rewriting the released Core, erasing automatic landmark outputs, weakening provenance, or moving frozen evidence merely for cosmetic reasons.

## Decision

Create a distinct post-Core development line named **NPL MotionLab Interactive**. The first planned public release is v0.2.0, but the package version shall not be bumped until the interactive milestones are actually complete.

The released v0.1.0 Core remains the measurement baseline. Existing Core modules and historical evidence are preserved. New application services sit around the Core rather than replacing it.

The application architecture is:

```text
NPL MotionLab Interactive UI
        |
        v
local application API
        |
        v
application services
  - session management
  - measurement orchestration
  - review/corrections
  - media/preview handling
  - results/export
        |
        +----------------------+
        |                      |
        v                      v
frozen MotionLab Core     session storage
        |                 SQLite + filesystem
        v
Sports2D / RTMPose
```

## Frozen Core boundary

The following released responsibilities remain authoritative unless a later explicit measurement ADR changes them:

- source-video provenance and metadata handling;
- the pinned Sports2D/RTMPose integration boundary for the released workflow;
- semantic landmark adaptation;
- verified 2D geometry;
- missing/invalid landmark handling;
- the v0.1.0 projected knee-flexion convention;
- historical M6-M9 result and event definitions.

Existing stable modules are not to be relocated or rewritten solely to make the repository look more symmetrical.

Interactive features may reuse these modules through explicit service boundaries. New measurement definitions may be added beside the existing knee workflow, but they do not retroactively change v0.1.0 conclusions.

## Session as the unit of work

The normal user-facing unit becomes a **MotionLab Session** rather than a set of CSV/JSON files.

A session represents one imported source video and all local state derived from it, including:

- source identity and metadata;
- pose-engine provenance and raw/minimally processed landmark outputs;
- automatic semantic landmarks;
- manual corrections and correction history;
- effective landmarks used for reviewed calculations;
- frame-level measurements;
- event annotations where applicable;
- render/export artifacts;
- processing and code provenance.

CSV, JSON, figures and MP4 files remain useful export or evidence formats, but they are not the primary interactive storage model.

## Storage decision

Use two complementary local storage layers.

**SQLite** stores structured session state such as:

- session/video metadata;
- frame identities/order;
- automatic landmarks;
- manual correction history;
- measurement values and validity state;
- events/annotations;
- artifact registry;
- application provenance.

**Filesystem storage** keeps large or tool-native artifacts such as:

- source video;
- Sports2D outputs;
- preview/cache media;
- rendered overlays;
- CSV/JSON/report exports;
- logs.

Video and other large binary media shall not be stored as SQLite blobs.

This SQLite decision applies only to the interactive application. It does not change the deliberately simple file-based Core v0.1.0 evidence model.

## Automatic and manual landmark model

Physical markers placed on the participant are **visual references for the human operator only**. MotionLab shall not detect those markers automatically as part of this design.

Pose estimation continues to produce automatic landmarks. During review, if an automatic landmark is visibly displaced from the intended reference location, the operator may move that landmark manually.

Automatic coordinates are immutable evidence and must never be overwritten by a correction.

Conceptually:

```text
effective_position =
    latest active manual correction, if present
    otherwise automatic_position
```

The correction model must support provenance and future undo/reset behavior. A correction should retain at least frame, semantic landmark, corrected coordinates, timestamp and relationship to the automatic value. A future implementation may record additional operator notes without making them mandatory.

## Initial semantic landmark set

The first interactive measurement set is bounded to one selected body side and these semantic roles:

- shoulder;
- hip;
- knee;
- ankle;
- toe/forefoot reference.

The external Sports2D field names for shoulder and toe must be verified against the pinned `Body_with_feet` output before I2 implementation. This ADR defines MotionLab semantic roles, not an unverified external column mapping.

## Initial measurement set

The first interactive release targets three image-plane measurements.

### 1. 2D projected knee flexion

Reuse the existing MotionLab convention and verified geometry based on hip-knee-ankle landmarks. The interactive layer must not invent a second knee-angle implementation.

### 2. 2D projected shank-foot angle

Use knee-ankle-toe/forefoot geometry with the ankle as the vertex. The initial name is intentionally geometric. It shall not be described as clinical dorsiflexion until a separate reference convention and evidence justify that interpretation.

### 3. 2D projected trunk inclination

Use the angle between:

```text
Hip -> Shoulder
Hip -> image vertical
```

Both vectors originate at **Hip**. The vertical reference must originate at Hip. The measurement describes projected trunk inclination and must not be called a spine angle or spinal flexion measurement.

## Dependency-aware recalculation

Manual correction should trigger only measurements that depend on the edited landmark for the affected frame.

Initial dependency intent:

```text
shoulder -> trunk
hip      -> knee, trunk
knee     -> knee, shank-foot
ankle    -> knee, shank-foot
toe      -> shank-foot
```

This allows interactive review without rerunning pose estimation or recalculating unrelated frames.

## Interface direction

The target application is a local web-style workspace with:

- React + TypeScript for the interactive UI;
- a local Python API/service boundary, with FastAPI as the initial preferred framework;
- the existing Python measurement code behind that boundary;
- SQLite and local filesystem storage.

The technology choice may be revisited if a concrete implementation constraint appears, but any replacement must preserve the separation between UI, application services and measurement logic.

The final UI should support video playback, frame stepping, zoom, visible landmarks/segments/angles, drag-based correction, synchronized graphs, numeric results, a frame table and exports.

## NPL visual direction

The interface must read as an NPL engineering product rather than a generic SaaS dashboard.

The current MotionLab repository does not contain a formal NPL brand token set, logo system, authoritative color palette or typography specification. Therefore I0 shall not invent authoritative brand colors or fonts.

Until verified NPL assets are supplied, the design direction is limited to principles:

- engineering-first;
- precise and minimal;
- high information density with clear hierarchy;
- restrained decoration;
- video as the primary analysis workspace;
- measurements, validity and provenance as primary information;
- no decorative "AI" aesthetic, gratuitous gradients or fake clinical styling.

I4 must implement a tokenized design system so verified NPL colors, typography and spacing can be inserted without rewriting components.

## Local workspace decision

New interactive work uses a private Git-ignored root:

```text
workspace/
    sessions/
    archive/
    temp/
```

Future sessions may use:

```text
workspace/sessions/<session_id>/
    session.db
    source/
    engine/sports2d/
    cache/
    renders/
    exports/
    logs/
```

Directories are created on demand. The repository shall not be filled with empty scaffolding.

Existing `data/raw/` and `data/derived/` Core evidence remains at its current paths unless a specific reviewed migration later proves safe. Frozen provenance paths are more important than cosmetic reorganization.

## Data migration rule

Before any local artifact is moved, it must be inventoried and classified as one of:

- `CORE_REFERENCED`;
- `ACTIVE_POST_CORE`;
- `HISTORICAL_TEST`;
- `HISTORICAL_RENDER`;
- `TEMPORARY`;
- `UNKNOWN_REVIEW_REQUIRED`.

`CORE_REFERENCED` and `UNKNOWN_REVIEW_REQUIRED` items are not moved automatically. No file is deleted as part of I0.

## Privacy

Human source video, pose outputs tied to human recordings, reviewed landmarks, session databases, rendered results, private inventories and similar derived artifacts remain local and Git-ignored by default.

Public repository changes may document schemas, architecture and synthetic tests only.

## Consequences

### Positive

- the released Core remains defensible and unchanged;
- the user workflow becomes session-oriented instead of file-oriented;
- automatic and manual measurements remain distinguishable;
- manual correction can be fast without sacrificing auditability;
- additional 2D measurements can be added through explicit definitions;
- media organization becomes predictable;
- UI work can proceed without coupling visual components directly to Sports2D files.

### Trade-offs

- a session database introduces migration/schema responsibilities that did not exist in the Core;
- React/FastAPI adds application complexity and a second runtime boundary;
- interactive correction requires careful frame and coordinate mapping between displayed previews and original pixel coordinates;
- the operator remains responsible for judging whether a visual landmark correction is appropriate;
- adding ankle and trunk measurements expands functionality but does not by itself establish biomechanical or clinical accuracy.

## Non-goals for I0

I0 does not implement:

- SQLite schemas or migrations;
- FastAPI endpoints;
- React components;
- manual drag behavior;
- automatic physical-marker detection;
- ankle or trunk calculation code;
- a second pose engine;
- 3D reconstruction;
- clinical interpretation;
- cloud accounts or remote databases.

I0 establishes the architecture, privacy boundary, workspace policy and development sequence only.
