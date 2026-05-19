import { motion } from "framer-motion";
import { ExternalLink, HelpCircle, X } from "lucide-react";
import { useStore } from "../store";

export function HelpModal() {
  const helpOpen = useStore((s) => s.helpOpen);
  const setHelpOpen = useStore((s) => s.setHelpOpen);
  const setCurrentPage = useStore((s) => s.setCurrentPage);

  if (!helpOpen) return null;

  return (
    <div className="fixed inset-0 z-[9998] flex items-center justify-center">
      <div
        role="button"
        tabIndex={0}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm cursor-default"
        onClick={() => setHelpOpen(false)}
        onKeyDown={(e) => {
          if (e.key === "Escape") setHelpOpen(false);
        }}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative w-full max-w-xl max-h-[80vh] bg-card border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Help & Documentation</h2>
          </div>
          <button
            type="button"
            onClick={() => setHelpOpen(false)}
            className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm">
          <section>
            <h3 className="font-semibold text-foreground mb-2">
              GIMP MCP Overview
            </h3>
            <p className="text-muted-foreground">
              GIMP MCP is a FastMCP 3.2 server that lets AI agents control GIMP
              for professional image editing. It uses 8 portmanteau tools
              consolidating 50+ image operations.
            </p>
          </section>

          <section>
            <h3 className="font-semibold text-foreground mb-2">Pages</h3>
            <ul className="space-y-2 text-muted-foreground">
              <li>
                <strong className="text-foreground">Dashboard</strong> — Live
                stats, health, and port status
              </li>
              <li>
                <strong className="text-foreground">Apps Hub</strong> — Discover
                other MCP webapps on the fleet
              </li>
              <li>
                <strong className="text-foreground">Chat</strong> — LLM chat
                with MCP tool-calling
              </li>
              <li>
                <strong className="text-foreground">Tools</strong> — Browse
                portmanteau tools and schemas
              </li>
              <li>
                <strong className="text-foreground">Skills</strong> — View
                FastMCP skills and documentation
              </li>
              <li>
                <strong className="text-foreground">API Docs</strong> — Swagger
                / ReDoc for the REST API
              </li>
              <li>
                <strong className="text-foreground">Status</strong> — System
                health and diagnostics
              </li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold text-foreground mb-2">
              Connection Modes
            </h3>
            <ul className="space-y-2 text-muted-foreground">
              <li>
                <strong className="text-green-400">Live Bridge</strong> — TCP
                connection to running GIMP instance (port 10774)
              </li>
              <li>
                <strong className="text-blue-400">Headless</strong> — Batch GIMP
                subprocess for CLI operations
              </li>
              <li>
                <strong className="text-red-400">Offline</strong> — GIMP not
                detected; limited functionality
              </li>
            </ul>
          </section>

          <section>
            <h3 className="font-semibold text-foreground mb-2">
              Documentation
            </h3>
            <p className="text-muted-foreground">
              Full docs at{" "}
              <code className="text-xs bg-secondary px-1.5 py-0.5 rounded">
                docs/
              </code>{" "}
              in the repository. See{" "}
              <code className="text-xs bg-secondary px-1.5 py-0.5 rounded">
                llms.txt
              </code>{" "}
              for LLM-facing capability summary.
            </p>
          </section>

          <button
            type="button"
            onClick={() => {
              setHelpOpen(false);
              setCurrentPage("help");
            }}
            className="flex items-center justify-center gap-2 w-full px-4 py-2.5 bg-primary/10 hover:bg-primary/20 text-primary text-sm font-medium rounded-lg transition-colors"
          >
            <ExternalLink className="w-4 h-4" />
            Open full Help page
          </button>
        </div>
      </motion.div>
    </div>
  );
}
