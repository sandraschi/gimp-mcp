import { Activity, Brain, ChevronRight, Image, Server, Terminal, WifiOff, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui-core";
import { useStore } from "../store";

interface PortStatus {
  port: number;
  label: string;
  status: "open" | "closed";
}

export default function Dashboard() {
  const systemStatus = useStore((s) => s.systemStatus);
  const setCurrentPage = useStore((s) => s.setCurrentPage);
  // @ts-expect-error
  const addLog = useStore((s) => s.addLog);
  const [portStatuses, setPortStatuses] = useState<PortStatus[]>([
    { port: 10772, label: "Frontend (Vite)", status: "closed" },
    { port: 10773, label: "Backend (FastAPI)", status: "closed" },
    { port: 10824, label: "GIMP Bridge", status: "closed" },
  ]);
  const [connected, setConnected] = useState(false);
  const [llmStatus, setLlmStatus] = useState<"detecting" | "online" | "offline">("detecting");
  const [llmProvider, setLlmProvider] = useState("");

  useEffect(() => {
    const checkPorts = async () => {
      const updated = [...portStatuses];
      let anyOpen = false;
      for (const p of updated) {
        try {
          const resp = await fetch(`http://localhost:${p.port}/api/health`);
          p.status = resp.ok ? "open" : "closed";
          if (resp.ok) anyOpen = true;
        } catch {
          if (p.port === 10824) {
            p.status = systemStatus?.live_mode?.mode === "live" ? "open" : "closed";
            if (p.status === "open") anyOpen = true;
          }
        }
      }
      setPortStatuses([...updated]);
      setConnected(anyOpen);
    };

    checkPorts();
    const interval = setInterval(checkPorts, 10000);
    return () => clearInterval(interval);
  }, [systemStatus]);

  useEffect(() => {
    const detectLlm = async () => {
      setLlmStatus("detecting");
      try {
        const resp = await fetch("/api/llm/detect");
        if (resp.ok) {
          const data = await resp.json();
          const ollama = data.ollama?.running;
          const lmstudio = data.lmstudio?.running;
          if (ollama || lmstudio) {
            setLlmStatus("online");
            const label = ollama ? "Ollama" : "LM Studio";
            const models = ollama
              ? (data.ollama.models || []).slice(0, 3).join(", ")
              : (data.lmstudio.models || []).slice(0, 3).join(", ");
            setLlmProvider(models ? `${label} (${models})` : label);
            return;
          }
        }
      } catch {}
      setLlmStatus("offline");
      setLlmProvider("");
    };
    detectLlm();
  }, []);

  const getModeIcon = () => {
    const mode = systemStatus?.live_mode?.mode;
    if (mode === "live") return <Zap className="w-5 h-5 text-green-400" />;
    if (mode === "headless") return <Terminal className="w-5 h-5 text-blue-400" />;
    return <WifiOff className="w-5 h-5 text-red-400" />;
  };

  const formatUptime = (s: number | undefined) => {
    if (s === undefined || s === null) return "—";
    const m = Math.floor(s / 60);
    const h = Math.floor(m / 60);
    if (h > 0) return `${h}h ${m % 60}m`;
    if (m > 0) return `${m}m ${s % 60}s`;
    return `${s}s`;
  };

  const mode = systemStatus?.live_mode?.mode;
  const isLive = mode === "live";

  const heroBanner = connected
    ? {
        bg: "bg-gradient-to-r from-green-500/10 via-emerald-500/5 to-transparent",
        border: "border-green-500/20",
        icon: <Zap className="w-6 h-6 text-green-400" />,
        title: isLive ? "Live Bridge — Connected" : "Headless Mode — Active",
        sub: isLive
          ? "GIMP running with bridge plugin. All tools available."
          : "No running GIMP detected. Tools fall back to gimp-console-3.exe. Some features limited.",
      }
    : {
        bg: "bg-gradient-to-r from-red-500/10 via-orange-500/5 to-transparent",
        border: "border-red-500/20",
        icon: <WifiOff className="w-6 h-6 text-red-400" />,
        title: "Backend Unreachable",
        sub: "Backend server not responding on port 10773. Start the backend and try refreshing.",
      };

  const statCards = [
    {
      label: "Uptime",
      value: connected ? formatUptime(systemStatus?.uptime_seconds as number | undefined) : "—",
      icon: <Activity className="w-5 h-5 text-primary" />,
      testid: "kpi-server",
    },
    {
      label: "Connection",
      value: systemStatus?.live_mode?.mode || (connected ? "online" : "offline"),
      icon: getModeIcon(),
      capitalize: true,
      testid: "kpi-connection",
    },
    {
      label: "FastMCP",
      value: connected ? systemStatus?.fastmcp || "3.x" : "—",
      icon: <Server className="w-5 h-5 text-purple-400" />,
      testid: "kpi-fastmcp",
    },
    {
      label: "GIMP Path",
      value: connected ? systemStatus?.config?.gimp_executable || "Not detected" : "—",
      icon: <Image className="w-5 h-5 text-amber-400" />,
      mono: true,
      testid: "kpi-gimp-path",
    },
  ];

  const llmBadgeColor =
    llmStatus === "online"
      ? "bg-green-500/10 text-green-400 border-green-500/20"
      : llmStatus === "detecting"
        ? "bg-gray-500/10 text-gray-400 border-gray-500/20"
        : "bg-amber-500/10 text-amber-400 border-amber-500/20";
  const llmBadgeDot =
    llmStatus === "online" ? "bg-green-500" : llmStatus === "detecting" ? "bg-gray-500" : "bg-amber-500";

  return (
    <div data-testid="dashboard" className="max-w-6xl mx-auto space-y-6">
      <div className={`rounded-xl border p-5 ${heroBanner.bg} ${heroBanner.border}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="shrink-0">{heroBanner.icon}</div>
            <div>
              <h2 className="text-lg font-bold">{heroBanner.title}</h2>
              <p className="text-sm text-muted-foreground mt-0.5">{heroBanner.sub}</p>
            </div>
          </div>
          <span
            data-testid="backend-dot"
            className={`shrink-0 w-3 h-3 rounded-full ${connected ? "bg-green-500" : "bg-red-500"} animate-pulse`}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <Card
            key={i}
            data-testid={card.testid}
            className="bg-card/60 backdrop-blur-sm border-primary/5 hover:border-primary/20 transition-all"
          >
            <CardContent className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{card.label}</span>
                {card.icon}
              </div>
              <div
                className={`text-xl font-bold truncate ${card.capitalize ? "capitalize" : ""} ${card.mono ? "font-mono text-xs" : ""}`}
              >
                {card.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Port Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {portStatuses.map((p) => (
                <div
                  key={p.port}
                  className="flex items-center justify-between py-2 border-b border-border/30 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-2 h-2 rounded-full ${p.status === "open" ? "bg-green-500" : "bg-red-500"}`} />
                    <div>
                      <span className="font-mono text-sm font-medium">{p.port}</span>
                      <span className="text-xs text-muted-foreground ml-2">{p.label}</span>
                    </div>
                  </div>
                  <span className={`text-xs font-medium ${p.status === "open" ? "text-green-400" : "text-red-400"}`}>
                    {p.status === "open" ? "OPEN" : "CLOSED"}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              <div className="flex items-center justify-between">
                <span>Local LLM</span>
                <span
                  className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${llmBadgeColor}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${llmBadgeDot}`} />
                  {llmStatus === "online" ? "Online" : llmStatus === "detecting" ? "Detecting..." : "Offline"}
                </span>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {llmStatus === "online" && llmProvider && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Brain className="w-4 h-4 text-primary shrink-0" />
                <span className="font-mono text-xs">{llmProvider}</span>
              </div>
            )}
            {llmStatus === "offline" && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  No local LLM detected. Install Ollama or LM Studio to unlock AI-powered features without cloud API
                  keys.
                </p>
                <div className="flex gap-2">
                  <a
                    href="https://ollama.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
                  >
                    Install Ollama
                    <ChevronRight className="w-3 h-3" />
                  </a>
                  <button
                    type="button"
                    onClick={() => setCurrentPage("settings")}
                    className="inline-flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg bg-primary/10 hover:bg-primary/20 text-primary transition-colors"
                  >
                    Go to Settings
                    <ChevronRight className="w-3 h-3" />
                  </button>
                </div>
                <p className="text-[11px] text-muted-foreground/60">
                  Your RTX 4090 can run models locally for free — no API keys needed.
                </p>
              </div>
            )}
            {llmStatus === "detecting" && (
              <p className="text-sm text-muted-foreground">
                Scanning for Ollama (port 11434) and LM Studio (port 1234)...
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {systemStatus?.sota?.features && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">SOTA Features</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(systemStatus.sota.features).map(([key, val]) => (
                <div key={key} className="flex items-center gap-2 bg-secondary/30 px-3 py-2 rounded-lg">
                  <span className={`w-1.5 h-1.5 rounded-full ${val ? "bg-green-500" : "bg-red-500"}`} />
                  <span className="text-xs font-mono">{key}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
