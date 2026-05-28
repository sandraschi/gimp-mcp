/**
 * MCP API client for GIMP MCP webapp Agent Lab.
 * Backend: POST /api/v1/tool on port 10773 (proxied via Vite /api).
 */

const API_BASE = "/api";

export async function getBackendHealth(): Promise<{ ok: boolean; error?: string }> {
  try {
    const r = await fetch(`${API_BASE}/health`);
    if (!r.ok) return { ok: false, error: `HTTP ${r.status}` };
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : "Network error" };
  }
}

interface MCPResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export async function callTool<T>(
  tool: string,
  params: Record<string, unknown> = {},
): Promise<MCPResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}/v1/tool`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool, params }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return (await response.json()) as MCPResponse<T>;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

export interface CaptureRecord {
  id: string;
  outputPath: string;
  capturedAt: string;
  previewBase64?: string;
}

const CAPTURES_KEY = "gimp_mcp_capture_gallery";

export function loadCaptures(): CaptureRecord[] {
  try {
    const raw = localStorage.getItem(CAPTURES_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as CaptureRecord[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveCapture(record: CaptureRecord): void {
  const existing = loadCaptures();
  const next = [record, ...existing].slice(0, 24);
  localStorage.setItem(CAPTURES_KEY, JSON.stringify(next));
}

export function clearCaptures(): void {
  localStorage.removeItem(CAPTURES_KEY);
}
