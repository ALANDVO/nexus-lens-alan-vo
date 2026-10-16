/** Typed API contracts, derived from backend Pydantic schemas. */

export type Severity = "pass" | "warn" | "fail";

export type ScoreBand = "excellent" | "good" | "needs_review" | "poor";

export type PluginType = "lsp" | "mcp" | "hook" | "other";

export interface Plugin {
  id: number;
  name: string;
  description: string;
  source: string;
  plugin_type: PluginType;
  manifest: Record<string, unknown>;
  latest_score: number | null;
  latest_band: ScoreBand | null;
  created_at: string;
  updated_at: string;
}

export interface Finding {
  check_id: string;
  severity: Severity;
  message: string;
  evidence: Record<string, unknown>;
}

export interface Analysis {
  id: number;
  plugin_id: number;
  score: number;
  band: ScoreBand;
  checks_run: string[];
  findings: Finding[];
  created_at: string;
}

export interface AnalysisSummary {
  id: number;
  plugin_id: number;
  score: number;
  band: ScoreBand;
  checks_run: string[];
  created_at: string;
}

export interface PaginatedPlugins {
  items: Plugin[];
  total: number;
  page: number;
  per_page: number;
}

export interface PluginCreate {
  name: string;
  description: string;
  source: string;
  plugin_type: PluginType;
  manifest: Record<string, unknown>;
}

export type ListParams = {
  page?: number;
  per_page?: number;
  search?: string;
  type?: string;
  min_score?: number;
  max_score?: number;
};