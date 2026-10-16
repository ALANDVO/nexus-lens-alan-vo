/**
 * Nexus Lens — main application shell.
 *
 * Simple state-based routing (no router dependency needed for the v1 surface):
 *   dashboard → new plugin → detail
 *   dashboard → detail
 *   detail → dashboard
 */

import { useState } from "react";
import DashboardPage from "./pages/DashboardPage";
import NewPluginPage from "./pages/NewPluginPage";
import PluginDetailPage from "./pages/PluginDetailPage";

export type View = "dashboard" | "new" | "detail";

export default function App() {
  const [view, setView] = useState<View>("dashboard");
  const [pluginId, setPluginId] = useState<number | null>(null);

  const openDetail = (id: number) => {
    setPluginId(id);
    setView("detail");
  };
  const backToDashboard = () => {
    setPluginId(null);
    setView("dashboard");
  };

  switch (view) {
    case "new":
      return <NewPluginPage onSuccess={openDetail} onCancel={backToDashboard} />;
    case "detail":
      if (pluginId !== null) {
        return <PluginDetailPage id={pluginId} onBack={backToDashboard} />;
      }
      // fall through
    default:
      return (
        <DashboardPage onViewPlugin={openDetail} onNewPlugin={() => setView("new")} />
      );
  }
}