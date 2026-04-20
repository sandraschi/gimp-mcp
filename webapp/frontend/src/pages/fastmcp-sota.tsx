import { useEffect, useState } from 'react';
import { Sparkles, BookOpen, Boxes, LayoutTemplate, Package, Cpu } from 'lucide-react';

interface SotaPayload {
  package?: string;
  fastmcp?: string;
  sota_target?: string;
  features?: {
    sampling?: boolean;
    prompts_registered?: number;
    resources?: string[];
    skills_provider?: boolean;
    skills_uris?: string[];
    prefab_tools?: boolean;
    mcpb_packaging?: boolean;
  };
}

export default function FastmcpSotaPage() {
  const [data, setData] = useState<SotaPayload | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch('/api/sota');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const j = (await res.json()) as SotaPayload;
        if (!cancelled) setData(j);
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : 'Failed to load /api/sota');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const f = data?.features;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Sparkles className="w-7 h-7 text-primary" />
          FastMCP 3.2 SOTA
        </h2>
        <p className="text-muted-foreground mt-1">
          Sampling, prompts, resources, skills (skill://), prefab UI tools, and MCPB packaging — surfaced for the fleet dashboard.
        </p>
      </div>

      {err && (
        <div className="rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm">
          {err}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-card rounded-xl border border-border/50 p-5 space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Cpu className="w-4 h-4" />
            Runtime
          </div>
          <p className="text-lg font-semibold">{data?.package ?? 'gimp-mcp'}</p>
          <p className="text-sm text-muted-foreground">fastmcp {data?.fastmcp ?? '…'} · target {data?.sota_target ?? '3.2'}</p>
        </div>

        <div className="bg-card rounded-xl border border-border/50 p-5 space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <BookOpen className="w-4 h-4" />
            Prompts
          </div>
          <p className="text-2xl font-bold">{f?.prompts_registered ?? '—'}</p>
          <p className="text-xs text-muted-foreground">Registered MCP prompt templates</p>
        </div>

        <div className="bg-card rounded-xl border border-border/50 p-5 space-y-3 md:col-span-2">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Boxes className="w-4 h-4" />
            Resources
          </div>
          <ul className="text-sm font-mono space-y-1 break-all">
            {(f?.resources ?? []).map((u) => (
              <li key={u}>{u}</li>
            ))}
            {!f?.resources?.length && <li className="text-muted-foreground">No data yet</li>}
          </ul>
        </div>

        <div className="bg-card rounded-xl border border-border/50 p-5 space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <LayoutTemplate className="w-4 h-4" />
            Skills & prefab
          </div>
          <ul className="text-sm space-y-1">
            <li>Skills provider: <span className="font-medium">{f?.skills_provider ? 'on' : 'off'}</span></li>
            <li>Prefab tools: <span className="font-medium">{f?.prefab_tools ? 'on' : 'off'}</span></li>
          </ul>
          <ul className="text-xs font-mono text-muted-foreground break-all mt-2">
            {(f?.skills_uris ?? []).map((u) => (
              <li key={u}>{u}</li>
            ))}
          </ul>
        </div>

        <div className="bg-card rounded-xl border border-border/50 p-5 space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Package className="w-4 h-4" />
            MCPB
          </div>
          <p className="text-sm">
            Packaging: <span className="font-medium">{f?.mcpb_packaging ? 'enabled' : '—'}</span>
          </p>
          <p className="text-xs text-muted-foreground">Run <code className="bg-secondary px-1 rounded">python build_mcpb.py</code> at repo root.</p>
        </div>
      </div>

      <div className="bg-secondary/30 rounded-xl border border-border/40 p-4 text-sm text-muted-foreground">
        <strong className="text-foreground">Sampling:</strong>{' '}
        {f?.sampling ? 'Host may call ctx.sample for agentic_gimp_workflow and advanced tools.' : '—'}
      </div>
    </div>
  );
}
