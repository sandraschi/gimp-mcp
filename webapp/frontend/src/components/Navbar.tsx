import { ChevronDown, ExternalLink, HelpCircle, Maximize2, Menu, Minimize2, Moon, ScrollText, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { useStore } from "../store";

// EXPERIMENTAL light mode (invert hack). Not fleet standard — see index.css.
// Toggling `.dark` off the root flips the invert filter; persisted so the
// choice survives reloads. Delete this + the CSS block to revert.
const THEME_KEY = "gimp-light-mode";

function useExperimentalTheme() {
  const [light, setLight] = useState(() => {
    try {
      return localStorage.getItem(THEME_KEY) === "1";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", !light);
    try {
      localStorage.setItem(THEME_KEY, light ? "1" : "0");
    } catch {
      // ignore storage errors
    }
  }, [light]);

  return { light, toggle: () => setLight((v) => !v) };
}

const pageLabels: Record<string, string> = {
  dashboard: "Dashboard",
  demos: "Demos",
  "apps-hub": "Apps Hub",
  chat: "LLM Chat",
  "image-editor": "Editor",
  "batch-processor": "Batch",
  "layer-manager": "Layers",
  "tools-explorer": "Tools",
  skills: "Skills",
  "api-docs": "API Docs",
  "system-status": "Status",
  "script-fu-console": "Script-Fu",
  "fastmcp-sota": "FastMCP 3.2",
  "agent-tools": "Agent Tools",
  help: "Help",
  settings: "Settings",
};

export function Navbar() {
  const currentPage = useStore((s) => s.currentPage);
  const systemStatus = useStore((s) => s.systemStatus);
  const compactMode = useStore((s) => s.compactMode);
  const setCurrentPage = useStore((s) => s.setCurrentPage);
  const setLoggerOpen = useStore((s) => s.setLoggerOpen);
  const setHelpOpen = useStore((s) => s.setHelpOpen);
  const toggleCompactMode = useStore((s) => s.toggleCompactMode);
  const [navOpen, setNavOpen] = useState(false);
  const { light, toggle } = useExperimentalTheme();

  const mode = (() => {
    const m = systemStatus?.live_mode?.mode;
    if (m === "live") return { label: "Live", color: "bg-green-500", text: "text-green-400" };
    if (m === "headless") return { label: "CLI", color: "bg-blue-500", text: "text-blue-400" };
    return { label: "Offline", color: "bg-red-500", text: "text-red-400" };
  })();

  const healthy = systemStatus?.status === "healthy";

  const handlePopOut = () => {
    window.open(window.location.href, "gimp-mcp", "width=480,height=720,menubar=no,toolbar=no,location=no");
  };

  return (
    <nav
      className={`h-12 border-b bg-background/80 backdrop-blur-sm flex items-center justify-between px-3 shrink-0 z-40 ${
        compactMode ? "border-t-2 border-t-amber-500/30" : ""
      }`}
    >
      {/* Left: compact nav dropdown or full title */}
      <div className="flex items-center gap-2 min-w-0">
        {compactMode ? (
          <div className="relative">
            <button
              onClick={() => setNavOpen(!navOpen)}
              className="flex items-center gap-1.5 px-2 py-1.5 rounded-md hover:bg-secondary text-xs font-medium"
            >
              <Menu className="w-3.5 h-3.5" />
              <span className="truncate max-w-24">{pageLabels[currentPage] || currentPage}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
            {navOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setNavOpen(false)} />
                <div className="absolute top-full left-0 mt-1 w-44 bg-popover border rounded-lg shadow-xl z-20 py-1 max-h-72 overflow-y-auto">
                  {Object.entries(pageLabels).map(([id, label]) => (
                    <button
                      key={id}
                      onClick={() => {
                        setCurrentPage(id);
                        setNavOpen(false);
                      }}
                      className={`w-full text-left px-3 py-1.5 text-xs hover:bg-secondary transition-colors ${
                        id === currentPage ? "text-primary font-medium" : "text-muted-foreground"
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        ) : (
          <h1 className="text-sm font-semibold truncate">{pageLabels[currentPage] || "GIMP MCP"}</h1>
        )}

        {/* Status dot */}
        <div className="flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 rounded-full ${healthy ? "bg-green-500" : "bg-red-500"}`} />
          {!compactMode && (
            <span className={`text-[11px] font-mono ${healthy ? "text-green-400" : "text-red-400"}`}>
              {healthy ? "healthy" : "degraded"}
            </span>
          )}
        </div>
      </div>

      {/* Right: controls */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={toggle}
          className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
          title={light ? "Switch to dark (experimental light mode)" : "Switch to light (experimental, ugly)"}
          aria-label="Toggle light mode (experimental)"
        >
          {light ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
        </button>

        {!compactMode && (
          <div className="flex items-center gap-1.5 px-2 py-1 bg-secondary rounded-full text-[11px] mr-1">
            <span className={`w-1.5 h-1.5 rounded-full ${mode.color}`} />
            <span className="text-muted-foreground font-medium">{mode.label}</span>
          </div>
        )}

        <button
          type="button"
          onClick={() => setLoggerOpen(true)}
          className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
          title="Logger"
        >
          <ScrollText className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={handlePopOut}
          className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground hidden md:inline-flex"
          title="Pop out to separate window"
        >
          <ExternalLink className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={toggleCompactMode}
          className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
          title={compactMode ? "Full mode" : "Companion mode"}
        >
          {compactMode ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
        </button>

        {!compactMode && (
          <button
            type="button"
            onClick={() => setHelpOpen(true)}
            className="p-1.5 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
            title="Help"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        )}
      </div>
    </nav>
  );
}
