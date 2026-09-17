# NPL MotionLab Interactive Architecture

## Purpose

NPL MotionLab Interactive is the post-Core application layer built on top of the released MotionLab Core v0.1.0. Its purpose is to turn the verified measurement workflow into a local, reviewable workspace where a user can import a video, run the existing pose workflow, inspect measurements, correct clearly misplaced landmarks when necessary, and review synchronized video, graphs, numbers and tables.

This document describes the target architecture. It does not change the released Core measurement claims.

## Product boundary

The released Core remains responsible for the measurement-engineering foundation:

```text
source video
    -> source identity / metadata
    -> Sports2D / RTMPose
    -> pixel landmarks
    -> MotionLab semantic mapping
    -> MotionLab geometry
    -> traceable measurement outputs
```

Interactive adds the application workflow around that pipeline:

```text
Import
  -> Analyze
  -> Review
  -> Correct if needed
  -> Recalculate affected measurements
  -> Inspect results
  -> Export
```

## Target system architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                  NPL MOTIONLAB INTERACTIVE                  │
│                                                              │
│  Import | Analyze | Review | Results | Export               │
│                                                              │
│  Video + landmarks + measurements + graphs + table          │
└──────────────────────────────┬───────────────────────────────┘
                               │
                        local application API
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                    APPLICATION SERVICES                      │
│                                                              │
│ Session | Analysis | Review | Measurements | Media | Export │
└───────────────┬───────────────────────────────┬──────────────┘
                │                               │
                ▼                               ▼
       MotionLab Core                    Session storage
                │                      SQLite + filesystem
                ▼
       Sports2D / RTMPose
```

The UI must not read TRC/CSV files directly as its primary operating model. File parsing and measurement logic belong behind application services.

## MotionLab Session

A session is the unit of work exposed to the user.

Conceptually one session contains:

```text
Session
├── source video identity
├── source metadata
├── pose-engine provenance
├── frame index/order
├── automatic landmarks
├── manual corrections
├── effective landmarks
├── measurements
├── events/annotations
├── artifacts
└── application provenance
```

The session should be reopenable without rerunning pose estimation when the required source and derived artifacts are still available and provenance checks pass.

## Storage model

### SQLite

Structured, editable state belongs in `session.db`.

Planned logical entities include:

```text
sessions
videos
frames
automatic_landmarks
manual_corrections
measurement_definitions
measurement_results
events
artifacts
provenance
```

Exact SQL tables are an I1 implementation decision. I0 freezes responsibilities, not schema syntax.

### Filesystem

Large or tool-native artifacts remain files:

```text
source video
Sports2D output
preview media
thumbnails/cache
rendered overlay video
CSV/JSON exports
logs
```

The database stores identity/path/hash/provenance metadata for those artifacts rather than embedding the binaries.

## Local workspace

New interactive work uses:

```text
workspace/
├── sessions/
├── archive/
└── temp/
```

A future session may be arranged as:

```text
workspace/sessions/<session_id>/
├── session.db
├── source/
├── engine/
│   └── sports2d/
├── cache/
├── renders/
├── exports/
└── logs/
```

Subdirectories are created only when needed. `workspace/` is private and Git-ignored.

Historical Core paths under `data/raw/` and `data/derived/` remain frozen evidence unless a later reviewed migration explicitly proves a move is safe.

## Landmark model

The first interactive scope uses one selected body side and these MotionLab semantic roles:

```text
shoulder
hip
knee
ankle
toe
```

`toe` means the selected toe/forefoot landmark used by the pinned pose model. Its exact external field name must be verified before implementation. The same applies to shoulder mapping.

### Automatic landmarks

Automatic points come from the existing external pose workflow and are immutable evidence.

### Manual corrections

Physical markers are visual aids to the operator. MotionLab does not automatically detect those markers in this scope.

If the operator judges an automatic landmark to be incorrectly placed, the point may be moved manually for that frame.

The original automatic coordinate is retained permanently.

Conceptually:

```text
effective_landmark(frame, role) =
    active manual correction
    if one exists
    else automatic landmark
```

Correction history must support later audit, undo and reset-to-automatic behavior.

## Measurement model

Measurements should be defined by semantic landmark dependencies rather than duplicated hard-coded UI logic.

### Knee flexion

```text
Hip -> Knee -> Ankle
```

The released MotionLab projected-flexion convention remains authoritative:

```text
projected flexion = 180 deg - included segment angle
```

Interactive must call the existing verified geometry rather than create a second formula.

### Shank-foot angle

```text
Knee -> Ankle -> Toe
```

The ankle is the vertex. The initial output is named **2D projected shank-foot angle**. It is not automatically equivalent to clinical dorsiflexion.

### Trunk inclination

```text
            Shoulder
               ●
              /
             / θ
            /
         Hip ●
             │
             │ vertical reference
```

The two reference vectors originate at Hip:

```text
Hip -> Shoulder
Hip -> image vertical
```

The intended output is **2D projected trunk inclination**. It is not a spine-angle or spinal-flexion measurement.

## Dependency graph

The initial recalculation graph is:

```text
shoulder -> trunk inclination
hip      -> knee flexion, trunk inclination
knee     -> knee flexion, shank-foot angle
ankle    -> knee flexion, shank-foot angle
toe      -> shank-foot angle
```

A manual edit should recalculate only affected measurements for the affected frame. Pose inference is not rerun when a point is manually corrected.

## Coordinate contract for the UI

Source measurements remain in original decoded pixel coordinates.

The UI may display a scaled preview for performance, but manual drag coordinates must be transformed back into original-image coordinates before they are persisted.

For original dimensions `(W, H)` and displayed image dimensions `(w, h)`:

```text
x_original = x_display * W / w
y_original = y_display * H / h
```

The implementation must also account for any explicit letterboxing/padding before using this relationship. The UI may not silently crop, rotate, mirror or stretch the measurement coordinate system.

## User workflow

The intended primary flow is:

```text
New Session
    -> Import Video
    -> Select side / supported analysis options
    -> Run Analysis
    -> Review Video
    -> Correct landmarks only where needed
    -> Inspect measurements
    -> Inspect synchronized graphs/table
    -> Export selected artifacts
```

The normal user should not need to manually locate TRCs, provenance JSONs or CSVs.

## Review workspace

The future review screen should contain three synchronized areas.

### Video workspace

- video playback;
- frame-by-frame navigation;
- zoom/pan as needed;
- visible semantic landmark points;
- connecting segments;
- angle overlays;
- drag/edit mode;
- reset/undo controls;
- validity/correction status.

### Measurement inspector

At minimum show current-frame values for:

```text
Knee flexion
Shank-foot angle
Trunk inclination
```

It should make invalid measurements explicit rather than substituting values.

### Results area

- synchronized time/frame curves;
- current-frame cursor;
- frame-level table;
- status and manual-edit indicators;
- useful session-level summary values;
- provenance access.

Selecting a table row or graph position should navigate the video to the corresponding frame.

## UI technology direction

The initial target stack is:

```text
React + TypeScript
        |
        v
local FastAPI service
        |
        v
MotionLab Python application services / Core
        |
        v
SQLite + filesystem
```

This is intentionally local-first. No cloud backend, authentication service or paid API is required for v0.2.

## NPL design direction

The interface should communicate measurement engineering rather than generic dashboard software.

Design principles:

- engineering-first;
- compact and precise;
- strong visual hierarchy;
- high information density without clutter;
- video is the primary canvas;
- measurements, validity and provenance are visually prominent;
- secondary chrome is restrained;
- correction state is obvious;
- error/invalid states are never hidden.

Avoid:

- decorative AI/neon aesthetics;
- gratuitous gradients;
- oversized KPI-card layouts that reduce working space;
- fake clinical/diagnostic language;
- design choices that make precision harder to inspect.

No formal NPL color/font token system is present in the current repository. I4 should implement CSS/design tokens and only assign authoritative NPL brand values once verified assets or brand guidance are available.

## Data lifecycle

The application should distinguish at least:

```text
source video
external pose output
automatic MotionLab semantic landmarks
manual corrections
effective reviewed landmarks
measurement results
render/export artifacts
```

No derived layer silently replaces its source layer.

## Export model

Exports are outputs of the session, not the database of record.

Expected export classes include:

- measurements CSV;
- landmarks CSV;
- session/provenance JSON;
- figures;
- rendered overlay MP4.

Export formats must retain enough identity to be linked back to the source session and measurement definitions.

## Privacy

Human source media and private derived session state remain local by default.

The public repository may contain:

- schemas;
- synthetic fixtures;
- application code;
- public architecture documentation.

It must not contain identifiable source video, private session databases, pose outputs tied to human recordings, reviewed human landmarks or rendered private results unless publication is explicitly reviewed later.

## Implementation sequence

The architecture is developed through bounded milestones:

```text
I0 Architecture & local data organization
I1 Session model / SQLite
I2 Measurement model
I3 Local API
I4 NPL workspace UI
I5 Interactive landmark review
I6 Results workspace
I7 Render / export
I8 Verification
I9 v0.2 release
```

See `docs/interactive_roadmap.md` for exit criteria.

## Current I0 boundary

I0 documents architecture and storage policy, adds the ignored workspace boundary, and inventories private local artifacts. It does not implement the session database, UI, new angle calculations or manual correction behavior.
