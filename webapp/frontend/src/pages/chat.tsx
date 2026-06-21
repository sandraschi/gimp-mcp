import { Bot, Loader2, Send, Terminal, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "../components/ui-core";
import { useStore } from "../store";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
}

export default function ChatPage() {
  const addToast = useStore((s) => s.addToast);
  const addLog = useStore((s) => s.addLog);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I am the GIMP MCP assistant.\n\n" +
        "- Try asking about image editing operations\n" +
        "- Or send a modification request like \"make this image warmer\"\n" +
        "- If a local LLM (Ollama/LM Studio) is configured, I'll use it for smarter responses",
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [llmProvider, setLlmProvider] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    addLog("info", `Chat: ${text}`);

    try {
      // Try local LLM first
      const chatHistory = messages.slice(-10).map((m) => ({
        role: m.role,
        content: m.content,
      }));
      chatHistory.push({ role: "user", content: text });

      const llmResp = await fetch("/api/llm/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: chatHistory }),
      });

      if (llmResp.ok) {
        const llmData = await llmResp.json();
        if (llmData.reply) {
          const aiMsg: Message = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: llmData.reply,
            timestamp: Date.now(),
          };
          setMessages((m) => [...m, aiMsg]);
          setLlmProvider("local");
          setLoading(false);
          return;
        }
      }
    } catch {
      // Local LLM not available, fall back to cloud
    }

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: messages
            .slice(-10)
            .map((m) => ({ role: m.role, content: m.content })),
        }),
      });

      const data = await response.json();

      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          data.reply ||
          data.message ||
          "I received your message but could not generate a response.",
        timestamp: Date.now(),
      };
      setMessages((m) => [...m, aiMsg]);
      setLlmProvider("cloud");

      if (data.error) {
        addToast("Chat error: " + data.error, "error");
        addLog("error", `Chat error: ${data.error}`);
      }
    } catch (err: any) {
      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: "system",
        content: `No AI backend available. Try setting up a local LLM in Settings or check your connection.`,
        timestamp: Date.now(),
      };
      setMessages((m) => [...m, aiMsg]);
      addLog("error", `Chat API error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-12rem)] flex flex-col">
      <div className="mb-4">
        <h2 className="text-2xl font-bold">LLM Chat</h2>
        <p className="text-muted-foreground">
          Context-aware chat with MCP tool-calling support
        </p>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
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
                {msg.content}
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
          <div className="flex items-center justify-between mb-2">
            {llmProvider && (
              <span className="text-[10px] text-muted-foreground font-mono">
                {llmProvider === "local" ? "Local LLM" : "Cloud API"}
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about GIMP operations, tools, or system status..."
              rows={1}
              className="flex-1 bg-secondary border-none rounded-xl px-4 py-3 text-sm resize-none outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
            <button
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
