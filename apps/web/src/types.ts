export type Side = "left" | "right";
export type SourceState = "automatic" | "manual_corrected";

export interface VideoRecord {
  source_path: string;
  source_filename: string;
  sha256: string;
  decoded_width_px: number;
  decoded_height_px: number;
  fps: number;
  frame_count: number;
  duration_s: number;
}

export interface SessionCounts {
  frames: number;
  automatic_landmarks: number;
  active_manual_corrections: number;
  measurement_results: number;
}

export interface SessionSnapshot {
  id: string;
  label: string | null;
  selected_side: Side;
  status: string;
  created_at_utc: string;
  video: VideoRecord | null;
  counts: SessionCounts;
}

export interface LandmarkSnapshot {
  x_px: number;
  y_px: number;
  source_state: SourceState;
  automatic_x_px: number;
  automatic_y_px: number;
  correction_id: number | null;
}

export type LandmarkRole = "shoulder" | "hip" | "knee" | "ankle" | "toe";

export interface MeasurementSnapshot {
  display_name: string;
  definition_version: string;
  unit: string;
  value_deg: number | null;
  valid: boolean;
  invalid_reason: string | null;
  source_state: SourceState;
}

export interface FrameSnapshot {
  frame_index: number;
  time_s: number;
  landmarks: Record<LandmarkRole, LandmarkSnapshot | null>;
  measurements: Record<string, MeasurementSnapshot>;
}

export interface MeasurementDefinition {
  name: string;
  display_name: string;
  version: string;
  unit: string;
  dependencies: LandmarkRole[];
}
