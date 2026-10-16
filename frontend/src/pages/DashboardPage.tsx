import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Plugin } from "../api/types";
import PluginList from "../components/PluginList";

interface Props {
  onViewPlugin: (id: number) => void;
  onNewPlugin: () => void;
}

export default function DashboardPage({ onViewPlugin, onNewPlugin }: Props) {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listPlugins()
      .then((data) => setPlugins(data.items))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="state"><p>Loading plugins…</p></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="state" style={{ color: "var(--red)" }}>
          <p>Error: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <div>
          <h1>Nexus Lens</h1>
          <p className="subtitle">
            Registry + conformance analyzer for Claude Code plugins
          </p>
        </div>
        <button className="btn btn-primary" onClick={onNewPlugin}>
          New Plugin
        </button>
      </div>
      <PluginList plugins={plugins} onView={onViewPlugin} />
    </div>
  );
}