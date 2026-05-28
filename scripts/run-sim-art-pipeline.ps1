# Sim-art pipeline: Gazebo icons, atlases, VRChat handoff
param(
    [Parameter(Mandatory = $true)]
    [string]$InputDir,
    [string]$StagingDir = "D:/Temp/fleet_pipeline/sim_art",
    [ValidateSet("gazebo", "vrchat")]
    [string]$Pipeline = "gazebo",
    [string]$TemplateId = "gazebo_icon_256",
    [string]$Layout = "4x4",
    [int]$CellSize = 256,
    [switch]$SkipAtlas,
    [switch]$SkipRobotics,
    [switch]$SkipAvatar,
    [switch]$NoValidate,
    [string]$RoboticsUrl = "http://127.0.0.1:10892",
    [string]$AvatarUrl = "http://127.0.0.1:10793",
    [string]$ModelsRoot = "",
    [string]$ModelId = "",
    [string]$VrmPath = "",
    [switch]$AutoImport
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$argsList = @(
    "run", "python", "scripts/sim_art_pipeline.py",
    "--input-dir", $InputDir,
    "--staging-dir", $StagingDir,
    "--pipeline", $Pipeline,
    "--template-id", $TemplateId,
    "--layout", $Layout,
    "--cell-size", $CellSize,
    "--robotics-url", $RoboticsUrl,
    "--avatar-url", $AvatarUrl
)

if ($SkipAtlas) { $argsList += "--skip-atlas" }
if ($SkipRobotics) { $argsList += "--skip-robotics" }
if ($SkipAvatar) { $argsList += "--skip-avatar" }
if ($NoValidate) { $argsList += "--no-validate" }
if ($ModelsRoot) { $argsList += @("--models-root", $ModelsRoot) }
if ($ModelId) { $argsList += @("--model-id", $ModelId) }
if ($VrmPath) { $argsList += @("--vrm-path", $VrmPath) }
if ($AutoImport) { $argsList += "--auto-import" }

uv @argsList
