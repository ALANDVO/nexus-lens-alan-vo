import { useState } from "react";
import type { PluginCreate, PluginType } from "../api/types";

interface Props {
  onSubmit: (data: PluginCreate) => Promise<void> | void;
  loading?: boolean;
}

function buildManifest(
  name: string,
  description: string,
  source: string,
  pluginType: PluginType,
): Record<string, unknown> {
  const base = {
    name,
    description,
    source,
    plugin_type: pluginType,
  };
  if (pluginType === "lsp") {
    return {
      ...base,
      config: {
        lspServers: {},
        lspConfig: { plugin: { pluginId: name } },
      },
    };
  }
  return { ...base, config: {} };
}

export default function PluginForm({ onSubmit, loading }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [source, setSource] = useState("");
  const [pluginType, setPluginType] = useState<PluginType>("lsp");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const manifest = buildManifest(name, description, source, pluginType);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!name.trim()) newErrors.name = "Name is required";
    if (!description.trim()) newErrors.description = "Description is required";
    if (!source.trim()) newErrors.source = "Source is required";
    else if (!/^[A-Za-z0-9.-]{1,39}\/[A-Za-z0-9._-]{1,100}$/.test(source)) {
      newErrors.source = "Use owner/repo format (e.g. anthropics/claude-plugins-official)";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ name, description, source, plugin_type: pluginType, manifest });
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="form-row">
        <div className="form-group">
          <label>Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. typescript-lsp"
          />
          {errors.name && <div className="form-error">{errors.name}</div>}
        </div>
        <div className="form-group">
          <label>Type</label>
          <select value={pluginType} onChange={(e) => setPluginType(e.target.value as PluginType)}>
            <option value="lsp">LSP</option>
            <option value="mcp">MCP</option>
            <option value="hook">Hook</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label>Description</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="What does this plugin do?"
          rows={3}
        />
        {errors.description && <div className="form-error">{errors.description}</div>}
      </div>

      <div className="form-group">
        <label>Source (GitHub owner/repo)</label>
        <input
          type="text"
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="owner/repo"
        />
        {errors.source && <div className="form-error">{errors.source}</div>}
      </div>

      <div className="form-group">
        <label>Manifest preview (JSON)</label>
        <pre
          style={{
            background: "var(--surface-2)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)",
            padding: "12px",
            fontFamily: "monospace",
            fontSize: "0.8rem",
            color: "var(--text-dim)",
            maxHeight: "200px",
            overflow: "auto",
          }}
        >
          {JSON.stringify(manifest, null, 2)}
        </pre>
      </div>

      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Saving…" : "Register Plugin"}
        </button>
        {errors.submit && <div className="form-error">{errors.submit}</div>}
      </div>
    </form>
  );
}