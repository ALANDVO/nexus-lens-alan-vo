/** Typed HTTP client matching backend routes at /api/v1.

All calls return the parsed JSON body or throw an ApiError with a redacted
detail string from the server.
*/

import type {
  Analysis,
  AnalysisSummary,
  ListParams,
  PaginatedPlugins,
  Plugin,
  PluginCreate,
} from "./types";

const API_BASE = "/api/v1";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init.headers },
    ...init,
  });

  const body = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const detail = typeof body.detail === "string"
      ? body.detail
      : "Request failed";
    throw new ApiError(detail, resp.status);
  }
  return body as T;
}

function buildQuery(params: ListParams): string {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") usp.append(k, String(v));
  }
  const q = usp.toString();
  return q ? `?${q}` : "";
}

export const api = {
  // --- Plugins ---
  listPlugins(params?: ListParams): Promise<PaginatedPlugins> {
    const q = params ? buildQuery(params) : "";
    return request<PaginatedPlugins>(`/plugins${q}`);
  },

  getPlugin(id: number): Promise<Plugin> {
    return request<Plugin>(`/plugins/${id}`);
  },

  createPlugin(data: PluginCreate): Promise<Plugin> {
    return request<Plugin>("/plugins", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  updatePlugin(id: number, data: Partial<PluginCreate>): Promise<Plugin> {
    return request<Plugin>(`/plugins/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  deletePlugin(id: number): Promise<void> {
    return request<void>(`/plugins/${id}`, { method: "DELETE" });
  },

  // --- Analyses ---
  runAnalysis(pluginId: number): Promise<Analysis> {
    return request<Analysis>(`/plugins/${pluginId}/analyze`, {
      method: "POST",
    });
  },

  getAnalysis(analysisId: number): Promise<Analysis> {
    return request<Analysis>(`/plugins/analyses/${analysisId}`);
  },

  listAnalyses(pluginId: number): Promise<AnalysisSummary[]> {
    return request<AnalysisSummary[]>(`/plugins/${pluginId}/analyses`);
  },

  // --- Health ---
  health(): Promise<{ status: string; time: string }> {
    return request<{ status: string; time: string }>("/health");
  },
};