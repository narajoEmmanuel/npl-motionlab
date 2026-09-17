import type {
  FrameSnapshot,
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
};
