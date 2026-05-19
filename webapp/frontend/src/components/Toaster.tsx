import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Info, X, XCircle } from "lucide-react";
import { useStore } from "../store";

export function Toaster() {
  const toasts = useStore((s) => s.toasts);
  const removeToast = useStore((s) => s.removeToast);

  const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-green-400" />,
    error: <XCircle className="w-4 h-4 text-red-400" />,
    info: <Info className="w-4 h-4 text-blue-400" />,
  };

  const borders = {
    success: "border-green-500/30",
    error: "border-red-500/30",
    info: "border-blue-500/30",
  };

  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2 pointer-events-none">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 bg-card border ${borders[t.variant]} rounded-xl shadow-xl backdrop-blur-sm max-w-sm`}
          >
            {icons[t.variant]}
            <span className="text-sm text-foreground flex-1">{t.message}</span>
            <button
              onClick={() => removeToast(t.id)}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
