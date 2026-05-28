import clsx from "clsx";
import {
  Activity,
  Bot,
  BookOpen,
  Code2,
  Cog,
  Copy,
  Globe,
  HelpCircle,
  Image,
  Layers,
  LayoutDashboard,
  MessageSquare,
  ScrollText,
  Sparkles,
  Terminal,
  Wand2,
} from "lucide-react";
import { useStore } from "../store";

export function Sidebar() {
  const currentPage = useStore((s) => s.currentPage);
  const setCurrentPage = useStore((s) => s.setCurrentPage);
  const systemStatus = useStore((s) => s.systemStatus);
  const setLoggerOpen = useStore((s) => s.setLoggerOpen);

  const mainNavItems = [
    { id: "agent-tools", icon: Bot, label: "Agent Tools" },
    { id: "dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { id: "apps-hub", icon: Globe, label: "Apps Hub" },
    { id: "chat", icon: MessageSquare, label: "Chat" },
    { id: "image-editor", icon: Image, label: "Editor" },
    { id: "batch-processor", icon: Copy, label: "Batch" },
    { id: "layer-manager", icon: Layers, label: "Layers" },
    { id: "tools-explorer", icon: Wand2, label: "Tools" },
    { id: "skills", icon: BookOpen, label: "Skills" },
    { id: "help", icon: HelpCircle, label: "Help" },
    { id: "api-docs", icon: Code2, label: "API Docs" },
    { id: "system-status", icon: Activity, label: "Status" },
    { id: "fastmcp-sota", icon: Sparkles, label: "FastMCP 3.2" },
    { id: "script-fu-console", icon: Terminal, label: "Script-Fu" },
    { id: "settings", icon: Cog, label: "Settings" },
  ];

  const bottomNavItems = [
    { icon: ScrollText, label: "Logger", action: () => setLoggerOpen(true) },
  ];

  const getModeColor = () => {
    const mode = systemStatus?.live_mode?.mode;
    if (mode === "live") return "bg-green-500";
    if (mode === "headless") return "bg-blue-500";
    return "bg-red-500";
  };

  return (
    <aside className="w-56 bg-card border-r flex flex-col shrink-0 z-50">
      <div className="h-16 flex items-center px-5 border-b shrink-0">
        <div className="flex items-center gap-2 font-bold text-lg">
          <Wand2 className="w-5 h-5 text-primary" />
          <span>GIMP MCP</span>
        </div>
      </div>

      <div className="p-3 flex flex-col gap-0.5 overflow-y-auto flex-1">
        {mainNavItems.map((item) => (
          <button
            type="button"
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={clsx(
              "flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-200",
              currentPage === item.id
                ? "bg-primary/10 text-primary hover:bg-primary/15"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground",
            )}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </button>
        ))}
      </div>

      <div className="p-3 border-t shrink-0 space-y-1">
        {bottomNavItems.map((item) => (
          <button
            type="button"
            key={item.label}
            onClick={item.action}
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-all w-full"
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </button>
        ))}
      </div>

      <div className="px-4 pb-3 shrink-0">
        <div className="bg-secondary/50 rounded-lg px-3 py-2">
          <div className="flex items-center gap-2">
            <span className={`w-1.5 h-1.5 rounded-full ${getModeColor()}`} />
            <span className="text-[11px] text-muted-foreground font-mono">
              {systemStatus?.live_mode?.mode || "offline"}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
