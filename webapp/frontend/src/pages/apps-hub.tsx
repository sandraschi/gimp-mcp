import { ExternalLink, Globe, Search, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Badge,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui-core";

interface FleetApp {
  name: string;
  port: number;
  url: string;
  status: "reachable" | "unreachable";
  vite?: boolean;
}

const KNOWN_APPS: { name: string; port: number; vite?: boolean }[] = [
  { name: "gimp-mcp", port: 10772, vite: true },
  { name: "qcad-mcp", port: 10967, vite: true },
  { name: "freecad-mcp", port: 10945, vite: true },
  { name: "godot-mcp", port: 10992, vite: true },
  { name: "devices-mcp", port: 10716, vite: true },
  { name: "filesystem-mcp", port: 10743, vite: true },
  { name: "autohotkey-mcp", port: 10747, vite: true },
  { name: "depot-mcp", port: 10726, vite: true },
  { name: "multi-backup-mcp", port: 10798, vite: true },
  { name: "documentation-mcp", port: 10794 },
  { name: "email-mcp", port: 10813, vite: true },
  { name: "browser-mcp", port: 10780 },
  { name: "discord-mcp", port: 10756 },
  { name: "blender-mcp", port: 10848 },
  { name: "opencode-cli-mcp", port: 10950 },
  { name: "chitchat", port: 10974 },
  { name: "notion-mcp", port: 10811, vite: true },
  { name: "beyondcompare-mcp", port: 10840 },
  { name: "resonite-mcp", port: 10978 },
  { name: "colony-mcp", port: 10970 },
  { name: "pywinauto-mcp", port: 10788 },
  { name: "reaper-mcp", port: 10796 },
  { name: "virtualdj-mcp", port: 10876 },
  { name: "myai", port: 10888 },
  { name: "deepfang", port: 10957 },
];

export default function AppsHub() {
  const [apps, setApps] = useState<FleetApp[]>([]);
  const [search, setSearch] = useState("");
  const [scanning, setScanning] = useState(true);

  useEffect(() => {
    const scan = async () => {
      const results: FleetApp[] = [];
      for (const app of KNOWN_APPS) {
        const url = app.vite
          ? `http://localhost:${app.port}`
          : `http://localhost:${app.port}/api/health`;
        try {
          const resp = await fetch(url, { signal: AbortSignal.timeout(2000) });
          results.push({
            ...app,
            url: `http://localhost:${app.port}`,
            status: resp.ok ? "reachable" : "unreachable",
          });
        } catch {
          // If health check fails, try root
          try {
            const resp = await fetch(`http://localhost:${app.port}`, {
              signal: AbortSignal.timeout(2000),
            });
            results.push({
              ...app,
              url: `http://localhost:${app.port}`,
              status: resp.ok ? "reachable" : "unreachable",
            });
          } catch {
            results.push({
              ...app,
              url: `http://localhost:${app.port}`,
              status: "unreachable",
            });
          }
        }
      }
      setApps(results);
      setScanning(false);
    };
    scan();
  }, []);

  const filtered = apps.filter((a) =>
    a.name.toLowerCase().includes(search.toLowerCase()),
  );

  const reachable = apps.filter((a) => a.status === "reachable").length;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Apps Hub</h2>
          <p className="text-muted-foreground mt-1">
            Fleet Discovery —{" "}
            {scanning
              ? "Scanning..."
              : `${reachable} / ${apps.length} apps reachable`}
          </p>
        </div>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search apps..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-secondary border-none rounded-xl focus:ring-2 focus:ring-primary/50 transition-all outline-none"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((app) => (
          <a
            key={app.name}
            href={app.url}
            target="_blank"
            rel="noopener noreferrer"
            className="group"
          >
            <Card className="bg-card/60 backdrop-blur-sm border-primary/5 hover:border-primary/20 hover:shadow-lg transition-all">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-primary" />
                    <span className="font-mono text-sm font-semibold">
                      {app.name}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        app.status === "reachable" ? "default" : "secondary"
                      }
                      className="text-[10px]"
                    >
                      {app.status === "reachable" ? "UP" : "DOWN"}
                    </Badge>
                    <ExternalLink className="w-3.5 h-3.5 text-muted-foreground group-hover:text-foreground transition-colors" />
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {app.status === "reachable" ? (
                    <Wifi className="w-3 h-3 text-green-400" />
                  ) : (
                    <WifiOff className="w-3 h-3 text-red-400" />
                  )}
                  <span className="font-mono">:{app.port}</span>
                  <span className="ml-auto">{app.url}</span>
                </div>
              </CardContent>
            </Card>
          </a>
        ))}
      </div>
    </div>
  );
}
