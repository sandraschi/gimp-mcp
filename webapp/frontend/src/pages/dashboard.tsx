import {
  Activity,
  Cpu,
  Image,
  Layers,
  Server,
  Terminal,
  Wifi,
  WifiOff,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui-core";
import { useStore } from "../store";

interface PortStatus {
  port: number;
  label: string;
  status: "open" | "closed";
}

export default function Dashboard() {
  const systemStatus = useStore((s) => s.systemStatus);
  const addLog = useStore((s) => s.addLog);
  const [portStatuses, setPortStatuses] = useState<PortStatus[]>([
    { port: 10772, label: "Frontend (Vite)", status: "closed" },
    { port: 10773, label: "Backend (FastAPI)", status: "closed" },
    { port: 10824, label: "GIMP Bridge", status: "closed" },
  ]);
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const checkPorts = async () => {
      const updated = [...portStatuses];
      for (const p of updated) {
        try {
          const resp = await fetch(`http://localhost:${p.port}/api/health`);
          p.status = resp.ok ? "open" : "closed";
        } catch {
          // Port closed - expected for GIMP bridge
          if (p.port === 10824) {
            p.status =
              systemStatus?.live_mode?.mode === "live" ? "open" : "closed";
          }
        }
      }
      setPortStatuses([...updated]);
    };

    checkPorts();
    const interval = setInterval(checkPorts, 10000);
    return () => clearInterval(interval);
  }, [systemStatus]);

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(
      () => setUptime(Math.floor((Date.now() - startTime) / 1000)),
      1000,
    );
    return () => clearInterval(interval);
  }, []);

  const getModeIcon = () => {
    const mode = systemStatus?.live_mode?.mode;
    if (mode === "live") return <Zap className="w-5 h-5 text-green-400" />;
    if (mode === "headless")
      return <Terminal className="w-5 h-5 text-blue-400" />;
    return <WifiOff className="w-5 h-5 text-red-400" />;
  };

  const formatUptime = (s: number) => {
    const m = Math.floor(s / 60);
    const h = Math.floor(m / 60);
    if (h > 0) return `${h}h ${m % 60}m`;
    if (m > 0) return `${m}m ${s % 60}s`;
    return `${s}s`;
  };

  const statCards = [
    {
      label: "Uptime",
      value: formatUptime(uptime),
      icon: <Activity className="w-5 h-5 text-primary" />,
    },
    {
      label: "Connection",
      value: systemStatus?.live_mode?.mode || "Unknown",
      icon: getModeIcon(),
      capitalize: true,
    },
    {
      label: "FastMCP",
      value: systemStatus?.fastmcp || "3.2",
      icon: <Server className="w-5 h-5 text-purple-400" />,
    },
    {
      label: "GIMP Path",
      value: systemStatus?.config?.gimp_executable || "Not detected",
      icon: <Image className="w-5 h-5 text-amber-400" />,
      mono: true,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <p className="text-muted-foreground mt-1">
          GIMP MCP v{systemStatus?.version || "4.0.0"} — FastMCP 3.2 SOTA
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <Card
            key={i}
            className="bg-card/60 backdrop-blur-sm border-primary/5 hover:border-primary/20 transition-all"
          >
            <CardContent className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  {card.label}
                </span>
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

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Port Reservation Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {portStatuses.map((p) => (
              <div
                key={p.port}
                className="flex items-center justify-between py-2 border-b border-border/30 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-2 h-2 rounded-full ${p.status === "open" ? "bg-green-500" : "bg-red-500"}`}
                  />
                  <div>
                    <span className="font-mono text-sm font-medium">
                      {p.port}
                    </span>
                    <span className="text-xs text-muted-foreground ml-2">
                      {p.label}
                    </span>
                  </div>
                </div>
                <span
                  className={`text-xs font-medium ${p.status === "open" ? "text-green-400" : "text-red-400"}`}
                >
                  {p.status === "open" ? "OPEN" : "CLOSED"}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {systemStatus?.sota?.features && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">SOTA Features</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(systemStatus.sota.features).map(([key, val]) => (
                <div
                  key={key}
                  className="flex items-center gap-2 bg-secondary/30 px-3 py-2 rounded-lg"
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${val ? "bg-green-500" : "bg-red-500"}`}
                  />
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
