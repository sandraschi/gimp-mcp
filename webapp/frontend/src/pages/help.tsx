import { AnimatePresence, motion } from "framer-motion";
import {
  Blocks,
  type Cog,
  Cpu,
  FileCode,
  Globe,
  Package,
  Plug,
  Terminal,
} from "lucide-react";
import { useState } from "react";
import { Card } from "../components/ui-core";

interface Tab {
  id: string;
  label: string;
  icon: typeof Cog;
}

const tabs: Tab[] = [
  { id: "install", label: "Install", icon: Package },
  { id: "architecture", label: "Architecture", icon: Blocks },
  { id: "gimp-bridge", label: "GIMP Bridge", icon: Plug },
  { id: "plugins", label: "Plugins", icon: FileCode },
  { id: "cli-api", label: "CLI & API", icon: Terminal },
];

function CodeBlock({ code }: { code: string }) {
  return (
    <pre className="bg-gray-950 text-gray-100 text-xs font-mono p-4 rounded-lg overflow-x-auto border border-gray-800 whitespace-pre-wrap">
      {code}
    </pre>
  );
}

function TabContent({
  children,
  id,
}: {
  children: React.ReactNode;
  id: string;
}) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={id}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        transition={{ duration: 0.2 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-lg font-semibold text-foreground mt-6 mb-3 first:mt-0">
      {children}
    </h3>
  );
}

export default function HelpPage() {
  const [activeTab, setActiveTab] = useState("install");

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Help & Documentation</h2>
        <p className="text-muted-foreground mt-1">
          GIMP MCP Server v4.0.0 — FastMCP 3.2 SOTA
        </p>
      </div>

      <div className="flex gap-1 flex-wrap border-b border-border/50 pb-0">
        {tabs.map((tab) => {
          const active = activeTab === tab.id;
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all border-b-2 ${
                active
                  ? "border-primary text-primary bg-primary/5"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <Card className="p-6">
        <TabContent id={activeTab}>
          {activeTab === "install" && <InstallContent />}
          {activeTab === "architecture" && <ArchitectureContent />}
          {activeTab === "gimp-bridge" && <GimpBridgeContent />}
          {activeTab === "plugins" && <PluginsContent />}
          {activeTab === "cli-api" && <CliApiContent />}
        </TabContent>
      </Card>
    </div>
  );
}

function InstallContent() {
  return (
    <div className="space-y-4 text-sm text-muted-foreground">
      <p>
        Follow these steps to set up the GIMP MCP Server with FastMCP 3.2 and
        the Fleet Standard web application.
      </p>

      <SectionHeading>Prerequisites</SectionHeading>
      <ul className="list-disc list-inside space-y-1 text-sm">
        <li>
          <strong className="text-foreground">GIMP 3.2+</strong> — standalone
          install (NOT Windows Store; CLI batch mode is unavailable in the Store
          version)
        </li>
        <li>
          <strong className="text-foreground">Python 3.12+</strong> — required
          for FastMCP 3.2
        </li>
        <li>
          <strong className="text-foreground">uv</strong> — recommended for
          high-performance dependency management
        </li>
      </ul>

      <SectionHeading>1. Install GIMP 3.2+</SectionHeading>
      <p>
        Download GIMP 3.2+ from <span className="text-primary">gimp.org</span>.
        Use the standalone Windows installer (not the Microsoft Store version).
        Default install path:
      </p>
      <CodeBlock code="C:\Program Files\GIMP 3\bin\gimp-console-3.0.exe" />

      <SectionHeading>2. Clone & Install</SectionHeading>
      <CodeBlock
        code={`git clone https://github.com/sandraschi/gimp-mcp.git
cd gimp-mcp
uv sync`}
      />

      <SectionHeading>3. Configure (Optional)</SectionHeading>
      <p>
        Create a{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          config.yaml
        </code>{" "}
        to manually point to your GIMP executable if not auto-detected:
      </p>
      <CodeBlock
        code={`gimp_executable: "C:\\\\Program Files\\\\GIMP 3\\\\bin\\\\gimp-console-3.0.exe"`}
      />

      <SectionHeading>4. Start the Webapp</SectionHeading>
      <p>Launch everything (backend + frontend + bridge):</p>
      <CodeBlock code={`.\\start.ps1`} />
      <p>Or with GIMP restart (kills old GIMP, launches fresh with bridge):</p>
      <CodeBlock code={`.\\start.ps1 -RestartGimp`} />
      <p>
        Using <strong className="text-foreground">just</strong> recipes:
      </p>
      <CodeBlock
        code={`just start        # webapp only
just start-gimp   # webapp + GIMP restart
just serve        # backend only (reload on changes)`}
      />

      <SectionHeading>5. Verify</SectionHeading>
      <ul className="list-disc list-inside space-y-1 text-sm">
        <li>
          Open <span className="text-primary">http://localhost:10772</span> in
          your browser
        </li>
        <li>Check the Dashboard for live port status</li>
        <li>
          Visit Tools Explorer to verify all 17 portmanteau tools are listed
        </li>
        <li>
          Check bridge status:{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            just bridge-status
          </code>
        </li>
      </ul>
    </div>
  );
}

function ArchitectureContent() {
  return (
    <div className="space-y-4 text-sm text-muted-foreground">
      <p>
        GIMP MCP follows a multi-layer architecture with clear separation of
        concerns:
      </p>

      <SectionHeading>Layer Overview</SectionHeading>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
        {[
          {
            icon: Cpu,
            label: "MCP Server Layer",
            desc: "FastMCP 3.2 server with 17 portmanteau tools consolidating GIMP's ~1000 PDB procedures. Exposes tools, prompts, resources, and skills via MCP protocol.",
            ports: "CLI (stdio) + HTTP (port 10773)",
          },
          {
            icon: Globe,
            label: "Webapp Backend",
            desc: "FastAPI HTTP server (uvicorn). Serves REST endpoints and FastMCP HTTP transport for the frontend.",
            ports: "Port 10773",
          },
          {
            icon: Globe,
            label: "Webapp Frontend",
            desc: "React 19 / Vite SPA with 12 pages: Dashboard, Chat, Editor, Tools, Skills, API Docs, Status, and more.",
            ports: "Port 10772",
          },
          {
            icon: Plug,
            label: "GIMP Bridge",
            desc: "TCP server running inside GIMP 3.2+ as a GIMP plugin. Enables real-time PDB command execution.",
            ports: "Port 10824",
          },
        ].map((layer) => {
          const Icon = layer.icon;
          return (
            <div
              key={layer.label}
              className="bg-secondary/20 rounded-xl p-4 border border-border/30 space-y-2"
            >
              <div className="flex items-center gap-2">
                <Icon className="w-4 h-4 text-primary" />
                <h4 className="text-sm font-semibold text-foreground">
                  {layer.label}
                </h4>
              </div>
              <p className="text-xs">{layer.desc}</p>
              <span className="text-[11px] font-mono text-muted-foreground bg-secondary/50 px-2 py-0.5 rounded">
                {layer.ports}
              </span>
            </div>
          );
        })}
      </div>

      <SectionHeading>Portmanteau Design</SectionHeading>
      <p>
        Instead of 50+ individual tools, GIMP MCP consolidates operations into 9
        portmanteau tools. Each tool accepts an{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          operation
        </code>{" "}
        parameter to select the specific action. This reduces context overhead
        for LLMs while maintaining full GIMP capability.
      </p>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
        {[
          ["gimp_file", "6"],
          ["gimp_transform", "7"],
          ["gimp_color", "12"],
          ["gimp_filter", "8"],
          ["gimp_layer", "8"],
          ["gimp_analysis", "8"],
          ["gimp_batch", "6"],
          ["gimp_system", "8"],
          ["gimp_pdb", "∞"],
          ["gimp_workspace", "10"],
          ["gimp_channel", "8"],
          ["gimp_animation", "5"],
          ["gimp_paths", "8"],
          ["gimp_parasites", "9"],
          ["gimp_gmic", "4"],
          ["gimp_gegl", "2"],
          ["gimp_color_management", "7"],
        ].map(([name, ops]) => (
          <div
            key={name}
            className="bg-secondary/30 px-3 py-2 rounded-lg text-xs font-mono flex justify-between"
          >
            <span className="text-foreground">{name}</span>
            <span className="text-muted-foreground">{ops}</span>
          </div>
        ))}
      </div>

      <SectionHeading>Live vs Headless Modes</SectionHeading>
      <ul className="list-disc list-inside space-y-1 text-sm">
        <li>
          <strong className="text-green-400">Live Bridge</strong> — TCP
          connection to a running GIMP 3 instance for real-time operations
        </li>
        <li>
          <strong className="text-blue-400">Headless CLI</strong> — Batch mode
          via{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            gimp-console-3.exe
          </code>{" "}
          for automated workflows without a GUI
        </li>
      </ul>
    </div>
  );
}

function GimpBridgeContent() {
  return (
    <div className="space-y-4 text-sm text-muted-foreground">
      <p>
        The GIMP Bridge enables real-time bidirectional communication between
        the MCP server and a running GIMP 3.2+ instance.
      </p>

      <SectionHeading>How It Works</SectionHeading>
      <ol className="list-decimal list-inside space-y-2 text-sm">
        <li>
          A <strong className="text-foreground">GIMP plugin</strong> (
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            gimp_mcp_bridge.py
          </code>
          ) runs inside GIMP and starts a TCP server on port 10824
        </li>
        <li>
          The <strong className="text-foreground">bridge wrapper</strong> (
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            bridge_wrapper.py
          </code>
          ) in the MCP server connects to this TCP server
        </li>
        <li>
          Python code snippets are sent as JSON over TCP and executed on GIMP's
          main thread via GLib idle callbacks
        </li>
        <li>Results are serialized back to the MCP server as JSON responses</li>
      </ol>

      <SectionHeading>PDB Proxy Tool</SectionHeading>
      <p>
        The{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          gimp_pdb
        </code>{" "}
        tool is a universal escape hatch that can call any GIMP PDB procedure by
        name. This gives you access to GIMP's full ~1000-procedure library:
      </p>
      <CodeBlock
        code={`# Get GIMP version
gimp_pdb("gimp-version", [])

# Feather a selection
gimp_pdb("gimp-selection-feather", [image_id, 5.0])

# Apply Gaussian blur
gimp_pdb("plug-in-gauss", [image_id, layer_id, 5.0, 5.0, 0])

# Set a text layer font
gimp_pdb("gimp-text-layer-set-font", [layer_id, "Arial"])`}
      />

      <SectionHeading>Check Bridge Status</SectionHeading>
      <p>Verify the bridge is running from the terminal:</p>
      <CodeBlock
        code={`# Check TCP listener
just bridge-status
# Output: Bridge active on port 10824 (PID 12345)

# Or via PowerShell
Get-NetTCPConnection -LocalPort 10824`}
      />
      <p>
        The Dashboard page also shows bridge status with a green indicator when
        connected.
      </p>
    </div>
  );
}

function PluginsContent() {
  return (
    <div className="space-y-4 text-sm text-muted-foreground">
      <p>
        GIMP MCP includes a bridge plugin that runs inside GIMP itself, enabling
        real-time AI control.
      </p>

      <SectionHeading>Bridge Plugin</SectionHeading>
      <p>
        The main bridge plugin is{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          gimp_mcp_bridge.py
        </code>{" "}
        — a
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          Gimp.PlugIn
        </code>{" "}
        subclass that:
      </p>
      <ul className="list-disc list-inside space-y-1 text-sm mt-2">
        <li>
          Starts a TCP listener on{" "}
          <strong className="text-foreground">127.0.0.1:10824</strong>
        </li>
        <li>
          Accepts JSON payloads with{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">{`{"code": "..."}`}</code>
        </li>
        <li>Executes code on GIMP's main thread via GLib idle callbacks</li>
        <li>
          Provides{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            Gimp
          </code>
          ,{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            pdb
          </code>
          ,{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            GLib
          </code>{" "}
          globals to executed snippets
        </li>
        <li>
          Sends back{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">{`{"result": "..."}`}</code>{" "}
          or{" "}
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">{`{"error": "..."}`}</code>
        </li>
      </ul>

      <SectionHeading>Installation to GIMP</SectionHeading>
      <p>The plugin is installed to GIMP's plug-ins directory:</p>
      <CodeBlock
        code={`# Install via just
just bridge-install

# Copies to:
# %APPDATA%\\GIMP\\3.2\\plug-ins\\gimp_mcp_bridge\\
# %APPDATA%\\GIMP\\3.0\\plug-ins\\gimp_mcp_bridge\\`}
      />
      <p>Then restart GIMP and start the bridge from the menu:</p>
      <CodeBlock
        code={`<Image> / Filters / Development / MCP / Start MCP Bridge`}
      />

      <SectionHeading>Plugin Architecture</SectionHeading>
      <p>
        The bridge plugin extends{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          Gimp.PlugIn
        </code>{" "}
        and follows GIMP 3's plugin protocol:
      </p>
      <ul className="list-disc list-inside space-y-1 text-sm">
        <li>
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            do_query_procedures()
          </code>{" "}
          — registers
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            gimp-mcp-bridge-start
          </code>
        </li>
        <li>
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            do_create_procedure()
          </code>{" "}
          — defines the procedure metadata and menu location
        </li>
        <li>
          <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
            run()
          </code>{" "}
          — starts the background TCP listener thread and GLib idle polling loop
        </li>
      </ul>

      <SectionHeading>Extending</SectionHeading>
      <p>
        The server also supports a plugin system via{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          GimpToolPlugin
        </code>
        . Create a Python class inheriting from{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          GimpToolPlugin
        </code>
        , implement{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          register_tools(app)
        </code>
        , and place it in the plugins directory. Tools are auto-discovered at
        startup.
      </p>
    </div>
  );
}

function CliApiContent() {
  return (
    <div className="space-y-4 text-sm text-muted-foreground">
      <SectionHeading>CLI Batch Mode</SectionHeading>
      <p>
        Run GIMP operations headlessly via{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          gimp-console-3.exe
        </code>{" "}
        without opening the GUI:
      </p>
      <CodeBlock
        code={`# Call any PDB procedure from the command line
just pdb "gimp-version"

# List all registered MCP tools
just tools

# Test CLI batch mode (requires standalone GIMP 3.2.4)
just test-cli

# Test PDB proxy end-to-end
just test-pdb`}
      />

      <SectionHeading>REST API Endpoints</SectionHeading>
      <p>
        The backend (port 10773) exposes these REST endpoints via FastMCP's HTTP
        transport:
      </p>
      <div className="space-y-2 mt-2">
        {[
          {
            method: "GET",
            path: "/api/health",
            desc: "Health check — status, version, SOTA features",
          },
          {
            method: "GET",
            path: "/api/status",
            desc: "System status (alias for health)",
          },
          { method: "GET", path: "/api/sota", desc: "SOTA feature manifest" },
          { method: "GET", path: "/api/skills", desc: "List available skills" },
          {
            method: "GET",
            path: "/api/skills/{name}",
            desc: "Get skill content by name",
          },
          {
            method: "GET",
            path: "/api/tools",
            desc: "List registered MCP tools",
          },
        ].map((ep) => (
          <div
            key={ep.path}
            className="flex items-start gap-3 bg-secondary/20 rounded-lg px-4 py-2.5 border border-border/20"
          >
            <span className="text-[11px] font-mono font-bold text-green-400 bg-green-400/10 px-2 py-0.5 rounded shrink-0">
              {ep.method}
            </span>
            <div className="min-w-0">
              <span className="text-xs font-mono text-foreground">
                {ep.path}
              </span>
              <p className="text-xs text-muted-foreground mt-0.5">{ep.desc}</p>
            </div>
          </div>
        ))}
      </div>

      <SectionHeading>Justfile Recipes</SectionHeading>
      <p>
        The project includes a comprehensive{" "}
        <code className="text-xs bg-secondary px-1.5 py-0.5 rounded font-mono">
          justfile
        </code>{" "}
        for all common operations:
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
        {[
          ["start", "Start everything (backend + frontend + bridge)"],
          ["start-gimp", "Start with GIMP restart"],
          ["serve", "Backend only (uvicorn, reload)"],
          ["webapp", "Frontend only (Vite dev)"],
          ["build", "Build frontend for production"],
          ["bridge-status", "Check if bridge is active"],
          ["bridge-install", "Install bridge plugin to GIMP"],
          ["pdb", 'Call any PDB procedure: just pdb "gimp-version"'],
          ["tools", "List all registered MCP tools"],
          ["test", "Run all tests"],
          ["test-cov", "Run tests with coverage"],
          ["lint", "Lint Python (ruff) + frontend (biome)"],
          ["fix", "Auto-fix lint issues"],
          ["kill", "Kill all gimp-mcp processes"],
          ["clean", "Clean temp files and caches"],
        ].map(([recipe, desc]) => (
          <div
            key={recipe}
            className="flex items-start gap-2 bg-secondary/20 rounded-lg px-3 py-2 border border-border/20"
          >
            <span className="text-[11px] font-mono text-primary bg-primary/10 px-1.5 py-0.5 rounded shrink-0 mt-0.5">
              {recipe}
            </span>
            <span className="text-xs">{desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
