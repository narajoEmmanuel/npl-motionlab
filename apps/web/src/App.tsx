import { ChangeEvent, FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { motionlabApi } from "./api";
import ExportPanel from "./ExportPanel";
import { ReviewOverlay } from "./ReviewOverlay";
import ResultsWorkspace from "./ResultsWorkspace";
import type {
  FrameSnapshot,
  LandmarkRole,
  SessionSnapshot,
  Side,
} from "./types";

const LANDMARK_ORDER: LandmarkRole[] = ["shoulder", "hip", "knee", "ankle", "toe"];

function formatAngle(value: number | null, valid: boolean) {
  if (!valid || value === null) return "—";
  return `${value.toFixed(1)}°`;
}

function App() {
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");
  const [sourcePath, setSourcePath] = useState("");
  const [label, setLabel] = useState("");
  const [side, setSide] = useState<Side>("right");
  const [session, setSession] = useState<SessionSnapshot | null>(null);
  const [trcPath, setTrcPath] = useState("");
  const [provenancePath, setProvenancePath] = useState("");
  const [frameIndex, setFrameIndex] = useState(0);
  const [frame, setFrame] = useState<FrameSnapshot | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [reviewBusy, setReviewBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    motionlabApi.health().then(
      () => setApiStatus("online"),
      () => setApiStatus("offline"),
    );
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  useEffect(() => {
    const fps = session?.video?.fps;
    if (!videoRef.current || !fps || !Number.isFinite(fps)) return;
    const nominalTime = frameIndex / fps;
    if (Math.abs(videoRef.current.currentTime - nominalTime) > 0.03) {
      videoRef.current.currentTime = nominalTime;
    }
  }, [frameIndex, session]);

  const maxFrame = Math.max(0, (session?.video?.frame_count ?? 1) - 1);
  const analysisReady = Boolean(session && trcPath && provenancePath);

  const correctedCount = useMemo(() => {
    if (!frame) return 0;
    return LANDMARK_ORDER.filter(
      (role) => frame.landmarks[role]?.source_state === "manual_corrected",
    ).length;
  }, [frame]);

  async function createSession(event: FormEvent) {
    event.preventDefault();
    if (!sourcePath.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const created = await motionlabApi.createSession({
        source_path: sourcePath.trim(),
        selected_side: side,
        label: label.trim() || undefined,
      });
      setSession(created);
      setFrame(null);
      setFrameIndex(0);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create session");
    } finally {
      setBusy(false);
    }
  }

  async function importAnalysis() {
    if (!session || !analysisReady) return;
    setBusy(true);
    setError(null);
    try {
      await motionlabApi.importAnalysis(session.id, {
        trc_path: trcPath.trim(),
        engine_provenance_path: provenancePath.trim(),
      });
      const refreshed = await motionlabApi.getSession(session.id);
      setSession(refreshed);
      await loadFrame(0, refreshed);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to import analysis");
    } finally {
      setBusy(false);
    }
  }

  async function loadFrame(next: number, explicitSession = session) {
    if (!explicitSession) return;
    const bounded = Math.min(Math.max(0, next), Math.max(0, explicitSession.counts.frames - 1));
    setError(null);
    try {
      const snapshot = await motionlabApi.getFrame(explicitSession.id, bounded);
      setFrameIndex(bounded);
      setFrame(snapshot);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load frame");
    }
  }

  async function correctLandmark(role: LandmarkRole, xPx: number, yPx: number) {
    if (!session || !frame) return;
    setReviewBusy(true);
    setError(null);
    try {
      const reviewed = await motionlabApi.correctLandmark(
        session.id,
        frame.frame_index,
        role,
        { x_px: xPx, y_px: yPx, note: "interactive drag review" },
      );
      setFrame(reviewed);
      const refreshed = await motionlabApi.getSession(session.id);
      setSession(refreshed);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : `Unable to correct ${role}`);
      throw reason;
    } finally {
      setReviewBusy(false);
    }
  }

  async function resetLandmark(role: LandmarkRole) {
    if (!session || !frame) return;
    setReviewBusy(true);
    setError(null);
    try {
      const reviewed = await motionlabApi.resetLandmark(session.id, frame.frame_index, role);
      setFrame(reviewed);
      const refreshed = await motionlabApi.getSession(session.id);
      setSession(refreshed);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : `Unable to reset ${role}`);
    } finally {
      setReviewBusy(false);
    }
  }

  async function undoLandmark(role: LandmarkRole) {
    if (!session || !frame) return;
    setReviewBusy(true);
    setError(null);
    try {
      const reviewed = await motionlabApi.undoLandmark(session.id, frame.frame_index, role);
      setFrame(reviewed);
      setSession(await motionlabApi.getSession(session.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : `Unable to undo ${role}`);
    } finally {
      setReviewBusy(false);
    }
  }

  function attachPreview(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(file));
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-mark" aria-hidden="true">ML</div>
          <div>
            <strong>NPL MotionLab</strong>
            <span>Interactive measurement workspace</span>
          </div>
        </div>
        <div className="topbar-actions">
          <span className={`status-pill status-${apiStatus}`}>
            <span className="status-dot" />
            API {apiStatus}
          </span>
          <span className="phase-pill">Interactive v0.2 · completion</span>
        </div>
      </header>

      <main className="workspace-grid">
        <aside className="left-rail panel">
          <div className="panel-heading">
            <span className="eyebrow">Session</span>
            <h1>Measurement setup</h1>
          </div>

          <form className="stack" onSubmit={createSession}>
            <label>
              <span>Source video path</span>
              <input
                value={sourcePath}
                onChange={(event) => setSourcePath(event.target.value)}
                placeholder="C:\data\trial_01.mp4"
                spellCheck={false}
              />
            </label>
            <label>
              <span>Session label</span>
              <input value={label} onChange={(event) => setLabel(event.target.value)} placeholder="Trial 01" />
            </label>
            <div className="segmented" role="group" aria-label="Analysis side">
              {(["right", "left"] as Side[]).map((value) => (
                <button
                  key={value}
                  type="button"
                  className={side === value ? "active" : ""}
                  onClick={() => setSide(value)}
                >
                  {value}
                </button>
              ))}
            </div>
            <button className="primary-button" disabled={busy || apiStatus !== "online"}>
              Create session
            </button>
          </form>

          <div className="divider" />

          <div className="stack compact">
            <div className="section-row">
              <div>
                <span className="eyebrow">Analysis input</span>
                <h2>Sports2D boundary</h2>
              </div>
              <span className="mini-badge">Pinned</span>
            </div>
            <label>
              <span>Pixel TRC path</span>
              <input value={trcPath} onChange={(event) => setTrcPath(event.target.value)} placeholder="…_px_person00.trc" spellCheck={false} />
            </label>
            <label>
              <span>Provenance JSON path</span>
              <input value={provenancePath} onChange={(event) => setProvenancePath(event.target.value)} placeholder="motionlab_sports2d_provenance.json" spellCheck={false} />
            </label>
            <button className="secondary-button" disabled={!analysisReady || busy} onClick={importAnalysis}>
              Import verified analysis
            </button>
          </div>

          {session && (
            <div className="session-card">
              <div className="session-card-title">
                <span>{session.label || "Untitled session"}</span>
                <span className="mini-badge">{session.status}</span>
              </div>
              <dl>
                <div><dt>Side</dt><dd>{session.selected_side}</dd></div>
                <div><dt>Frames</dt><dd>{session.counts.frames}</dd></div>
                <div><dt>Auto points</dt><dd>{session.counts.automatic_landmarks}</dd></div>
                <div><dt>Corrections</dt><dd>{session.counts.active_manual_corrections}</dd></div>
              </dl>
              <code>{session.id}</code>
            </div>
          )}
        </aside>

        <section className="center-stage">
          <div className="viewer panel">
            <div className="viewer-toolbar">
              <div>
                <span className="eyebrow">Source view</span>
                <h2>{session?.video?.source_filename ?? "No active video"}</h2>
              </div>
              <label className="file-button">
                Attach local preview
                <input type="file" aria-label="Attach local preview" accept="video/*" onChange={attachPreview} />
              </label>
            </div>

            <div className="video-canvas">
              {previewUrl ? (
                <div className="video-layer">
                  <video ref={videoRef} src={previewUrl} controls preload="metadata" />
                  {session?.video && frame && (
                    <ReviewOverlay
                      frame={frame}
                      video={session.video}
                      disabled={reviewBusy}
                      onCommit={correctLandmark}
                    />
                  )}
                </div>
              ) : (
                <div className="empty-viewer">
                  <div className="crosshair" aria-hidden="true" />
                  <strong>Attach the same local source video for preview</strong>
                  <p>The backend keeps the authoritative source path and hash. The browser preview remains local and is not uploaded.</p>
                </div>
              )}
            </div>

            <div className="timeline-strip">
              <button onClick={() => loadFrame(frameIndex - 1)} disabled={!session || frameIndex <= 0 || reviewBusy}>←</button>
              <input
                aria-label="Frame"
                type="range"
                min="0"
                max={maxFrame}
                value={Math.min(frameIndex, maxFrame)}
                disabled={!session || reviewBusy}
                onChange={(event) => loadFrame(Number(event.target.value))}
              />
              <button onClick={() => loadFrame(frameIndex + 1)} disabled={!session || frameIndex >= maxFrame || reviewBusy}>→</button>
              <div className="frame-readout">
                <span>Frame <strong>{frameIndex}</strong> / {maxFrame}</span>
                <span>{frame ? `${frame.time_s.toFixed(3)} s` : "—"}</span>
              </div>
            </div>
            <p className="viewer-note">Drag a visible landmark to review that frame. Release saves the correction; Esc cancels the active drag. Preview seeking still uses nominal FPS and is not an exact-VFR timing claim.</p>
          </div>

          {error && <div className="error-banner" role="alert">{error}</div>}

          <div className="lower-grid">
            <div className="panel compact-panel">
              <div className="section-row">
                <div><span className="eyebrow">Frame evidence</span><h2>Landmarks</h2></div>
                <span className="mini-badge">{correctedCount} corrected</span>
              </div>
              <div className="landmark-table landmark-review-table" role="table" aria-label="Current frame landmarks">
                <div className="table-row table-head" role="row"><span>Role</span><span>X px</span><span>Y px</span><span>State</span><span>Review</span></div>
                {LANDMARK_ORDER.map((role) => {
                  const point = frame?.landmarks[role];
                  return (
                    <div className="table-row" role="row" key={role}>
                      <strong>{role}</strong>
                      <span>{point ? point.x_px.toFixed(1) : "—"}</span>
                      <span>{point ? point.y_px.toFixed(1) : "—"}</span>
                      <span className={`source-state source-${point?.source_state ?? "missing"}`}>
                        {point?.source_state === "manual_corrected" ? "Corrected" : point ? "Automatic" : "Missing"}
                      </span>
                      <span className="review-actions">
                        <button
                          type="button"
                          className="table-action"
                          aria-label={`Reset ${role} to automatic`}
                          disabled={!point || point.source_state !== "manual_corrected" || reviewBusy}
                          onClick={() => resetLandmark(role)}
                        >
                          Reset
                        </button>
                        <button type="button" className="table-action"
                          aria-label={`Undo ${role} correction`}
                          disabled={!point || point.source_state !== "manual_corrected" || reviewBusy}
                          onClick={() => undoLandmark(role)}>
                          Undo
                        </button>
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="panel compact-panel">
              <ResultsWorkspace
                session={session}
                currentFrame={frameIndex}
                onSelectFrame={(index) => void loadFrame(index)}
              />
            </div>
          </div>
        </section>

        <aside className="right-rail panel">
          <div className="panel-heading">
            <span className="eyebrow">Current frame</span>
            <h1>Measurements</h1>
          </div>

          <div className="measurement-stack">
            {[
              "projected_knee_flexion",
              "projected_shank_foot_angle",
              "projected_trunk_inclination",
            ].map((key) => {
              const measurement = frame?.measurements[key];
              return (
                <article className="measurement-card" key={key}>
                  <div className="measurement-label">
                    <span>{measurement?.display_name ?? key.replaceAll("_", " ")}</span>
                    <span className={`source-state source-${measurement?.source_state ?? "missing"}`}>
                      {measurement?.source_state === "manual_corrected" ? "Reviewed" : measurement ? "Auto" : "—"}
                    </span>
                  </div>
                  <strong>{measurement ? formatAngle(measurement.value_deg, measurement.valid) : "—"}</strong>
                  <small>
                    {measurement?.valid
                      ? `Definition v${measurement.definition_version}`
                      : measurement?.invalid_reason ?? "No frame result loaded"}
                  </small>
                </article>
              );
            })}
          </div>

          <div className="divider" />

          <div className="integrity-block">
            <span className="eyebrow">Interpretation boundary</span>
            <ul>
              <li>Knee: projected flexion convention</li>
              <li>Shank-foot: geometric image-plane angle</li>
              <li>Trunk: inclination vs image vertical</li>
            </ul>
            <p>Manual review corrects visible landmark placement; it does not by itself establish clinical accuracy.</p>
          </div>

          <div className="integrity-block">
            <span className="eyebrow">Review state</span>
            <div className="legend-row"><span className="legend-dot auto" />Automatic landmark</div>
            <div className="legend-row"><span className="legend-dot corrected" />Manual correction active</div>
            <div className="legend-row"><span className="legend-dot invalid" />Missing / invalid</div>
          </div>

          <div className="divider" />
          <ExportPanel session={session} />
        </aside>
      </main>
    </div>
  );
}

export default App;
