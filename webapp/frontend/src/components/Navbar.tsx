import {
  Globe,
  HelpCircle,
  ScrollText,
  Search,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useStore } from "../store";

export function Navbar() {
  const currentPage = useStore((s) => s.currentPage);
  const systemStatus = useStore((s) => s.systemStatus);
  const setLoggerOpen = useStore((s) => s.setLoggerOpen);
  const setHelpOpen = useStore((s) => s.setHelpOpen);

  const getTitle = () => {
    const titles: Record<string, string> = {
      dashboard: "Dashboard",
      "apps-hub": "Apps Hub",
      chat: "LLM Chat",
      "image-editor": "Image Editor",
      "batch-processor": "Batch Processor",
      "layer-manager": "Layer Manager",
      "tools-explorer": "Tools Explorer",
      skills: "Skills",
      "api-docs": "API Docs",
      "system-status": "System Status",
      "script-fu-console": "Script-Fu Console",
      "fastmcp-sota": "FastMCP 3.2 SOTA",
    };
    return titles[currentPage] || "GIMP MCP";
  };

  const getModeInfo = () => {
    const mode = systemStatus?.live_mode?.mode;
    if (mode === "live")
      return {
        label: "Live Bridge",
        color: "bg-green-500",
        text: "text-green-400",
      };
    if (mode === "headless")
      return {
        label: "Headless CLI",
        color: "bg-blue-500",
        text: "text-blue-400",
      };
    return { label: "Offline", color: "bg-red-500", text: "text-red-400" };
  };

  const mode = getModeInfo();
  const healthy = systemStatus?.status === "healthy";

  return (
    <nav className="h-12 border-b bg-card/80 backdrop-blur-sm flex items-center justify-between px-5 shrink-0 z-40">
      <div className="flex items-center gap-4">
        <h1 className="text-sm font-semibold">{getTitle()}</h1>
        <div className="flex items-center gap-2 text-[11px]">
          <span
            className={`w-1.5 h-1.5 rounded-full ${healthy ? "bg-green-500" : "bg-red-500"}`}
          />
          <span
            className={`font-mono ${healthy ? "text-green-400" : "text-red-400"}`}
          >
            {healthy ? "healthy" : "degraded"}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-1">
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-secondary rounded-full text-[11px] mr-2">
          <span className={`w-1.5 h-1.5 rounded-full ${mode.color}`} />
          <span className="text-muted-foreground font-medium">
            {mode.label}
          </span>
        </div>

        <button
          type="button"
          onClick={() => setLoggerOpen(true)}
          className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
          title="Global Logger"
        >
          <ScrollText className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={() => setHelpOpen(true)}
          className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
          title="Help"
        >
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>
    </nav>
  );
}
