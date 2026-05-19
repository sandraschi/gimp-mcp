import { Code2, ExternalLink, FileCode } from "lucide-react";
import { useState } from "react";
import { Card, CardContent } from "../components/ui-core";

export default function ApiDocsPage() {
  const [view, setView] = useState<"swagger" | "redoc">("swagger");
  const backendBase = "http://localhost:10773";

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">API Documentation</h2>
          <p className="text-muted-foreground mt-1">
            REST API reference — FastMCP 3.2 backend
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setView("swagger")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              view === "swagger"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-muted-foreground hover:text-foreground"
            }`}
          >
            <Code2 className="w-4 h-4 inline mr-1.5" />
            Swagger
          </button>
          <button
            type="button"
            onClick={() => setView("redoc")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              view === "redoc"
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-muted-foreground hover:text-foreground"
            }`}
          >
            <FileCode className="w-4 h-4 inline mr-1.5" />
            ReDoc
          </button>
          <a
            href={
              view === "swagger"
                ? `${backendBase}/docs`
                : `${backendBase}/redoc`
            }
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-secondary text-muted-foreground hover:text-foreground rounded-lg text-sm font-medium transition-all"
          >
            <ExternalLink className="w-4 h-4 inline mr-1.5" />
            Open
          </a>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2">
        {[
          { method: "GET", path: "/api/health", desc: "Server health check" },
          { method: "GET", path: "/api/status", desc: "System status" },
          { method: "GET", path: "/api/sota", desc: "SOTA feature manifest" },
          { method: "GET", path: "/api/skills", desc: "List skills" },
          {
            method: "GET",
            path: "/api/skills/{name}",
            desc: "Read skill content",
          },
          { method: "POST", path: "/mcp", desc: "MCP HTTP endpoint" },
          { method: "GET", path: "/sse", desc: "MCP SSE stream" },
        ].map((ep) => (
          <div
            key={ep.path}
            className="shrink-0 flex items-center gap-2 bg-secondary/50 border border-border/30 rounded-lg px-3 py-1.5"
          >
            <span
              className={`text-[10px] font-bold uppercase ${
                ep.method === "GET" ? "text-green-400" : "text-amber-400"
              }`}
            >
              {ep.method}
            </span>
            <span className="text-xs font-mono">{ep.path}</span>
            <span className="text-[10px] text-muted-foreground">{ep.desc}</span>
          </div>
        ))}
      </div>

      <Card className="overflow-hidden border-primary/10">
        <CardContent className="p-0">
          <iframe
            src={view === "swagger" ? "/docs" : "/redoc"}
            title="API Documentation"
            className="w-full h-[calc(100vh-16rem)] border-0"
          />
        </CardContent>
      </Card>
    </div>
  );
}
