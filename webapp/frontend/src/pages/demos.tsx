import { AnimatePresence, motion } from "framer-motion";
import {
  CheckCircle2,
  Image as ImageIcon,
  Loader2,
  Palette,
  Play,
  Sparkles,
  SquareStack,
  Wand2,
  XCircle,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Card } from "../components/ui-core";

interface Demo {
  id: string;
  description: string;
  steps: number;
  file?: string;
  error?: string;
}

interface StepResult {
  step: string;
  label: string;
  success: boolean;
  has_snapshot?: boolean;
  error?: string;
  result?: Record<string, unknown>;
}

interface RunResult {
  success: boolean;
  demo_id: string;
  total_steps: number;
  completed: number;
  results: StepResult[];
}

const demoIcons: Record<string, typeof Sparkles> = {
  portrait_retouch: Wand2,
  product_photo: ImageIcon,
  meme_generator: Palette,
  gmic_art_pipeline: SquareStack,
};

export default function DemosPage() {
  const [demos, setDemos] = useState<Demo[]>([]);
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<RunResult | null>(null);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/demos")
      .then((r) => r.json())
      .then((d) => setDemos(d.demos || []))
      .catch(() => setError("Failed to load demos"));
  }, []);

  const runDemo = useCallback(async (demoId: string) => {
    setRunning(demoId);
    setResults(null);
    setCurrentStep(-1);
    setError("");

    try {
      const r = await fetch("/api/demos/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ demo_id: demoId }),
      });
      const data: RunResult = await r.json();
      setResults(data);

      // Animate through steps
      for (let i = 0; i < data.results.length; i++) {
        setCurrentStep(i);
        await new Promise((r) => setTimeout(r, 400));
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setRunning(null);
      setCurrentStep(-1);
    }
  }, []);

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-amber-400" />
            Demo Studio
          </h1>
          <p className="text-slate-400 mt-1">
            One-click multi-step GIMP automation demos — watch the AI edit images in real time
          </p>
        </div>
        {results && (
          <div className="text-sm text-slate-400">
            {results.completed}/{results.total_steps} steps passed
          </div>
        )}
      </div>

      {/* Results panel */}
      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4"
          >
            <div className="flex items-center gap-2 text-emerald-400 font-medium mb-3">
              <CheckCircle2 className="h-4 w-4" />
              Demo {results.demo_id} — {results.completed}/{results.total_steps} steps completed
            </div>
            <div className="space-y-1.5">
              {results.results.map((step, i) => {
                const isCurrent = i === currentStep && running;
                const done = i < (currentStep >= 0 ? currentStep + 1 : 0);
                return (
                  <div
                    key={step.step}
                    className={`flex items-center gap-3 text-sm py-1 px-2 rounded transition-colors ${
                      isCurrent ? "bg-blue-500/10 text-blue-300" : done ? "text-slate-300" : "text-slate-600"
                    }`}
                  >
                    {isCurrent ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin shrink-0" />
                    ) : step.success ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5 text-red-500 shrink-0" />
                    )}
                    <span className="font-mono text-xs text-slate-500 w-24 shrink-0">{step.step}</span>
                    <span>{step.label}</span>
                    {step.has_snapshot && <ImageIcon className="h-3 w-3 text-blue-400 shrink-0" />}
                    {step.error && <span className="text-red-400 text-xs ml-2">{step.error}</span>}
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Demo grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {demos.map((demo) => {
          const Icon = demoIcons[demo.id] || Sparkles;
          const isRunning = running === demo.id;
          return (
            <Card
              key={demo.id}
              className={`border-slate-800 bg-slate-950/50 p-5 transition-all ${
                isRunning ? "ring-2 ring-blue-500/50" : results?.demo_id === demo.id ? "ring-1 ring-emerald-500/30" : ""
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-amber-400" />
                  <div>
                    <h3 className="text-white font-medium text-sm">{demo.id.replace(/_/g, " ")}</h3>
                    <span className="text-xs text-slate-500">{demo.steps} steps</span>
                  </div>
                </div>
                <button
                  onClick={() => runDemo(demo.id)}
                  disabled={isRunning}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    isRunning
                      ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                      : "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20"
                  }`}
                >
                  {isRunning ? <Loader2 className="h-3 w-3 animate-spin" /> : <Play className="h-3 w-3" />}
                  {isRunning ? "Running..." : "Run Demo"}
                </button>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {demo.description || "No description available."}
              </p>
              {demo.file && <p className="text-[10px] text-slate-600 mt-2 font-mono">{demo.file}</p>}
            </Card>
          );
        })}
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/5 p-4 text-red-400 text-sm">{error}</div>
      )}
    </div>
  );
}
