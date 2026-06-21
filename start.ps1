Param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser,
    [switch]$RestartGimp
)

# --- SOTA Headless Standard 2026 ---
if ($Headless -and ($Host.Name -ne 'ConsoleHost' -or -not (Get-Variable -Name "NoRelaunch" -ErrorAction SilentlyContinue))) {
    $argList = @("-File", $PSCommandPath, "-NoRelaunch")
    if ($BackendOnly) { $argList += "-BackendOnly" }
    $argList += "-NoBrowser"
    Start-Process pwsh.exe -ArgumentList $argList -WindowStyle Hidden
    exit
}

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot

Write-Host "=== gimp-mcp Industrial Startup (v4.1.0) ===" -ForegroundColor Cyan

# 1. Kill stale ports
$WebPort = 10772
$BackendPort = 10773
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

$BridgePort = 10824
$ports = @($WebPort, $BackendPort, $BridgePort)

function Clear-Port {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if (-not $conns) { return $true }
    $pids = $conns | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
    if (-not $pids) { return $true }
    foreach ($pidKill in $pids) {
        Write-Host "  Port $Port occupied by PID $pidKill - attempting kill..." -ForegroundColor Yellow
        try {
            $proc = Get-Process -Id $pidKill -ErrorAction Stop
            $proc.Kill()
            $proc.WaitForExit(2000)
            Write-Host "    Killed PID $pidKill" -ForegroundColor DarkGreen
        } catch {
            try { Stop-Process -Id $pidKill -Force -ErrorAction Stop; Write-Host "    Killed PID $pidKill (force)" -ForegroundColor DarkGreen } catch {
                Write-Host "    Trying taskkill for PID $pidKill ..." -ForegroundColor DarkYellow
                $null = taskkill /F /PID $pidKill 2> $null
                Start-Sleep -Seconds 1
                $still = Get-Process -Id $pidKill -ErrorAction SilentlyContinue
                if ($still) {
                    Write-Host "    taskkill failed, trying WMI Terminate for PID $pidKill ..." -ForegroundColor DarkYellow
                    try { $null = Get-CimInstance Win32_Process -Filter "ProcessId = $pidKill" | Invoke-CimMethod -MethodName Terminate } catch {}
                    Start-Sleep -Seconds 1
                    $still = Get-Process -Id $pidKill -ErrorAction SilentlyContinue
                    if ($still) {
                        $owner = (Get-CimInstance Win32_Process -Filter "ProcessId = $pidKill" -ErrorAction SilentlyContinue).GetOwner().User
                        Write-Host "    FAILED to kill PID $pidKill (user: $owner) - open Task Manager as Admin" -ForegroundColor Red
                        Write-Host "    Or run: wmic process where ProcessId=$pidKill delete" -ForegroundColor Gray
                        return $false
                    } else {
                        Write-Host "    Killed PID $pidKill via WMI Terminate" -ForegroundColor DarkGreen
                    }
                } else {
                    Write-Host "    Killed PID $pidKill via taskkill" -ForegroundColor DarkGreen
                }
            }
        }
    }
    Start-Sleep -Seconds 1
    $remain = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
    if ($remain) {
        $remainingPid = ($remain | Select-Object -First 1).OwningProcess
        Write-Host "  Port $Port STILL occupied by PID $remainingPid after kill attempts" -ForegroundColor Red
        return $false
    }
    return $true
}

Write-Host "[0/3] Clearing ports..." -ForegroundColor Yellow
$allClear = $true
foreach ($p in @($WebPort, $BackendPort)) {
    if (-not (Clear-Port -Port $p)) { $allClear = $false }
}
Clear-Port -Port $BridgePort | Out-Null
if (-not $allClear) {
    Write-Host "`nSQUATTER DIAGNOSTIC:" -ForegroundColor Red
    foreach ($p in @($WebPort, $BackendPort)) {
        $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
        if ($conns) {
            foreach ($c in $conns) {
                $targetPid = $c.OwningProcess
                $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
                Write-Host "  Port $p : PID $targetPid $($proc.ProcessName) (started $($proc.StartTime))" -ForegroundColor Red
                try { $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $targetPid" -ErrorAction Stop).CommandLine; if ($cmd) { Write-Host "    Command: $cmd" -ForegroundColor Gray } } catch {}
            }
        }
    }
    Write-Host "Close these processes manually and retry." -ForegroundColor Red
    exit 1
}
Clear-Port -Port $BridgePort | Out-Null
Write-Host "  [ok] Ports are free" -ForegroundColor DarkGreen

# 1b. Auto-install GIMP MCP Bridge Plugin
Write-Host "[0.5/3] Installing GIMP MCP Bridge plugin..." -ForegroundColor Yellow
$gimpPluginDir = $null
$gimpProc = Get-Process -Name "gimp-3" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($gimpProc) {
    $localAppData = [Environment]::GetFolderPath("LocalApplicationData")
    $pkgBase = Join-Path $localAppData "Packages"
    $gimpPkg = Get-ChildItem "$pkgbase\GIMP*" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "GIMP.43237*" } | Select-Object -First 1
    if ($gimpPkg) {
        $gimpPluginDir = Join-Path $gimpPkg.FullName "LocalCache\Roaming\GIMP\3.2\plug-ins"
    }
} else {
    $gimpPluginDir = "$env:APPDATA\GIMP\3.0\plug-ins"
    if (-not (Test-Path $gimpPluginDir)) { $gimpPluginDir = "$env:APPDATA\GIMP\3.2\plug-ins" }
}
if ($gimpPluginDir) {
    if (-not (Test-Path $gimpPluginDir)) { New-Item -ItemType Directory -Path $gimpPluginDir -Force | Out-Null }
    Copy-Item (Join-Path $RepoRoot "src\gimp_mcp\plugins\gimp_mcp_bridge\gimp_mcp_bridge.py") (Join-Path $gimpPluginDir "gimp_mcp_bridge.py") -Force
    Write-Host "  [ok] Bridge plugin installed" -ForegroundColor DarkGreen
} else {
    Write-Host "  GIMP not running - plugin dir unknown. Bridge unavailable." -ForegroundColor Yellow
}

# 1c. Try to start the GIMP bridge
$bridgeListening = Get-NetTCPConnection -LocalPort $BridgePort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
if (-not $bridgeListening) {
    $gimpProc = Get-Process -Name "gimp-3" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($gimpProc) {
        if ($RestartGimp) {
            Write-Host "  --restart-gimp: Killing old GIMP (PID $($gimpProc.Id))..." -ForegroundColor Cyan
            try { Stop-Process -Id $gimpProc.Id -Force } catch { taskkill /F /PID $gimpProc.Id 2> $null }
            Start-Sleep -Seconds 3
            Write-Host "  Launching GIMP with bridge..." -ForegroundColor Cyan
            $gimpExe = "$env:LOCALAPPDATA\Programs\GIMP 3\bin\gimp-3.exe"
            Start-Process -FilePath $gimpExe
            for ($i = 0; $i -lt 30; $i++) {
                Start-Sleep -Seconds 2
                $bp = Get-NetTCPConnection -LocalPort $BridgePort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
                if ($bp) { Write-Host "  [ok] GIMP bridge active on port $BridgePort" -ForegroundColor DarkGreen; break }
            }
            if (-not $bp) {
                Write-Host "  Bridge not detected after 60s. Start manually via GIMP menu." -ForegroundColor Yellow
            }
        } else {
            Write-Host "  GIMP is running (PID $($gimpProc.Id)) but bridge is inactive on port $BridgePort" -ForegroundColor DarkYellow
            Write-Host "  Use --restart-gimp to auto-start the bridge." -ForegroundColor DarkGray
        }
    }
} else {
    Write-Host "  [ok] GIMP bridge active on port $BridgePort" -ForegroundColor DarkGreen
}

# 2. Python deps
if ($env:SKIP_SYNC -eq "1") {
    Write-Host "[1/3] Skipping Python deps (SKIP_SYNC=1)" -ForegroundColor DarkGray
} else {
    Write-Host "[1/3] Syncing Python deps (uv sync) ..." -ForegroundColor Cyan
    Set-Location $RepoRoot
    uv sync
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

# 3. Start Backend
Write-Host "[2/3] Starting Backend (port $BackendPort) ..." -ForegroundColor Cyan
$backendProc = Start-Process uv -ArgumentList "run", "uvicorn", "gimp_mcp.http_app:app", "--host", "127.0.0.1", "--port", "$BackendPort" `
    -WorkingDirectory $RepoRoot -PassThru -NoNewWindow
Write-Host "  [ok] Backend PID: $($backendProc.Id)" -ForegroundColor DarkGreen

if ($BackendOnly) {
    Write-Host "Backend-only mode active. Press Ctrl+C to exit." -ForegroundColor Yellow
    Wait-Process -Id $backendProc.Id
    exit
}

# Wait for backend readiness
Write-Host "  Waiting for backend..." -ForegroundColor DarkGray
$backendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $backendReady = $true; break
    } catch { Start-Sleep -Seconds 1 }
}
if (-not $backendReady) {
    Write-Host "  Backend not ready after 30s. Frontend may fail." -ForegroundColor Yellow
}

# 4. Start Frontend
Write-Host "[3/3] Starting Frontend (port $WebPort) ..." -ForegroundColor Cyan
$frontendDir = Join-Path $RepoRoot "webapp\frontend"
if (-not (Test-Path $frontendDir)) { $frontendDir = Join-Path $RepoRoot "webapp" }
if (-not (Test-Path $frontendDir)) { Write-Host "  Frontend directory not found!" -ForegroundColor Red; exit 1 }
Set-Location $frontendDir
if (-not (Test-Path "node_modules")) { npm install }
Start-Process npm -ArgumentList "run", "dev", "--", "--port", "$WebPort" -WorkingDirectory $frontendDir

Write-Host "Startup Complete." -ForegroundColor Green
if (-not $NoBrowser) {
    Write-Host "  Waiting for frontend..." -ForegroundColor DarkGray
    $frontendReady = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $null = Invoke-WebRequest -Uri "http://127.0.0.1:${WebPort}/" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            $frontendReady = $true; break
        } catch { Start-Sleep -Seconds 1 }
    }
    if ($frontendReady) {
        Start-Process "http://localhost:$WebPort"
        Write-Host "  Browser launched." -ForegroundColor Green
    } else {
        Write-Host "  Frontend not ready after 30s. Open http://localhost:$WebPort manually." -ForegroundColor Yellow
    }
}

# Keep alive
try {
    while ($true) {
        Start-Sleep -Seconds 5
        if ($backendProc.HasExited) { Write-Host "Backend exited!" -ForegroundColor Red; break }
    }
} finally {
    if ($backendProc -and -not $backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    }
}
