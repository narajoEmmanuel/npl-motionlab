# NPL MotionLab Interactive Roadmap

## Status

MotionLab Core v0.1.0 is complete and remains the released measurement baseline.

MotionLab Interactive is a separate post-Core development line intended to turn the verified pipeline into a local review workspace without rewriting the frozen Core.

## Milestones

| Milestone | Scope | Exit condition | Status |
|---|---|---|---|
| I0 | Architecture & local data organization | ADR accepted, workspace policy defined, private inventory completed, Core boundary preserved | Complete |
| I1 | Session model / SQLite | Session lifecycle and schema implemented/tested locally | Complete |
| I2 | Measurement model | Knee reuse plus verified shank-foot and trunk definitions with synthetic tests | Complete |
| I3 | Local API | Stable local service contract exposes session, analysis, review and result operations | Complete |
| I4 | NPL workspace UI | Import/run/review shell, player and tokenized NPL-oriented design system | In progress |
| I5 | Interactive landmark review | Drag correction, audit history, undo/reset and dependency-aware recalculation | Not started |
| I6 | Results workspace | Synchronized numbers, graphs and frame table | Not started |
| I7 | Render / export | Session-linked CSV/JSON/figure/MP4 exports | Not started |
| I8 | Verification | Synthetic coverage plus one private end-to-end reviewed session | Not started |
| I9 | v0.2 release | Documentation, clean public boundary, tests and tagged release | Not started |

## I0: Architecture & local data organization

I0 establishes the post-Core application architecture before feature implementation.

Required outcomes:

- preserve MotionLab Core v0.1.0 behavior and evidence;
- define MotionLab Session as the future unit of work;
- adopt SQLite for structured interactive state and the filesystem for large/tool-native artifacts;
- adopt a private `workspace/` root for new interactive analyses;
- inventory existing local video/derived artifacts before moving anything;
- classify local artifacts as `CORE_REFERENCED`, `ACTIVE_POST_CORE`, `HISTORICAL_TEST`, `HISTORICAL_RENDER`, `TEMPORARY`, or `UNKNOWN_REVIEW_REQUIRED`;
- do not delete local artifacts during I0;
- do not move Core-referenced evidence;
- record the architecture in ADR-0004 and `docs/interactive_architecture.md`;
- preserve privacy and provenance boundaries.

I0 does not implement the database, API, UI, new measurement code or manual corrections.

## I1: Session model / SQLite

Implement a local session service and schema for structured state such as:

- session/video identity;
- frames;
- automatic landmarks;
- manual correction history;
- measurement results;
- events;
- artifact registry;
- provenance.

Large source/derived media remain files. No video blobs in SQLite.

## I2: Measurement model

Keep existing projected knee flexion authoritative and add two explicit image-plane definitions:

### 2D projected shank-foot angle

```text
Knee -> Ankle -> Toe
```

Ankle is the vertex. Verify the actual Sports2D `Body_with_feet` external toe field before mapping it.

### 2D projected trunk inclination

```text
Hip -> Shoulder
Hip -> image vertical
```

Both vectors originate at **Hip**. The vertical reference originates at Hip. This is not a spine angle.

Initial semantic landmarks:

```text
Shoulder
Hip
Knee
Ankle
Toe
```

## I3: Local API

Introduce an application/service boundary between the UI and Python measurement/storage logic.

Initial preferred framework: FastAPI running locally.

The UI must not directly manipulate TRC/CSV files as its main workflow.

## I4: NPL workspace UI

Create the local interactive shell using React + TypeScript.

Primary areas:

- session navigation/import;
- video workspace;
- current-frame measurement inspector;
- analysis/progress state;
- results area;
- provenance/export access.

The design should be engineering-first, precise, compact, high-information-density and restrained. Do not invent authoritative NPL colors/fonts until verified brand assets are available. Use design tokens so real NPL identity can be introduced cleanly.

## I5: Interactive landmark review

Automatic landmarks remain immutable evidence.

Physical markers are visual references for the operator, not machine-detected targets.

When a point is manually corrected:

```text
effective position = active manual correction if present, else automatic position
```

Correction history must support audit, undo and reset-to-automatic.

Dependency-aware recalculation should initially follow:

```text
shoulder -> trunk
hip      -> knee, trunk
knee     -> knee, shank-foot
ankle    -> knee, shank-foot
toe      -> shank-foot
```

## I6: Results workspace

Provide synchronized:

- frame measurements;
- angle curves;
- current-frame cursor;
- frame table;
- validity state;
- manual-correction state;
- bounded session summaries.

Selecting a graph point or table row should navigate the video to that frame.

## I7: Render / export

Exports remain derived artifacts of a session, not the internal database of record.

Target exports:

- measurements CSV;
- landmarks CSV;
- provenance/session JSON;
- figures;
- overlay MP4.

Existing `video_overlay.py` remains a post-Core visualization baseline and may later be adapted behind the session/export service without changing measurement truth.

## I8: Verification

Verification should include:

- synthetic session/database tests;
- synthetic measurement cases;
- manual-correction/effective-landmark tests;
- preview-to-original coordinate mapping tests;
- API contract tests;
- UI interaction tests where practical;
- one private real end-to-end session reviewed locally.

Private human media and reviewed results remain untracked.

## I9: v0.2 release

Release only after the interactive workflow is coherent, tested and documented.

The release should distinguish clearly between:

- what Core v0.1.0 established;
- what Interactive v0.2 adds;
- what remains unvalidated or outside scope.

Do not describe manual correction or additional angles as clinical validation.

## Git workflow

Keep the same disciplined development pattern used for the Core:

```text
main
  -> focused feature branch
  -> tests/review
  -> pull request
  -> explicit merge approval
  -> next milestone branch
```

Do not combine I0-I9 into one long-lived feature branch.
