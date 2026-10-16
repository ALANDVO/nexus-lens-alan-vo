import type { Plugin } from "../api/types";
import ScoreBadge from "./ScoreBadge";

interface Props {
  plugins: Plugin[];
  onView: (id: number) => void;
}

const TYPE_LABELS: Record<string, string> = {
  lsp: "LSP",
  mcp: "MCP",
  hook: "Hook",
  other: "Other",
};

export default function PluginList({ plugins, onView }: Props) {
  if (plugins.length === 0) {
    return (
      <div className="state">
        <div className="icon">📦</div>
        <h3>No plugins registered yet</h3>
        <p>Click “New Plugin” to add your first Claude Code plugin.</p>
      </div>
    );
  }

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Plugin</th>
          <th>Source</th>
          <th>Type</th>
          <th>Quality</th>
          <th>Created</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {plugins.map((p) => (
          <tr key={p.id}>
            <td>
              <strong>{p.name}</strong>
            </td>
            <td style={{ color: "var(--text-dim)", fontSize: "0.85rem" }}>
              {p.source}
            </td>
            <td>{TYPE_LABELS[p.plugin_type] ?? p.plugin_type}</td>
            <td>
              <ScoreBadge score={p.latest_score ?? 0} band={p.latest_band} />
            </td>
            <td style={{ color: "var(--text-dim)", fontSize: "0.85rem" }}>
              {new Date(p.created_at).toLocaleDateString()}
            </td>
            <td>
              <button className="btn" onClick={() => onView(p.id)}>View</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}