import { PointerEvent, useEffect, useMemo, useRef, useState } from "react";

import type { FrameSnapshot, LandmarkRole, VideoRecord } from "./types";
import { pointerToImage } from "./pointerToImage";

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

function pointerFromOverlay(
  svg: SVGSVGElement,
  video: VideoRecord,
  clientX: number,
  clientY: number,
): { x: number; y: number } | null {
  return pointerToImage(svg.getBoundingClientRect(), video, clientX, clientY);
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
    const point = pointerFromOverlay(svgRef.current, video, event.clientX, event.clientY);
    if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDrag({ role, xPx: point.x, yPx: point.y, pointerId: event.pointerId });
    event.preventDefault();
  }

  function moveDrag(event: PointerEvent<SVGSVGElement>) {
    if (!drag || event.pointerId !== drag.pointerId || !svgRef.current) return;
    const point = pointerFromOverlay(svgRef.current, video, event.clientX, event.clientY);
    if (!point) return;
    setDrag({ ...drag, xPx: point.x, yPx: point.y });
  }

  async function finishDrag(event: PointerEvent<SVGSVGElement>) {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const point = svgRef.current && pointerFromOverlay(svgRef.current, video, event.clientX, event.clientY);
    const pending = drag;
    setDrag(null);
    if (!point) return;
    setSaving(true);
    try {
      await onCommit(pending.role, point.x, point.y);
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
              r={video.decoded_width_px / 128}
              className="landmark-handle"
              role="button"
              aria-label={`Move ${role} landmark`}
              tabIndex={0}
              onPointerDown={(event) => beginDrag(event, role)}
            />
            <text
              x={point.x_px + video.decoded_width_px / 128 + 14}
              y={point.y_px - video.decoded_width_px / 128 - 14}
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
