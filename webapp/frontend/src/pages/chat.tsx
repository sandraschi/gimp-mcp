import { Bot, Download, Eraser, Loader2, Mic, MicOff, Send, Terminal, User, Volume2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { createSpeechRecognition, isSTTSupported, isTTSSupported, speak } from "../common/speech";
import { Card } from "../components/ui-core";
import { useStore } from "../store";

const STORAGE_KEY = "gimp-mcp-chat-history";
const PERSONALITY_KEY = "gimp-mcp-chat-personality";
const MODEL_KEY = "gimp-mcp-chat-model";

const MAX_MESSAGES = 100;

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  ts?: string;
}

interface Personality {
  id: string;
  label: string;
  prompt: string;
}

const PERSONALITIES: Personality[] = [
  {
    id: "gimp-expert",
    label: "GIMP Expert",
    prompt:
      "You are a GIMP image editing expert. Answer concisely with concrete tool names, menu paths, and keyboard shortcuts. Reference the available tools when suggesting operations.",
  },
  {
    id: "research-assistant",
    label: "Research Assistant",
    prompt:
      "You are a thorough research assistant. Provide detailed explanations, compare techniques, and cite relevant GIMP documentation or community knowledge.",
  },
  {
    id: "expert-reviewer",
    label: "Expert Reviewer",
    prompt:
      "You are a critical reviewer of image editing workflows. Analyze the user's approach, suggest optimizations, and highlight potential issues with their current method.",
  },
  {
    id: "quick-summarizer",
    label: "Quick Summarizer",
    prompt:
      "You are a concise summarizer. Provide brief answers in 2-3 sentences. Focus on actionable steps without elaboration.",
  },
  {
    id: "custom",
    label: "Custom",
    prompt: "",
  },
];

const EXAMPLE_PROMPTS = [
  { category: "Editing", text: "How do I crop an image to 800x600 pixels?" },
  { category: "Editing", text: "Make this image warmer and more vibrant" },
  { category: "Editing", text: "Remove the background from this photo" },
  { category: "Layers", text: "Explain how layer masks work in GIMP" },
  { category: "Tools", text: "Compare the healing brush vs clone tool" },
  { category: "Batch", text: "How do I batch resize 50 images at once?" },
  { category: "Filters", text: "Apply a watercolor effect to this image" },
  { category: "Advanced", text: "How can I use GIMP for photo retouching?" },
];

// @ts-expect-error
async function checkBackendHealth(): Promise<{
  ok: boolean;
  error?: string;
  provider?: string;
  model?: string;
}> {
  try {
    const r = await fetch("/api/health");
    if (!r.ok) return { ok: false, error: `HTTP ${r.status}` };
    return { ok: true };
  } catch (e) {
    return {
      ok: false,
      error: e instanceof Error ? e.message : "Network error",
    };
  }
}

function buildSystemPrompt(skillContent: string, personality: Personality, customPrompt: string): string {
  const base = skillContent || "You are a helpful GIMP assistant.";
  if (personality.id === "custom") return customPrompt || base;
  return `${base}\n\n---\n\n## Role\n${personality.prompt}`;
}

export default function ChatPage() {
  const addToast = useStore((s) => s.addToast);
  const addLog = useStore((s) => s.addLog);

  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as Message[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch {}
    return [];
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [skillContent, setSkillContent] = useState("");
  const [skillName, setSkillName] = useState("gimp-expert");
  const [providerStatus, setProviderStatus] = useState<"detecting" | "online" | "offline">("detecting");
  const [providerDetail, setProviderDetail] = useState("");
  const [modelName, setModelName] = useState(() => {
    try {
      return localStorage.getItem(MODEL_KEY) || "";
    } catch {
      return "";
    }
  });
  const [personalityId, setPersonalityId] = useState(() => {
    try {
      return localStorage.getItem(PERSONALITY_KEY) || "gimp-expert";
    } catch {
      return "gimp-expert";
    }
  });
  const [customPrompt, setCustomPrompt] = useState("");
  const [listening, setListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState("");
  const recognitionRef = useRef<ReturnType<typeof createSpeechRecognition> | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const personality = PERSONALITIES.find((p) => p.id === personalityId) || PERSONALITIES[0];

  const systemPrompt = buildSystemPrompt(skillContent, personality, customPrompt);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(PERSONALITY_KEY, personalityId);
  }, [personalityId]);

  useEffect(() => {
    localStorage.setItem(MODEL_KEY, modelName);
  }, [modelName]);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const resp = await fetch("/api/skills");
        const data = await resp.json();
        const skills: { name: string; uri: string }[] = data.skills || [];
        if (skills.length > 0) {
          const primary = skills[0];
          setSkillName(primary.name);
          const contentResp = await fetch(`/api/skills/${primary.name}`);
          const contentData = await contentResp.json();
          if (contentData.content) {
            setSkillContent(contentData.content);
            addLog("info", `Loaded skill: ${primary.name}`);
          }
        }
      } catch {
        addLog("warn", "Could not fetch skills");
      }
    };
    fetchSkills();
  }, [addLog]);

  useEffect(() => {
    const detectProvider = async () => {
      setProviderStatus("detecting");
      try {
        const resp = await fetch("/api/llm/detect");
        if (resp.ok) {
          const data = await resp.json();
          if (data.provider) {
            setProviderStatus("online");
            setProviderDetail(data.provider);
            if (data.model) setModelName(data.model);
            return;
          }
        }
      } catch {}
      setProviderStatus("offline");
      setProviderDetail("Not detected");
    };
    detectProvider();
  }, []);

  useEffect(() => {
    if (!isSTTSupported()) return;
    recognitionRef.current = createSpeechRecognition(
      (transcript, isFinal) => {
        if (isFinal) {
          setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
          setInterimTranscript("");
        } else {
          setInterimTranscript(transcript);
        }
      },
      () => setListening(false),
    );
    return () => {
      recognitionRef.current?.stop();
    };
  }, []);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      ts: new Date().toISOString(),
    };
    setMessages((m) => {
      const next = [...m, userMsg];
      return next.length > MAX_MESSAGES ? next.slice(-MAX_MESSAGES) : next;
    });
    setInput("");
    setLoading(true);
    addLog("info", `Chat: ${text}`);

    try {
      const historyForApi = messages.slice(-10).map((m) => ({
        role: m.role,
        content: m.content,
      }));
      historyForApi.push({ role: "user", content: text });

      const llmResp = await fetch("/api/llm/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [{ role: "system", content: systemPrompt }, ...historyForApi],
          model: modelName || undefined,
        }),
      });

      if (llmResp.ok) {
        const llmData = await llmResp.json();
        if (llmData.reply) {
          const aiMsg: Message = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: llmData.reply,
            ts: new Date().toISOString(),
          };
          setMessages((m) => {
            const next = [...m, aiMsg];
            return next.length > MAX_MESSAGES ? next.slice(-MAX_MESSAGES) : next;
          });
          setLoading(false);
          return;
        }
      }
    } catch {}

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          system: systemPrompt,
          history: messages.slice(-10).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      const data = await response.json();
      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.reply || data.message || "I received your message but could not generate a response.",
        ts: new Date().toISOString(),
      };
      setMessages((m) => {
        const next = [...m, aiMsg];
        return next.length > MAX_MESSAGES ? next.slice(-MAX_MESSAGES) : next;
      });

      if (data.error) {
        addToast("Chat error: " + data.error, "error");
        addLog("error", `Chat error: ${data.error}`);
      }
    } catch (err: any) {
      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: "system",
        content: "No AI backend available. Try setting up a local LLM in Settings or check your connection.",
        ts: new Date().toISOString(),
      };
      setMessages((m) => {
        const next = [...m, aiMsg];
        return next.length > MAX_MESSAGES ? next.slice(-MAX_MESSAGES) : next;
      });
      addLog("error", `Chat API error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages, personalityId, skillContent, customPrompt, modelName, systemPrompt, addToast, addLog]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const exportChat = () => {
    if (messages.length === 0) return;
    const lines = messages.map((m) => `[${m.ts || new Date().toISOString()}] ${m.role}: ${m.content}`);
    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gimp-mcp-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    addToast("Chat exported", "success");
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    addToast("Chat cleared", "info");
  };

  const toggleMic = () => {
    if (!recognitionRef.current) return;
    if (listening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  };

  const providerColor =
    providerStatus === "online" ? "bg-green-500" : providerStatus === "offline" ? "bg-red-500" : "bg-gray-500";

  const hasMessages = messages.length > 0;

  return (
    <div data-testid="chat-page" className="max-w-4xl mx-auto h-[calc(100vh-12rem)] flex flex-col">
      <div data-testid="chat-controls" className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">LLM Chat</h2>
          <p className="text-muted-foreground text-sm">
            {skillName ? `skill:${skillName}` : "Context-aware chat with MCP tool-calling"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={`w-1.5 h-1.5 rounded-full ${providerColor} animate-pulse`} />
            <span className="font-mono">
              {providerDetail || (providerStatus === "detecting" ? "Detecting..." : "Offline")}
            </span>
          </div>
          <select
            data-testid="personality-select"
            value={personalityId}
            onChange={(e) => setPersonalityId(e.target.value)}
            className="bg-zinc-800 text-zinc-100 border-zinc-600 rounded-lg px-2 py-1 text-xs font-mono"
          >
            {PERSONALITIES.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
          <button
            data-testid="chat-export"
            type="button"
            onClick={exportChat}
            disabled={!hasMessages}
            title="Export chat"
            className="p-1.5 rounded-lg transition-colors text-muted-foreground hover:text-foreground disabled:opacity-30"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            data-testid="chat-clear"
            type="button"
            onClick={clearChat}
            disabled={!hasMessages}
            title="Clear conversation"
            className="p-1.5 rounded-lg transition-colors text-muted-foreground hover:text-foreground disabled:opacity-30"
          >
            <Eraser className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mb-3 flex items-center gap-2">
        <input
          type="text"
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
          placeholder="Model name..."
          className="bg-zinc-800 text-zinc-100 border-zinc-600 rounded-lg px-2 py-1 text-xs font-mono w-48"
        />
        {personalityId === "custom" && (
          <input
            type="text"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Custom system prompt..."
            className="bg-zinc-800 text-zinc-100 border-zinc-600 rounded-lg px-2 py-1 text-xs font-mono flex-1"
          />
        )}
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <div data-testid="chat-messages" ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          {!hasMessages && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground text-sm max-w-md">
                <Bot className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="mb-4">Ask about GIMP operations, tools, or image editing techniques.</p>
                <div data-testid="example-prompts" className="flex flex-wrap justify-center gap-2">
                  {EXAMPLE_PROMPTS.slice(0, 6).map((ep) => (
                    <button
                      key={ep.text}
                      type="button"
                      onClick={() => {
                        setInput(ep.text);
                        setTimeout(() => sendMessage(), 50);
                      }}
                      className="px-3 py-1.5 text-xs rounded-full border border-zinc-700 bg-zinc-800/50 hover:bg-zinc-700 transition-colors"
                    >
                      {ep.text.length > 40 ? ep.text.slice(0, 40) + "..." : ep.text}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role !== "user" && (
                <div
                  className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    msg.role === "system" ? "bg-red-500/10" : "bg-primary/10"
                  }`}
                >
                  {msg.role === "system" ? (
                    <Terminal className="w-4 h-4 text-red-400" />
                  ) : (
                    <Bot className="w-4 h-4 text-primary" />
                  )}
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-primary/20 text-foreground rounded-br-md"
                    : msg.role === "system"
                      ? "bg-red-500/10 border border-red-500/20 text-red-300 rounded-bl-md"
                      : "bg-secondary/60 text-foreground rounded-bl-md"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">{msg.content}</div>
                  {msg.role === "assistant" && isTTSSupported() && (
                    <button
                      type="button"
                      onClick={() => {
                        speak(msg.content);
                      }}
                      title="Speak"
                      className="shrink-0 mt-0.5 p-1 rounded transition-colors text-slate-500 hover:text-white opacity-50 hover:opacity-100"
                    >
                      <Volume2 className="h-3 w-3" />
                    </button>
                  )}
                </div>
              </div>
              {msg.role === "user" && (
                <div className="shrink-0 w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <User className="w-4 h-4 text-blue-400" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="w-4 h-4 text-primary" />
              </div>
              <div className="bg-secondary/60 rounded-2xl rounded-bl-md px-4 py-3">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
              </div>
            </div>
          )}
        </div>

        <div className="border-t p-4">
          <div className="flex gap-2">
            {isSTTSupported() && (
              <button
                type="button"
                onClick={toggleMic}
                title={listening ? "Stop" : "Voice input"}
                className={`shrink-0 p-3 rounded-xl transition-all ${
                  listening
                    ? "bg-red-500/20 text-red-400 border border-red-500/30"
                    : "bg-secondary text-muted-foreground hover:text-foreground"
                }`}
              >
                {listening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>
            )}
            <textarea
              data-testid="chat-input"
              value={interimTranscript ? `${input} ${interimTranscript}` : input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                messages.length === 0 ? "Ask about GIMP operations, tools, or system status..." : "Type a message..."
              }
              rows={1}
              className="flex-1 bg-secondary border-none rounded-xl px-4 py-3 text-sm resize-none outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
            <button
              data-testid="chat-send"
              type="button"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="shrink-0 p-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 disabled:opacity-50 transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
