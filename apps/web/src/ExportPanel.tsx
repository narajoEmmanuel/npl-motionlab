import { useState } from "react";

import { motionlabApi } from "./api";
import type { SessionSnapshot } from "./types";

interface Props {
  session: SessionSnapshot | null;
}

export default function ExportPanel({ session }: Props) {
  const [includeOverlay, setIncludeOverlay] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [artifacts, setArtifacts] = useState<Record<string, string> | null>(null);

  async function runExport() {
    if (!session) return;
    setBusy(true);
    setError(null);
    setArtifacts(null);
    try {
      const response = await motionlabApi.exportSession(session.id, includeOverlay);
      setArtifacts(response.artifacts);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Export failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="export-panel" aria-label="Session export">
      <div>
        <span className="eyebrow">Local artifacts</span>
        <h2>Export session</h2>
      </div>
      <label className="export-option">
        <input
          type="checkbox"
          checked={includeOverlay}
          onChange={(event) => setIncludeOverlay(event.target.checked)}
          disabled={!session || busy}
        />
        Include reviewed overlay MP4
      </label>
      <button
        type="button"
        className="secondary-button"
        onClick={runExport}
        disabled={!session || session.status !== "analyzed" || busy}
      >
        {busy ? "Exporting…" : "Create local export"}
      </button>
      <p className="viewer-note">Exports are derived local artifacts; they do not replace session or automatic evidence.</p>
      {error && <div className="error-banner" role="alert">{error}</div>}
      {artifacts && (
        <div className="export-artifacts">
          {Object.entries(artifacts).map(([name, path]) => (
            <div key={name}><strong>{name}</strong><code>{path}</code></div>
          ))}
        </div>
      )}
    </section>
  );
}
