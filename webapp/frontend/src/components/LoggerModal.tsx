import { motion } from "framer-motion";
import { ScrollText, Trash2, X } from "lucide-react";
import { useStore } from "../store";

export function LoggerModal() {
  const loggerOpen = useStore((s) => s.loggerOpen);
  const setLoggerOpen = useStore((s) => s.setLoggerOpen);
  const logs = useStore((s) => s.logs);
  const clearLogs = useStore((s) => s.clearLogs);

  if (!loggerOpen) return null;

  const levelStyles: Record<string, string> = {
    info: "text-blue-400",
    warn: "text-yellow-400",
    error: "text-red-400",
  };

  return (
    <div className="fixed inset-0 z-[9998] flex items-center justify-center">
      <div
        role="button"
        tabIndex={0}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm cursor-default"
        onClick={() => setLoggerOpen(false)}
        onKeyDown={(e) => {
          if (e.key === "Escape") setLoggerOpen(false);
        }}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative w-full max-w-3xl max-h-[80vh] bg-card border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <div className="flex items-center gap-2">
            <ScrollText className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Global Logger</h2>
            <span className="text-xs text-muted-foreground">
              ({logs.length} entries)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={clearLogs}
              className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
              title="Clear logs"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setLoggerOpen(false)}
              className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1">
          {logs.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">
              No log entries yet.
            </p>
          ) : (
            logs.map((entry) => (
              <div
                key={entry.id}
                className="flex gap-2 hover:bg-secondary/30 px-2 py-0.5 rounded"
              >
                <span className="text-muted-foreground shrink-0">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </span>
                <span
                  className={`shrink-0 uppercase ${levelStyles[entry.level]}`}
                >
                  [{entry.level}]
                </span>
                <span className="text-foreground/80 break-all">
                  {entry.message}
                </span>
              </div>
            ))
          )}
        </div>
      </motion.div>
    </div>
  );
}
