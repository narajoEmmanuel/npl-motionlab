# I1 — MotionLab Session Model / SQLite

## Status

Implementation candidate for MotionLab Interactive I1.

I1 introduces the local structured session store described by ADR-0004. It does
not change the released Core v0.1.0 measurement logic, add new angle formulas,
start the API/UI layers, or migrate historical Core artifacts.

## Storage boundary

One future interactive session owns one local SQLite file:

```text
workspace/sessions/<session_id>/session.db
```

The database stores structured state only. Source video, Sports2D files, previews,
renders, exports and logs remain filesystem artifacts referenced by path and
provenance.

No video binary is embedded in SQLite.

## Schema version

The initial schema version is `1` and is recorded in `schema_meta`.

Opening a database with a different schema version fails rather than silently
interpreting incompatible state. Later schema changes should use explicit
migrations instead of modifying old session files in place without versioning.

## Initial tables

I1 creates:

```text
sessions
videos
frames
automatic_landmarks
manual_corrections
measurement_results
events
artifacts
provenance
```

`measurement_results`, `events`, `artifacts` and `provenance` establish storage
boundaries for later milestones. I1 does not yet implement their higher-level
application services.

## Session and video identity

A session has a stable generated identifier and selected side (`left` or
`right`).

The associated video record retains:

- source path/reference;
- source filename;
- SHA-256 identity;
- decoded dimensions;
- nominal FPS;
- frame count;
- duration.

The source media is not copied automatically by I1.

## Frame contract

Frames are stored in zero-based decoded order.

For nominal constant FPS metadata, I1 initializes:

```text
frame_index = 0, 1, 2, ...
time_s      = frame_index / fps
```

This is a session ordering/indexing convention, not a claim that arbitrary
variable-frame-rate source timestamps are reconstructed exactly.

A session's frame rows are initialized once. Silent replacement is rejected.

## Automatic landmark contract

Initial semantic roles are:

```text
shoulder
hip
knee
ankle
toe
```

The role names are MotionLab semantics. Exact external Sports2D column mapping is
an I2 integration task and must be verified against the pinned model output.

Automatic landmark rows are immutable evidence. Only one automatic point may
exist for one `(frame, semantic role)` pair. Attempting to insert a second point
is rejected rather than overwriting the first.

## Manual correction contract

A manual correction can exist only when the corresponding automatic landmark
exists.

Corrections are append-only history. Adding a later correction deactivates the
previous active correction but does not delete it.

At most one correction may be active for one `(frame, role)` pair.

Resetting a correction deactivates the active correction and restores the
automatic point as the effective point. Historical correction rows remain.

The effective-point rule is:

```text
effective position = active manual correction
                     if present
                     otherwise automatic position
```

The returned effective-landmark object exposes both the effective coordinates
and the original automatic coordinates so later application/UI layers do not
lose provenance.

## Transaction and integrity behavior

SQLite foreign keys are enabled for every `SessionDatabase` connection.

Schema creation is idempotent for the supported schema version. Invalid foreign
references and duplicate immutable automatic landmarks fail through database
constraints rather than being silently accepted.

## Privacy

`session.db` belongs under the already ignored `workspace/` boundary for real
human sessions. Public tests use only synthetic temporary databases.

No private session database or human landmark data should be committed.

## I1 non-goals

I1 does not implement:

- Sports2D execution/import orchestration;
- shoulder/toe external mapping;
- knee/ankle/trunk calculation services;
- dependency-aware measurement recalculation;
- FastAPI;
- React/TypeScript UI;
- preview media;
- drag interaction;
- CSV/JSON/MP4 export services;
- historical Core data migration.

These remain I2+ work.

## Verification target

Synthetic tests cover:

- schema creation/versioning;
- idempotent initialization;
- selected-side validation;
- video identity metadata;
- deterministic frame rows;
- immutable automatic landmarks;
- manual override precedence;
- correction-history preservation;
- reset-to-automatic behavior;
- correction-without-auto rejection;
- missing automatic landmark behavior;
- foreign-key enforcement.

The complete repository test suite must pass before I1 is merged.
