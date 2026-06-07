Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Webapp Start - Standardized SOTA (v4.0.1)
$WebPort = 10772
$BackendPort = 10773
$BridgePort = 10824
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 1. Aggressive port clearing with fallback
Write-Host "=== gimp-mcp Webapp Startup ===" -ForegroundColor Cyan
Write-Host "Clearing ports $WebPort, $BackendPort, $BridgePort..." -ForegroundColor Yellow

function Clear-Port {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if (-not $conns) { return $true }
    $pids = $conns | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
    if (-not $pids) { return $true }
    foreach ($pidKill in $pids) {
        Write-Host "  Port $Port occupied by PID $pidKill - killing..." -ForegroundColor Yellow
        try {
            $proc = Get-Process -Id $pidKill -ErrorAction Stop
            $proc.Kill()
            $proc.WaitForExit(2000)
        } catch {
            try { Stop-Process -Id $pidKill -Force -ErrorAction Stop } catch {
                $null = taskkill /F /PID $pidKill 2>$null
                Start-Sleep -Seconds 1
            }
        }
    }
    Start-Sleep -Seconds 1
    $remain = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
    if ($remain) {
        Write-Host "  Port $Port STILL occupied after kill attempts - aborting" -ForegroundColor Red
        return $false
    }
    return $true
}

$allClear = $true
foreach ($p in @($WebPort, $BackendPort, $BridgePort)) {
    if (-not (Clear-Port -Port $p)) { $allClear = $false }
}
if (-not $allClear) {
    Write-Host "Cannot proceed - close the processes manually and retry." -ForegroundColor Red
    exit 1
}
Write-Host "  [ok] Ports are free" -ForegroundColor DarkGreen

# 2. Setup
$FrontendDir = Join-Path $PSScriptRoot "frontend"
Set-Location $FrontendDir
if (-not (Test-Path "node_modules")) { npm install }

# 3. Start Python backend
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$PSScriptRoot'; uv run --project '$ProjectRoot' uvicorn gimp_mcp.http_app:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# Wait for backend to be reachable before opening browser
Write-Host "  Waiting for backend (up to 30s)..." -ForegroundColor DarkGray
$backendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $backendReady = $true
        break
    } catch { Start-Sleep -Seconds 1 }
}
if (-not $backendReady) {
    Write-Host "  Warning: Backend not ready after 30s. Frontend may fail." -ForegroundColor Yellow
}

# 4. Launch Vite frontend
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green

# Browser opener - polls until frontend responds
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollScript = 'for ($i = 0; $i -lt 60; $i++) { try { $r = Invoke-WebRequest -Uri ' + "'$frontendUrl'" + ' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; if ($r.Content -match "GIMP MCP") { Start-Process ' + "'$frontendUrl'" + '; break } } catch {}; Start-Sleep -Seconds 1 }'
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollScript

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
Set-Location $FrontendDir
npm run dev -- --port $WebPort --host
