import { useEffect, useMemo, useState } from "react";

import { motionlabApi } from "./api";
import type { FrameSnapshot, SessionSnapshot } from "./types";

const SERIES = [
  ["projected_knee_flexion", "Knee"],
  ["projected_shank_foot_angle", "Shank-foot"],
  ["projected_trunk_inclination", "Trunk"],
] as const;

interface Props {
  session: SessionSnapshot | null;
  currentFrame: number;
  onSelectFrame: (frameIndex: number) => void;
}

function linePoints(rows: FrameSnapshot[], key: string, width: number, height: number) {
  const values = rows
    .map((row) => row.measurements[key])
    .filter((value) => value?.valid && value.value_deg !== null)
    .map((value) => value!.value_deg as number);
  if (!values.length || rows.length < 2) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(1e-9, max - min);
  return rows
    .map((row, index) => {
      const measurement = row.measurements[key];
      if (!measurement?.valid || measurement.value_deg === null) return null;
      const x = (index / Math.max(1, rows.length - 1)) * width;
      const y = height - ((measurement.value_deg - min) / span) * height;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .filter(Boolean)
    .join(" ");
}

export default function ResultsWorkspace({ session, currentFrame, onSelectFrame }: Props) {
  const [rows, setRows] = useState<FrameSnapshot[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!session || session.status !== "analyzed") {
      setRows([]);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    const load = async () => {
      try {
        const next: FrameSnapshot[] = [];
        const batchSize = 24;
        for (let start = 0; start < session.counts.frames; start += batchSize) {
          const indices = Array.from(
            { length: Math.min(batchSize, session.counts.frames - start) },
            (_, offset) => start + offset,
          );
          const batch = await Promise.all(indices.map((index) => motionlabApi.getFrame(session.id, index)));
          next.push(...batch);
          if (cancelled) return;
        }
        if (!cancelled) setRows(next);
      } catch (reason) {
        if (!cancelled) setError(reason instanceof Error ? reason.message : "Unable to load results");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [session?.id, session?.status, session?.counts.frames]);

  const summaries = useMemo(() => {
    return Object.fromEntries(
      SERIES.map(([key]) => {
        const values = rows
          .map((row) => row.measurements[key])
          .filter((measurement) => measurement?.valid && measurement.value_deg !== null)
          .map((measurement) => measurement!.value_deg as number);
        return [
          key,
          values.length
            ? { min: Math.min(...values), max: Math.max(...values), mean: values.reduce((a, b) => a + b, 0) / values.length }
            : null,
        ];
      }),
    );
  }, [rows]);

  const width = 780;
  const height = 180;
  const cursorX = rows.length > 1 ? (currentFrame / (rows.length - 1)) * width : 0;

  return (
    <section className="results-workspace" aria-label="Session results">
      <div className="section-row">
        <div>
          <span className="eyebrow">Results workspace</span>
          <h2>Session curves & frame table</h2>
        </div>
        <span className="mini-badge">{loading ? "Loading" : `${rows.length} frames`}</span>
      </div>

      {error && <div className="error-banner" role="alert">{error}</div>}

      <div className="results-summary-row">
        {SERIES.map(([key, label]) => {
          const summary = summaries[key] as { min: number; max: number; mean: number } | null;
          return (
            <div className="results-summary" key={key}>
              <span>{label}</span>
              <strong>{summary ? `${summary.mean.toFixed(1)}° mean` : "—"}</strong>
              <small>{summary ? `${summary.min.toFixed(1)}–${summary.max.toFixed(1)}°` : "No valid values"}</small>
            </div>
          );
        })}
      </div>

      <div className="chart-stack">
        {SERIES.map(([key, label]) => {
          const points = linePoints(rows, key, width, height);
          return (
            <div className="result-chart" key={key}>
              <div className="chart-title">{label}</div>
              <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${label} angle by frame`}>
                <line x1={cursorX} x2={cursorX} y1="0" y2={height} className="chart-cursor" />
                {points && <polyline points={points} className="chart-line" />}
              </svg>
            </div>
          );
        })}
      </div>

      <div className="results-table-wrap">
        <table className="results-table">
          <thead>
            <tr><th>Frame</th><th>Time s</th><th>Knee °</th><th>Shank-foot °</th><th>Trunk °</th><th>Edited</th></tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const edited = Object.values(row.landmarks).some((point) => point?.source_state === "manual_corrected");
              return (
                <tr
                  key={row.frame_index}
                  className={row.frame_index === currentFrame ? "active" : ""}
                  onClick={() => onSelectFrame(row.frame_index)}
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") onSelectFrame(row.frame_index);
                  }}
                >
                  <td>{row.frame_index}</td>
                  <td>{row.time_s.toFixed(3)}</td>
                  {SERIES.map(([key]) => {
                    const value = row.measurements[key];
                    return <td key={key}>{value?.valid && value.value_deg !== null ? value.value_deg.toFixed(1) : "—"}</td>;
                  })}
                  <td>{edited ? "Yes" : "No"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
