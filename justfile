set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

gimp_bin := "C:\\Users\\sandr\\AppData\\Local\\Programs\\GIMP 3\\bin\\gimp-console-3.exe"

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [SOTA] GIMP MCP Industrial Operations v4.1.0' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# ── ([^─]+) ─') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^─].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [System State: PROD/GIMP 3.2]" -ForegroundColor DarkGray; \
    Write-Host ''

# ── Startup ───────────────────────────────────────────────────────────────────

# Start everything: backend + frontend + bridge
start:
    Set-Location '{{justfile_directory()}}'
    .\start.ps1

# Start with GIMP restart (kills old GIMP, launches fresh with bridge)
start-gimp:
    Set-Location '{{justfile_directory()}}'
    .\start.ps1 -RestartGimp

# Start backend only (uvicorn)
serve:
    Set-Location '{{justfile_directory()}}'
    uv run uvicorn gimp_mcp.http_app:app --host 127.0.0.1 --port 10773 --reload

# Start webapp frontend only (Vite dev)
webapp:
    Set-Location '{{justfile_directory()}}\webapp\frontend'
    npm run dev -- --port 10772 --host

# Build frontend for production
build:
    Set-Location '{{justfile_directory()}}\webapp\frontend'
    npm run build

# ── Bridge ────────────────────────────────────────────────────────────────────

# Check if GIMP bridge is active on port 10775
bridge-status:
    $p = Get-NetTCPConnection -LocalPort 10775 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }; \
    if ($p) { Write-Host "Bridge active on port 10775 (PID $($p.OwningProcess))" -ForegroundColor Green } \
    else { Write-Host "Bridge inactive" -ForegroundColor Red }

# Install bridge plugin to GIMP plug-ins directory
bridge-install:
    foreach ($d in @("$env:APPDATA\GIMP\3.2\plug-ins\gimp_mcp_bridge", "$env:APPDATA\GIMP\3.0\plug-ins\gimp_mcp_bridge")) { \
        New-Item -ItemType Directory -Path $d -Force | Out-Null; \
        Copy-Item '{{justfile_directory()}}\src\gimp_mcp\plugins\gimp_mcp_bridge\gimp_mcp_bridge.py' "$d\" -Force; \
        '' | Set-Content "$d\__init__.py"; \
        Write-Host "Installed to $d" -ForegroundColor Green; \
    }

# ── PDB Proxy ─────────────────────────────────────────────────────────────────

# Call any GIMP PDB procedure. Usage: just pdb "gimp-version"
pdb procedure:
    @Set-Location '{{justfile_directory()}}'
    @$env:GIMP_BIN = '{{gimp_bin}}'
    @uv run python scripts/pdb_call.py {{procedure}}

# List all registered MCP tools
tools:
    @Set-Location '{{justfile_directory()}}'
    @uv run python scripts/list_tools.py

# ── Testing ───────────────────────────────────────────────────────────────────

# Run all tests
test:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
    Set-Location '{{justfile_directory()}}'
    uv run pytest tests/ --cov=gimp_mcp --cov-report=term-missing

# Test CLI batch mode (requires standalone GIMP 3.2.4)
test-cli:
    Set-Location '{{justfile_directory()}}'
    $env:GIMP_BIN = '{{gimp_bin}}'
    uv run python scripts/test_cli.py

# Test PDB proxy end-to-end
test-pdb:
    Set-Location '{{justfile_directory()}}'
    $env:GIMP_BIN = '{{gimp_bin}}'
    uv run python scripts/test_pdb.py

# ── Quality ───────────────────────────────────────────────────────────────────

# Lint Python (ruff) and frontend (biome)
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    Set-Location '{{justfile_directory()}}\webapp\frontend'
    npx @biomejs/biome ci .

# Auto-fix lint issues
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\webapp\frontend'
    npx @biomejs/biome check --write .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# ── Cleanup ───────────────────────────────────────────────────────────────────

# Kill all gimp-mcp processes (frontend, backend, bridge)
kill:
    foreach ($p in @(10772, 10773, 10775)) { \
        $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue; \
        foreach ($c in $conns) { \
            try { Stop-Process -Id $c.OwningProcess -Force } catch { taskkill /F /PID $c.OwningProcess 2>$null } \
        } \
    }; \
    Write-Host "Killed processes on ports 10772, 10773, 10775" -ForegroundColor Yellow

# Clean temp files, node_modules, caches
clean:
    Remove-Item -Recurse -Force '{{justfile_directory()}}\webapp\frontend\node_modules' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\webapp\frontend\dist' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\.venv' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\**\__pycache__' -ErrorAction SilentlyContinue
    uv cache clean
    Write-Host "Cleaned" -ForegroundColor Green

# Remove GIMP bridge plugin from user profile
clean-gimp:
    Remove-Item -Recurse -Force "$env:APPDATA\GIMP\3.0\plug-ins\gimp_mcp_bridge" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "$env:APPDATA\GIMP\3.2\plug-ins\gimp_mcp_bridge" -ErrorAction SilentlyContinue
    Write-Host "GIMP bridge plugin removed" -ForegroundColor Yellow
