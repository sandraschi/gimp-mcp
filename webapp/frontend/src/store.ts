import { create } from "zustand";

export interface GimpSystemStatus {
  status: string;
  live_mode: {
    mode: "live" | "headless" | "offline";
    last_check?: string;
    details?: string;
  };
  config?: {
    gimp_executable: string;
    max_concurrent_processes: number;
  };
  server_name?: string;
  version?: string;
  fastmcp?: string;
  sota?: {
    package?: string;
    fastmcp?: string;
    sota_target?: string;
    features?: Record<string, unknown>;
  };
}

export interface Toast {
  id: string;
  message: string;
  variant: "success" | "error" | "info";
  timestamp: number;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "warn" | "error";
  message: string;
}

interface AppState {
  currentPage: string;
  systemStatus: GimpSystemStatus | null;
  toasts: Toast[];
  logs: LogEntry[];
  loggerOpen: boolean;
  helpOpen: boolean;
  setCurrentPage: (page: string) => void;
  setSystemStatus: (status: GimpSystemStatus | null) => void;
  addToast: (message: string, variant: Toast["variant"]) => void;
  removeToast: (id: string) => void;
  addLog: (level: LogEntry["level"], message: string) => void;
  clearLogs: () => void;
  setLoggerOpen: (open: boolean) => void;
  setHelpOpen: (open: boolean) => void;
}

export const useStore = create<AppState>((set, get) => ({
  currentPage: "dashboard",
  systemStatus: null,
  toasts: [],
  logs: [],
  loggerOpen: false,
  helpOpen: false,

  setCurrentPage: (page) => set({ currentPage: page }),

  setSystemStatus: (status) => set({ systemStatus: status }),

  addToast: (message, variant) => {
    const id = crypto.randomUUID();
    const toast: Toast = { id, message, variant, timestamp: Date.now() };
    set((s) => ({ toasts: [...s.toasts, toast] }));
    setTimeout(() => get().removeToast(id), 4000);
  },

  removeToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),

  addLog: (level, message) => {
    const entry: LogEntry = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      level,
      message,
    };
    set((s) => ({ logs: [...s.logs, entry].slice(-200) }));
  },

  clearLogs: () => set({ logs: [] }),

  setLoggerOpen: (open) => set({ loggerOpen: open }),

  setHelpOpen: (open) => set({ helpOpen: open }),
}));
