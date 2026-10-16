import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Analysis, AnalysisSummary, Plugin } from "../api/types";
import AnalysisView from "../components/AnalysisView";

interface Props {
  id: number;
  onBack: () => void;
}

export default function PluginDetailPage({ id, onBack }: Props) {
  const [plugin, setPlugin] = useState<Plugin | null>(null);
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getPlugin(id)
      .then((p) => setPlugin(p))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));

    api
      .listAnalyses(id)
      .then((a) => setAnalyses(a))
      .catch(() => setAnalyses([]));
  }, [id]);

  const runAnalysis = async () => {
    setRunning(true);
    setError(null);
    try {
      const result = await api.runAnalysis(id);
      setSelectedAnalysis(result);
      // Prepend to analyses list.
      setAnalyses((prev) => [
        { id: result.id, plugin_id: result.plugin_id, score: result.score,
          band: result.band, checks_run: result.checks_run, created_at: result.created_at },
        ...prev,
      ]);
    } catch (err) {
      if (err instanceof Error) setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  const viewAnalysis = async (analysisId: number) => {
    try {
      const result = await api.getAnalysis(analysisId);
      setSelectedAnalysis(result);
    } catch (err) {
      if (err instanceof Error) setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="state"><p>Loading plugin…</p></div>
      </div>
    );
  }

  if (error && !plugin) {
    return (
      <div className="container">
        <div className="state" style={{ color: "var(--red)" }}>
          <p>Error: {error}</p>
        </div>
      </div>
    );
  }

  if (!plugin) return null;

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1>{plugin.name}</h1>
          <p className="subtitle">{plugin.description}</p>
        </div>
        <button className="btn" onClick={onBack}>← Dashboard</button>
      </div>

      <div className="card">
        <table className="table" style={{ width: "auto" }}>
          <tbody>
            <tr><th>Source</th><td>{plugin.source}</td></tr>
            <tr><th>Type</th><td>{plugin.plugin_type}</td></tr>
            <tr><th>Languages</th><td style={{ color: "var(--text-dim)" }}>
              {plugin.latest_score !== null
                ? `${plugin.latest_score} — ${plugin.latest_band}`
                : "Not analyzed"}
            </td></tr>
          </tbody>
        </table>
      </div>

      <div style={{ marginBottom: "16px" }}>
        <button
          className="btn btn-primary"
          onClick={runAnalysis}
          disabled={running}
        >
          {running ? "Analyzing…" : "Run Conformance Analysis"}
        </button>
      </div>

      {error && <div className="form-error">{error}</div>}

      {selectedAnalysis && <AnalysisView analysis={selectedAnalysis} />}

      {analyses.length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Past Analyses</h3>
          <ul className="findings-list">
            {analyses.map((a) => (
              <li key={a.id} className="finding-item pass">
                <div className="finding-header">
                  <code className="finding-check">Score: {a.score} ({a.band})</code>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-dim)" }}>
                    {new Date(a.created_at).toLocaleString()}
                  </span>
                  <button
                    className="btn"
                    style={{ marginLeft: "auto", fontSize: "0.75rem", padding: "4px 10px" }}
                    onClick={() => viewAnalysis(a.id)}
                  >
                    View
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}