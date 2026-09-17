import { PointerEvent, useEffect, useMemo, useRef, useState } from "react";

import type { FrameSnapshot, LandmarkRole, VideoRecord } from "./types";

const LANDMARK_ORDER: LandmarkRole[] = ["shoulder", "hip", "knee", "ankle", "toe"];
const SEGMENTS: Array<[LandmarkRole, LandmarkRole]> = [
  ["shoulder", "hip"],
  ["hip", "knee"],
  ["knee", "ankle"],
  ["ankle", "toe"],
];

interface ReviewOverlayProps {
  frame: FrameSnapshot;
  video: VideoRecord;
  disabled?: boolean;
  onCommit: (role: LandmarkRole, xPx: number, yPx: number) => Promise<void>;
}

interface DragState {
  role: LandmarkRole;
  xPx: number;
  yPx: number;
  pointerId: number;
}

function pointerToImage(
  svg: SVGSVGElement,
  video: VideoRecord,
  clientX: number,
  clientY: number,
): { x: number; y: number } | null {
  const rect = svg.getBoundingClientRect();
  const scale = Math.min(
    rect.width / video.decoded_width_px,
    rect.height / video.decoded_height_px,
  );
  if (!Number.isFinite(scale) || scale <= 0) return null;

  const renderedWidth = video.decoded_width_px * scale;
  const renderedHeight = video.decoded_height_px * scale;
  const offsetX = (rect.width - renderedWidth) / 2;
  const offsetY = (rect.height - renderedHeight) / 2;
  const localX = clientX - rect.left - offsetX;
  const localY = clientY - rect.top - offsetY;

  if (localX < 0 || localY < 0 || localX > renderedWidth || localY > renderedHeight) {
    return null;
  }

  return {
    x: Math.min(video.decoded_width_px, Math.max(0, localX / scale)),
    y: Math.min(video.decoded_height_px, Math.max(0, localY / scale)),
  };
}

export function ReviewOverlay({ frame, video, disabled = false, onCommit }: ReviewOverlayProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    function cancel(event: KeyboardEvent) {
      if (event.key === "Escape") setDrag(null);
    }
    window.addEventListener("keydown", cancel);
    return () => window.removeEventListener("keydown", cancel);
  }, []);

  const displayed = useMemo(() => {
    const result = { ...frame.landmarks };
    if (drag) {
      const original = frame.landmarks[drag.role];
      if (original) {
        result[drag.role] = { ...original, x_px: drag.xPx, y_px: drag.yPx };
      }
    }
    return result;
  }, [drag, frame]);

  function beginDrag(event: PointerEvent<SVGCircleElement>, role: LandmarkRole) {
    if (disabled || saving || !svgRef.current) return;
    const point = pointerToImage(svgRef.current, video, event.clientX, event.clientY);
    if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDrag({ role, xPx: point.x, yPx: point.y, pointerId: event.pointerId });
    event.preventDefault();
  }

  function moveDrag(event: PointerEvent<SVGSVGElement>) {
    if (!drag || event.pointerId !== drag.pointerId || !svgRef.current) return;
    const point = pointerToImage(svgRef.current, video, event.clientX, event.clientY);
    if (!point) return;
    setDrag({ ...drag, xPx: point.x, yPx: point.y });
  }

  async function finishDrag(event: PointerEvent<SVGSVGElement>) {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const pending = drag;
    setDrag(null);
    setSaving(true);
    try {
      await onCommit(pending.role, pending.xPx, pending.yPx);
    } finally {
      setSaving(false);
    }
  }

  return (
    <svg
      ref={svgRef}
      className={`landmark-overlay review-overlay${drag ? " is-dragging" : ""}`}
      viewBox={`0 0 ${video.decoded_width_px} ${video.decoded_height_px}`}
      preserveAspectRatio="xMidYMid meet"
      aria-label="Interactive landmark review overlay"
      onPointerMove={moveDrag}
      onPointerUp={finishDrag}
      onPointerCancel={() => setDrag(null)}
    >
      {SEGMENTS.map(([a, b]) => {
        const pa = displayed[a];
        const pb = displayed[b];
        if (!pa || !pb) return null;
        return (
          <line
            key={`${a}-${b}`}
            x1={pa.x_px}
            y1={pa.y_px}
            x2={pb.x_px}
            y2={pb.y_px}
            className="segment-line"
          />
        );
      })}

      {LANDMARK_ORDER.map((role) => {
        const point = displayed[role];
        if (!point) return null;
        const active = drag?.role === role;
        return (
          <g
            key={role}
            className={`landmark landmark-${point.source_state}${active ? " landmark-active" : ""}`}
          >
            <circle
              cx={point.x_px}
              cy={point.y_px}
              r="12"
              className="landmark-handle"
              role="button"
              aria-label={`Move ${role} landmark`}
              tabIndex={0}
              onPointerDown={(event) => beginDrag(event, role)}
            />
            <text
              x={point.x_px + 16}
              y={point.y_px - 16}
              style={{ fontSize: video.decoded_width_px / 64 }}
            >
              {role}
            </text>
          </g>
        );
      })}

      {drag && (
        <text
          className="drag-help"
          x={drag.xPx + 18}
          y={drag.yPx + 34}
          style={{ fontSize: video.decoded_width_px / 80 }}
        >
          release to save · Esc cancels
        </text>
      )}
    </svg>
  );
}
