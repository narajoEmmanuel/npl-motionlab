# I4 — NPL MotionLab Interactive Workspace UI

## Scope

I4 introduces the first browser-based local workspace for MotionLab Interactive.
It sits on top of the I3 loopback API and does not change Core v0.1.0 measurement
logic, I1 session persistence, or I2 measurement definitions.

The UI is implemented in:

```text
apps/web/
```

with React + TypeScript + Vite.

## Runtime model

Run the Python API on loopback:

```powershell
python -m uvicorn motionlab.api.server:app --host 127.0.0.1 --port 8000
```

Run the web workspace separately:

```powershell
cd apps/web
npm install
npm run dev
```

Vite binds to `127.0.0.1:5173` and proxies `/api` to the local MotionLab API.
No cloud backend, remote database or paid service is required.

## Workspace layout

The initial engineering workspace has three primary columns:

```text
Session / analysis setup | Video review workspace | Measurement inspector
```

The center column is intentionally dominant because source imagery and geometry
are the primary inspection surface.

The current I4 shell contains:

- source-path session creation;
- side selection;
- pinned Sports2D TRC/provenance import controls;
- local-only browser preview attachment;
- semantic landmark overlay;
- frame navigation;
- current-frame landmark evidence table;
- current-frame knee, shank-foot and trunk measurements;
- explicit automatic/corrected/missing state presentation;
- a reserved results area for I6 synchronized curves and table navigation.

## Local video preview boundary

The backend session keeps the authoritative source path, source hash and decoded
metadata. I4 does not add a public file-upload service.

Because a browser cannot safely obtain an arbitrary full local filesystem path
from an HTML file input, the UI uses two distinct actions:

1. the source path is supplied to the local backend when the session is created;
2. the user may attach the same local video to the browser as a temporary preview
   using `URL.createObjectURL`.

The preview file is not uploaded or persisted by the web UI.

This preserves the local-first privacy boundary but means I4 does not yet prove
that the browser-selected preview bytes are identical to the backend source.
A later media/application milestone may replace this with a verified local media
endpoint or desktop wrapper.

## Frame timing limitation

When the current frame changes, I4 seeks the browser preview using:

```text
nominal time = frame_index / nominal_fps
```

This is only a display convenience. It is not an exact variable-frame-rate timing
claim and is labeled accordingly in the UI.

Exact decoded-frame synchronization remains a later verification/media concern.

## Overlay coordinate contract

The overlay uses the session's original decoded pixel dimensions as its SVG
viewBox. Landmark coordinates remain original-image pixel coordinates.

The browser may scale the source image for display, while SVG viewBox scaling
keeps point locations in the same original coordinate domain.

I4 overlays points and segments for inspection only. Drag editing is intentionally
reserved for I5.

## Measurement presentation

The inspector displays the three I2 definitions:

- 2D projected knee flexion;
- 2D projected shank-foot angle;
- 2D projected trunk inclination.

Validity and source state are explicit. The UI does not invent a value for an
invalid measurement.

The wording deliberately preserves interpretation boundaries:

- shank-foot angle is not labeled clinical dorsiflexion;
- trunk inclination is not labeled a spine angle;
- no measurement is presented as a diagnosis.

## Design direction

The UI follows the I0 engineering-first NPL direction:

- video/geometry first;
- compact information hierarchy;
- restrained visual decoration;
- explicit provenance and validity states;
- high information density without generic KPI-dashboard styling;
- keyboard/focus-friendly native controls;
- state is communicated with both text and color.

`apps/web/src/styles/tokens.css` defines provisional design tokens so an
authoritative NPL visual identity can be inserted later without restructuring the
workspace.

The current colors and typography are **not claimed as official NPL brand values**.
No formal NPL visual token set is currently stored in the repository.

## I4 boundaries

Implemented in I4:

- React/TypeScript local workspace shell;
- Vite loopback proxy;
- API connectivity/status;
- session setup and verified-analysis import controls;
- local browser preview;
- read-only landmark overlay;
- frame stepping/slider;
- measurement inspector;
- tokenized engineering-oriented styling.

Not implemented in I4:

- drag correction;
- undo/reset interaction in the UI;
- persisted reviewed-result recalculation;
- exact VFR frame synchronization;
- automatic Sports2D process execution/progress;
- synchronized measurement curves;
- full frame-results table;
- export workflows;
- clinical interpretation.

Those remain I5+ work.

## Verification target

Before I4 is merged:

- `npm install` completes without paid/external service configuration;
- `npm run typecheck` passes;
- `npm run build` passes;
- the Python full test suite remains green;
- the local API and Vite dev server run only on loopback;
- a synthetic/local session can be created through the UI;
- a verified synthetic analysis can be imported;
- current-frame landmarks and all three measurements render;
- private human media/workspace files remain untracked.

For the final v0.2 workflow, this composed server includes the established I3
API plus bulk results and export routes. See [local run guide](v0.2_local_run.md).
