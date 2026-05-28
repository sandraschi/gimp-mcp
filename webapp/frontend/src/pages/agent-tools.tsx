import {
  Activity,
  Bot,
  Camera,
  GitPullRequest,
  ImageIcon,
  ScanEye,
  ShieldCheck,
  Boxes,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  callTool,
  clearCaptures,
  getBackendHealth,
  loadCaptures,
  saveCapture,
  type CaptureRecord,
} from "../api/mcp";

type TabId = "bridge" | "vision" | "validation" | "gallery" | "fleet" | "simart";

function ResultBox({ text }: { text: string | null }) {
  if (!text) return null;
  return (
    <pre className="mt-3 p-3 text-xs bg-muted rounded-lg overflow-x-auto whitespace-pre-wrap border border-border">
      {text}
    </pre>
  );
}

export default function AgentToolsPage() {
  const [tab, setTab] = useState<TabId>("bridge");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [captures, setCaptures] = useState<CaptureRecord[]>([]);

  const [outputPath, setOutputPath] = useState("D:/Temp/gimp_mcp/review.png");
  const [inputPath, setInputPath] = useState("D:/Temp/gimp_mcp/texture.png");
  const [targetPlatform, setTargetPlatform] = useState("unity");
  const [projectPath, setProjectPath] = useState("D:/Unity/MyProject");
  const [stagingDir, setStagingDir] = useState("D:/Temp/fleet_pipeline/gimp_staging");
  const [reviewDir, setReviewDir] = useState("D:/Temp/fleet_pipeline/gimp_staging/processed");

  const [simInputDir, setSimInputDir] = useState("D:/Temp/model_renders");
  const [simStagingDir, setSimStagingDir] = useState("D:/Temp/fleet_pipeline/sim_art");
  const [simPipeline, setSimPipeline] = useState("gazebo");
  const [simTemplate, setSimTemplate] = useState("gazebo_icon_256");
  const [simLayout, setSimLayout] = useState("4x4");

  const tabs: { id: TabId; label: string; icon: typeof Bot }[] = [
    { id: "bridge", label: "Bridge", icon: Bot },
    { id: "vision", label: "Vision", icon: ScanEye },
    { id: "validation", label: "Validation", icon: ShieldCheck },
    { id: "gallery", label: "Gallery", icon: ImageIcon },
    { id: "fleet", label: "Fleet", icon: GitPullRequest },
    { id: "simart", label: "Sim Art", icon: Boxes },
  ];

  useEffect(() => {
    setCaptures(loadCaptures());
  }, []);

  const run = async (tool: string, params: Record<string, unknown>) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await callTool(tool, params);
      setResult(JSON.stringify(res, null, 2));

      if (
        tool === "gimp_render_tool" &&
        params.operation === "capture_active" &&
        res.success &&
        res.data &&
        typeof res.data === "object"
      ) {
        const data = res.data as Record<string, unknown>;
        const record: CaptureRecord = {
          id: crypto.randomUUID(),
          outputPath: String(data.output_path ?? outputPath),
          capturedAt: new Date().toISOString(),
          previewBase64:
            typeof data.image_base64 === "string" ? data.image_base64 : undefined,
        };
        saveCapture(record);
        setCaptures(loadCaptures());
      }
    } catch (e) {
      setResult(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  const checkBackend = async () => {
    const r = await getBackendHealth();
    setBackendOk(r.ok);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agent Tools</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Phase 1–5: live bridge, canvas capture, validation, gallery, fleet handoff, sim art.
          </p>
        </div>
        <button
          type="button"
          onClick={checkBackend}
          className="px-3 py-1.5 text-sm bg-secondary rounded-md hover:bg-secondary/80"
        >
          Check backend
        </button>
      </div>

      {backendOk !== null && (
        <p className={`text-sm ${backendOk ? "text-green-500" : "text-red-500"}`}>
          Backend {backendOk ? "online" : "offline"} — run webapp start.ps1 if needed.
        </p>
      )}

      <div className="flex flex-wrap gap-2 border-b border-border pb-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => {
              setTab(t.id);
              setResult(null);
            }}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t.id
                ? "bg-primary text-primary-foreground"
                : "bg-accent text-muted-foreground hover:text-foreground"
            }`}
          >
            <t.icon className="w-4 h-4" />
            {t.label}
          </button>
        ))}
      </div>

      <div className="border border-border rounded-lg p-5 bg-card space-y-4">
        {tab === "bridge" && (
          <>
            <h2 className="font-semibold">Live bridge (Hands-In)</h2>
            <p className="text-sm text-muted-foreground">
              Start MCP Bridge in GIMP: Filters &gt; Development &gt; MCP &gt; Start MCP Bridge (:10824)
            </p>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() => run("gimp_bridge_tool", { operation: "status" })}
              >
                Bridge status
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("gimp_bridge_tool", { operation: "execution_mode" })}
              >
                Execution mode
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("gimp_bridge_tool", { operation: "ping" })}
              >
                Ping bridge
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("gimp_bridge_tool", { operation: "list_open_images" })}
              >
                List open images
              </button>
            </div>
          </>
        )}

        {tab === "vision" && (
          <>
            <h2 className="font-semibold">Vision capture</h2>
            <label className="block text-sm">
              Output path (capture_active)
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={outputPath}
                onChange={(e) => setOutputPath(e.target.value)}
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("gimp_render_tool", {
                    operation: "capture_active",
                    output_path: outputPath,
                    include_base64: true,
                  })
                }
              >
                <Camera className="w-4 h-4 inline mr-1" />
                Capture active canvas
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("gimp_render_tool", { operation: "get_image_summary" })}
              >
                Image summary
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() => run("gimp_render_tool", { operation: "bridge_status" })}
              >
                Bridge status
              </button>
            </div>
          </>
        )}

        {tab === "validation" && (
          <>
            <h2 className="font-semibold">Image QA validation</h2>
            <label className="block text-sm">
              Input image path
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={inputPath}
                onChange={(e) => setInputPath(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Target platform (audit_texture)
              <select
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={targetPlatform}
                onChange={(e) => setTargetPlatform(e.target.value)}
              >
                <option value="unity">unity</option>
                <option value="vrchat">vrchat</option>
                <option value="print">print</option>
              </select>
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("gimp_validation_tool", {
                    operation: "validate_image",
                    input_path: inputPath,
                  })
                }
              >
                Validate image
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_validation_tool", {
                    operation: "audit_texture",
                    input_path: inputPath,
                    target_platform: targetPlatform,
                  })
                }
              >
                Audit texture
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_validation_tool", {
                    operation: "check_alpha",
                    input_path: inputPath,
                    require_alpha: true,
                  })
                }
              >
                Check alpha
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_validation_tool", {
                    operation: "check_icc",
                    input_path: inputPath,
                  })
                }
              >
                Check ICC
              </button>
            </div>
          </>
        )}

        {tab === "gallery" && (
          <>
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">Capture gallery</h2>
              <button
                type="button"
                className="px-3 py-1.5 text-sm bg-secondary rounded-md"
                onClick={() => {
                  clearCaptures();
                  setCaptures([]);
                }}
              >
                Clear history
              </button>
            </div>
            {captures.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No captures yet. Use Vision tab with live bridge to capture the active canvas.
              </p>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {captures.map((c) => (
                  <div key={c.id} className="border border-border rounded-lg p-2 space-y-2">
                    {c.previewBase64 ? (
                      <img
                        src={`data:image/png;base64,${c.previewBase64}`}
                        alt="Capture preview"
                        className="w-full h-32 object-contain bg-muted rounded"
                      />
                    ) : (
                      <div className="w-full h-32 bg-muted rounded flex items-center justify-center text-xs text-muted-foreground">
                        No preview
                      </div>
                    )}
                    <p className="text-[11px] font-mono truncate" title={c.outputPath}>
                      {c.outputPath}
                    </p>
                    <p className="text-[10px] text-muted-foreground">{c.capturedAt}</p>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {tab === "fleet" && (
          <>
            <h2 className="font-semibold">Fleet handoff (blender → gimp → unity)</h2>
            <label className="block text-sm">
              Unity project path
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={projectPath}
                onChange={(e) => setProjectPath(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Texture path (push_unity / import_file)
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={inputPath}
                onChange={(e) => setInputPath(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Staging directory
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={stagingDir}
                onChange={(e) => setStagingDir(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Review folder (review_bundle)
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={reviewDir}
                onChange={(e) => setReviewDir(e.target.value)}
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("gimp_import_tool", {
                    operation: "push_unity",
                    source_path: inputPath,
                    project_path: projectPath,
                    staging_dir: stagingDir,
                  })
                }
              >
                Push texture to Unity
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_import_tool", {
                    operation: "from_blender_render",
                    staging_dir: stagingDir,
                    blender_operation: "screenshot_viewport",
                    output_path: `${stagingDir}/blender_renders/viewport.png`,
                  })
                }
              >
                Import from Blender render
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_vision_refine_tool", {
                    operation: "review_bundle",
                    input_dir: reviewDir,
                    target_platform: targetPlatform,
                  })
                }
              >
                Texture review bundle
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_import_tool", { operation: "list_staging", staging_dir: stagingDir })
                }
              >
                List staging
              </button>
            </div>
          </>
        )}

        {tab === "simart" && (
          <>
            <h2 className="font-semibold">Sim art (Gazebo / VRChat / atlases)</h2>
            <label className="block text-sm">
              Input directory
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={simInputDir}
                onChange={(e) => setSimInputDir(e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Staging directory
              <input
                className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                value={simStagingDir}
                onChange={(e) => setSimStagingDir(e.target.value)}
              />
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <label className="block text-sm">
                Pipeline
                <select
                  className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                  value={simPipeline}
                  onChange={(e) => setSimPipeline(e.target.value)}
                >
                  <option value="gazebo">gazebo</option>
                  <option value="vrchat">vrchat</option>
                </select>
              </label>
              <label className="block text-sm">
                Template
                <input
                  className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                  value={simTemplate}
                  onChange={(e) => setSimTemplate(e.target.value)}
                />
              </label>
              <label className="block text-sm">
                Atlas layout
                <input
                  className="mt-1 w-full px-3 py-2 bg-background border border-border rounded-md text-sm"
                  value={simLayout}
                  onChange={(e) => setSimLayout(e.target.value)}
                />
              </label>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm"
                onClick={() =>
                  run("gimp_sim_art_tool", {
                    operation: simPipeline === "vrchat" ? "vrchat_icon_batch" : "gazebo_model_icons",
                    input_dir: simInputDir,
                    staging_dir: simStagingDir,
                    template_id: simTemplate,
                  })
                }
              >
                Batch icons
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_sim_art_tool", {
                    operation: "build_atlas",
                    input_dir: `${simStagingDir}/gazebo_icons`,
                    output_path: `${simStagingDir}/atlases/atlas_${simLayout}.png`,
                    layout: simLayout,
                    staging_dir: simStagingDir,
                  })
                }
              >
                Build atlas
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_sim_art_tool", {
                    operation: "stage_for_robotics",
                    input_dir: `${simStagingDir}/gazebo_icons`,
                    staging_dir: simStagingDir,
                  })
                }
              >
                Stage for robotics
              </button>
              <button
                type="button"
                disabled={loading}
                className="px-4 py-2 bg-secondary rounded-md text-sm"
                onClick={() =>
                  run("gimp_sim_art_tool", {
                    operation: "list_templates",
                    staging_dir: simStagingDir,
                  })
                }
              >
                List templates
              </button>
            </div>
          </>
        )}

        {loading && (
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <Activity className="w-4 h-4 animate-pulse" />
            Running tool...
          </p>
        )}
        <ResultBox text={result} />
      </div>
    </div>
  );
}
