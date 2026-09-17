# I3 — MotionLab Interactive Local API

## Scope

I3 introduces the local application/service boundary between the future UI and
MotionLab's Python session, adapter and measurement layers.

The service is intentionally local-first. It is not a cloud API and does not
introduce accounts, remote storage or paid services.

The initial framework is FastAPI, installed through the optional `interactive`
package extra. The frozen Core dependencies remain unchanged.

## Runtime boundary

Run the service on loopback only:

```powershell
python -m uvicorn motionlab.api.app:app --host 127.0.0.1 --port 8000
```

The API should not be exposed to a public network in this milestone.

## API version

The first contract is namespaced under:

```text
/api/v1
```

## Primary resources

### Health

```text
GET /api/v1/health
```

Returns service/API identity for the local UI.

### Measurement definitions

```text
GET /api/v1/measurements
```

Returns the versioned I2 measurement registry, including display names,
dependencies and units.

### Create session

```text
POST /api/v1/sessions
```

Request fields:

```text
source_path
selected_side
label (optional)
```

The backend inspects the source itself, stores SHA-256 and decoded metadata,
creates a private `workspace/sessions/<session_id>/session.db`, and initializes
frame rows using the currently available reported frame-count/nominal-FPS
contract.

The source video is referenced by path; it is not embedded in SQLite or copied
by this endpoint.

### Session snapshot

```text
GET /api/v1/sessions/{session_id}
```

Returns session/video identity plus bounded counts useful for the UI.

### Import verified Sports2D analysis

```text
POST /api/v1/sessions/{session_id}/analysis/import
```

Request fields:

```text
trc_path
engine_provenance_path
```

This endpoint is the first analysis application boundary. It consumes existing
pinned Sports2D output and does not run the pose engine itself.

The importer checks source identity and the pinned engine/model contract before
accepting the pixel TRC. It maps the verified I2 semantic landmarks, skips
non-finite automatic points rather than fabricating replacements, and stores
frame-level automatic measurement results.

The pose-engine execution process remains isolated because the existing Sports2D
runner belongs to its own heavier environment. A later orchestration layer may
invoke that runner and then call the same verified import service.

### Frame review snapshot

```text
GET /api/v1/sessions/{session_id}/frames/{frame_index}
```

Returns effective semantic landmarks and the three current-frame measurements.
Measurements are evaluated from effective landmarks so a manual correction is
visible immediately in the response.

### Manual correction

```text
POST /api/v1/sessions/{session_id}/frames/{frame_index}/landmarks/{role}/corrections
```

The endpoint appends a correction through the I1 audit model. It does not
overwrite automatic coordinates.

### Reset correction

```text
DELETE /api/v1/sessions/{session_id}/frames/{frame_index}/landmarks/{role}/correction
```

Deactivates the active manual correction and returns to the automatic point.

## Measurement persistence boundary

Automatic analysis import writes the initial automatic measurement rows to
SQLite.

Frame review responses evaluate measurements from the current effective
landmarks. During I3, manual corrections do not rewrite the persisted automatic
measurement rows. Dependency-aware reviewed-result persistence is intentionally
left to I5, where correction transactions and recalculation semantics are
implemented together.

This prevents I3 from silently mixing automatic evidence with reviewed results.

## Source timing limitation

I3 currently initializes frame rows using backend-reported frame count and
nominal FPS because that is the metadata contract available from Core
`video_metadata.py`.

This does not claim exact variable-frame-rate timestamps. Exact decoded
frame/timestamp handling remains a media/application concern for later
interactive work and must not be represented as stronger timing evidence than
is available.

## Privacy

Real session databases and all human media remain under the Git-ignored
`workspace/` boundary. API tests use only temporary synthetic sessions and
synthetic TRC content.

No endpoint publishes private files to Git or to a remote service.

## Dependency policy

FastAPI and Uvicorn are optional interactive dependencies rather than new frozen
Core dependencies:

```powershell
python -m pip install -e ".[dev,interactive]"
```

This stack is open-source and local; I3 introduces no paid service requirement.

## I3 non-goals

I3 does not yet implement:

- browser UI components;
- automatic file-picker behavior;
- pose-engine job/progress management;
- video streaming/preview endpoints;
- exact VFR timestamp extraction;
- drag interactions;
- persisted dependency-aware reviewed measurement updates;
- graph/table synchronization;
- exports.

Those are handled in later interactive milestones.
