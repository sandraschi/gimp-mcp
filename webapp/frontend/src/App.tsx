import { useEffect } from "react";
import { AppLayout } from "./components/AppLayout";
import { Toaster } from "./components/Toaster";
import AgentToolsPage from "./pages/agent-tools";
import ApiDocsPage from "./pages/api-docs";
import AppsHub from "./pages/apps-hub";
import BatchProcessor from "./pages/batch-processor";
import ChatPage from "./pages/chat";
import Dashboard from "./pages/dashboard";
import FastmcpSotaPage from "./pages/fastmcp-sota";
import HelpPage from "./pages/help";
import ImageEditor from "./pages/image-editor";
import LayerManager from "./pages/layer-manager";
import ScriptFuConsole from "./pages/script-fu-console";
import SettingsPage from "./pages/settings";
import SkillsPage from "./pages/skills";
import SystemStatusPage from "./pages/system-status";
import ToolsExplorer from "./pages/ToolsExplorer";
import { useStore } from "./store";

function App() {
  const currentPage = useStore((s) => s.currentPage);
  const setSystemStatus = useStore((s) => s.setSystemStatus);
  const addLog = useStore((s) => s.addLog);
  const addToast = useStore((s) => s.addToast);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch("/api/health");
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data);
          addLog("info", "Health check OK");
        }
      } catch (error) {
        addLog("warn", "Health check failed");
        setSystemStatus((prev) => {
          if (prev) return { ...prev, status: "unreachable" };
          return null;
        });
      }
    };

    fetchStatus();
    addLog("info", "GIMP MCP Webapp started — FastMCP 3.2 SOTA");
    addToast("Webapp ready", "success");

    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case "agent-tools":
        return <AgentToolsPage />;
      case "dashboard":
        return <Dashboard />;
      case "apps-hub":
        return <AppsHub />;
      case "chat":
        return <ChatPage />;
      case "image-editor":
        return <ImageEditor />;
      case "batch-processor":
        return <BatchProcessor />;
      case "layer-manager":
        return <LayerManager />;
      case "tools-explorer":
        return <ToolsExplorer />;
      case "skills":
        return <SkillsPage />;
      case "api-docs":
        return <ApiDocsPage />;
      case "system-status":
        return <SystemStatusPage status={useStore.getState().systemStatus} />;
      case "script-fu-console":
        return <ScriptFuConsole />;
      case "settings":
        return <SettingsPage />;
      case "fastmcp-sota":
        return <FastmcpSotaPage />;
      case "help":
        return <HelpPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <>
      <AppLayout>{renderPage()}</AppLayout>
      <Toaster />
    </>
  );
}

export default App;
