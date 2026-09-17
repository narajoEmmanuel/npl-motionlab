import type {
  FrameSnapshot,
  LandmarkRole,
  MeasurementDefinition,
  SessionSnapshot,
  Side,
} from "./types";

const API_ROOT = "/api/v1";

interface AnalysisImportResponse {
  session_id: string;
  status: string;
  imported: {
    frames: number;
    automatic_landmarks: number;
    measurement_results: number;
  };
}

export interface ExportResponse {
  session_id: string;
  export_dir: string;
  artifacts: Record<string, string>;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_ROOT}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) detail = payload.detail;
    } catch {
      // Keep the HTTP fallback when the body is not JSON.
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export const motionlabApi = {
  health: () => request<{ status: string; api_version: string }>("/health"),

  measurementDefinitions: () =>
    request<MeasurementDefinition[]>("/measurements"),

  createSession: (payload: {
    source_path: string;
    selected_side: Side;
    label?: string;
  }) =>
    request<SessionSnapshot>("/sessions", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getSession: (sessionId: string) =>
    request<SessionSnapshot>(`/sessions/${sessionId}`),

  importAnalysis: (
    sessionId: string,
    payload: { trc_path: string; engine_provenance_path: string },
  ) =>
    request<AnalysisImportResponse>(`/sessions/${sessionId}/analysis/import`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getFrame: (sessionId: string, frameIndex: number) =>
    request<FrameSnapshot>(`/sessions/${sessionId}/frames/${frameIndex}`),

  getFrames: (sessionId: string) =>
    request<FrameSnapshot[]>(`/sessions/${sessionId}/frames`),

  correctLandmark: (
    sessionId: string,
    frameIndex: number,
    role: LandmarkRole,
    payload: { x_px: number; y_px: number; note?: string },
  ) =>
    request<FrameSnapshot>(
      `/sessions/${sessionId}/frames/${frameIndex}/landmarks/${role}/corrections`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    ),

  resetLandmark: (sessionId: string, frameIndex: number, role: LandmarkRole) =>
    request<FrameSnapshot>(
      `/sessions/${sessionId}/frames/${frameIndex}/landmarks/${role}/correction`,
      { method: "DELETE" },
    ),

  undoLandmark: (sessionId: string, frameIndex: number, role: LandmarkRole) =>
    request<FrameSnapshot>(
      `/sessions/${sessionId}/frames/${frameIndex}/landmarks/${role}/undo`,
      { method: "POST" },
    ),

  exportSession: (sessionId: string, includeOverlayMp4 = true) =>
    request<ExportResponse>(`/sessions/${sessionId}/exports`, {
      method: "POST",
      body: JSON.stringify({ include_overlay_mp4: includeOverlayMp4 }),
    }),
};
