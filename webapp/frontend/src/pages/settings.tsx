import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui-core";
import { Key, Eye, EyeOff, CheckCircle2, XCircle, Sparkles, Loader2, Cpu, RefreshCw } from "lucide-react";
import { useStore } from "../store";

const PROVIDERS = [
  { id: "gemini", label: "Google Gemini", doc: "https://aistudio.google.com/app/apikey" },
  { id: "stability", label: "Stability AI", doc: "https://platform.stability.ai/account/keys" },
  { id: "bfl", label: "BFL / Flux", doc: "https://api.bfl.ml/settings" },
];

export default function SettingsPage() {
  const addToast = useStore((s) => s.addToast);
  const [keys, setKeys] = useState<Record<string, string>>({});
  const [status, setStatus] = useState<Record<string, boolean>>({});
  const [revealed, setRevealed] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [generating, setGenerating] = useState(false);
  const [genResult, setGenResult] = useState<string | null>(null);
  const [llmDetected, setLlmDetected] = useState<Record<string, any>>({});
  const [llmProvider, setLlmProvider] = useState("disabled");
  const [llmModel, setLlmModel] = useState("");
  const [llmScanning, setLlmScanning] = useState(false);

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((data) => setStatus(data.providers || {}))
      .catch(() => {});
  }, []);

  const saveKey = async (provider: string) => {
    setSaving((s) => ({ ...s, [provider]: true }));
    try {
      const resp = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, api_key: keys[provider] || "" }),
      });
      const data = await resp.json();
      setStatus(data.providers || {});
      addToast(`${provider} API key saved`, "success");
    } catch {
      addToast(`Failed to save ${provider} key`, "error");
    } finally {
      setSaving((s) => ({ ...s, [provider]: false }));
    }
  };

  const testGenerate = async (provider: string) => {
    setGenerating(true);
    setGenResult(null);
    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, prompt: "A beautiful mountain landscape at sunset, photorealistic" }),
      });
      const data = await resp.json();
      if (data.success) {
        setGenResult(data.image_path);
        addToast(`Image generated with ${provider}`, "success");
      } else {
        addToast(`Generation failed: ${data.error}`, "error");
      }
    } catch (err: any) {
      addToast(`Generation error: ${err.message}`, "error");
    } finally {
      setGenerating(false);
    }
  };

  const scanLocalLLM = async () => {
    setLlmScanning(true);
    try {
      const resp = await fetch("/api/llm/detect");
      const data = await resp.json();
      setLlmDetected(data);
      const available: string[] = [];
      if (data.ollama?.running) available.push("ollama");
      if (data.lmstudio?.running) available.push("lmstudio");
      if (available.length > 0 && llmProvider === "disabled") {
        setLlmProvider(available[0]);
        const models = data[available[0]]?.models || [];
        if (models.length > 0) setLlmModel(models[0]);
      }
      addToast(`LLM scan: ${available.length > 0 ? available.join(", ") + " detected" : "none found"}`, "info");
    } catch {
      addToast("Failed to scan for local LLM", "error");
    } finally {
      setLlmScanning(false);
    }
  };

  const saveLocalLLM = async () => {
    try {
      const resp = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scope: "local_llm", provider: llmProvider, model: llmModel }),
      });
      const data = await resp.json();
      setLlmDetected(data.detected || {});
      addToast(`Local LLM set to ${llmProvider} / ${llmModel}`, "success");
    } catch {
      addToast("Failed to save local LLM settings", "error");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold">Settings</h2>
        <p className="text-muted-foreground mt-1">AI image generation API keys</p>
      </div>

      <div className="space-y-4">
        {PROVIDERS.map((p) => (
          <Card key={p.id} className="bg-card/60 border-primary/5">
            <CardContent className="p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Key className="w-5 h-5 text-primary" />
                  <div>
                    <h3 className="font-semibold">{p.label}</h3>
                    <p className="text-xs text-muted-foreground">
                      {status[p.id] ? (
                        <span className="text-green-400 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Configured
                        </span>
                      ) : (
                        <span className="text-yellow-400 flex items-center gap-1">
                          <XCircle className="w-3 h-3" /> Not configured
                        </span>
                      )}
                    </p>
                  </div>
                </div>
                <a href={p.doc} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline">
                  Get API key
                </a>
              </div>

              <div className="flex gap-2">
                <div className="relative flex-1">
                  <input
                    type={revealed[p.id] ? "text" : "password"}
                    placeholder={`${p.label} API key`}
                    value={keys[p.id] || ""}
                    onChange={(e) => setKeys((k) => ({ ...k, [p.id]: e.target.value }))}
                    className="w-full bg-secondary border-none rounded-lg px-4 py-2 pr-10 text-sm font-mono outline-none focus:ring-2 focus:ring-primary/50"
                  />
                  <button
                    type="button"
                    onClick={() => setRevealed((r) => ({ ...r, [p.id]: !r[p.id] }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {revealed[p.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => saveKey(p.id)}
                  disabled={saving[p.id] || !keys[p.id]}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-all"
                >
                  {saving[p.id] ? <Loader2 className="w-4 h-4 animate-spin" /> : "Save"}
                </button>
                <button
                  type="button"
                  onClick={() => testGenerate(p.id)}
                  disabled={generating || !status[p.id]}
                  className="px-4 py-2 bg-secondary text-foreground rounded-lg text-sm font-medium hover:bg-secondary/80 disabled:opacity-50 transition-all flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4" />
                  Test
                </button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <h2 className="text-xl font-bold pt-4 border-t border-border/30">Local LLM</h2>
      <p className="text-sm text-muted-foreground -mt-6 mb-4">
        Connect Ollama or LM Studio for local AI inference. No API key needed.
      </p>

      <Card className="bg-card/60 border-primary/5">
        <CardContent className="p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Cpu className="w-5 h-5 text-primary" />
              <div>
                <h3 className="font-semibold">Local Inference</h3>
                <p className="text-xs text-muted-foreground">
                  {llmDetected.ollama?.running || llmDetected.lmstudio?.running ? (
                    <span className="text-green-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      {llmDetected.ollama?.running ? "Ollama" : ""}
                      {llmDetected.ollama?.running && llmDetected.lmstudio?.running ? " + " : ""}
                      {llmDetected.lmstudio?.running ? "LM Studio" : ""} detected
                    </span>
                  ) : (
                    <span className="text-muted-foreground">Not detected</span>
                  )}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={scanLocalLLM}
              disabled={llmScanning}
              className="flex items-center gap-2 px-3 py-2 bg-secondary rounded-lg text-sm hover:bg-secondary/80 transition-all"
            >
              <RefreshCw className={`w-4 h-4 ${llmScanning ? "animate-spin" : ""}`} />
              Scan
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Provider</label>
              <select
                value={llmProvider}
                onChange={(e) => {
                  setLlmProvider(e.target.value);
                  const models = e.target.value !== "disabled" ? llmDetected[e.target.value]?.models || [] : [];
                  if (models.length > 0 && !models.includes(llmModel)) setLlmModel(models[0]);
                }}
                className="w-full bg-secondary border-none rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="disabled">Disabled</option>
{llmDetected.ollama?.running && <option value="ollama">Ollama (:11434)</option>}
{llmDetected.lmstudio?.running && <option value="lmstudio">LM Studio (:1234)</option>}
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Model</label>
              <select
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                className="w-full bg-secondary border-none rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/50"
              >
                <option value="">Select model</option>
                {(llmDetected[llmProvider]?.models || []).map((m: string) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="button"
              onClick={saveLocalLLM}
              disabled={llmProvider === "disabled" || !llmModel}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-all"
            >
              Save
            </button>
          </div>
        </CardContent>
      </Card>

      {genResult && (
        <Card className="bg-card/60 border-green-500/20">
          <CardHeader>
            <CardTitle className="text-sm">Last Generation</CardTitle>
            <CardDescription>Generated image path: {genResult}</CardDescription>
          </CardHeader>
        </Card>
      )}
    </div>
  );
}
