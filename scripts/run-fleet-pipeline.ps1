# Fleet texture pipeline: blender-mcp -> gimp-mcp -> unity3d-mcp
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,
    [string]$TexturePath = "",
    [string]$BlenderUrl = "http://127.0.0.1:10849",
    [string]$UnityUrl = "http://127.0.0.1:10831",
    [string]$StagingDir = "D:/Temp/fleet_pipeline/gimp_staging",
    [switch]$SkipBlender,
    [switch]$SkipValidate,
    [switch]$SkipReview,
    [switch]$SkipUnity,
    [string]$BlenderOperation = "screenshot_viewport",
    [int]$BlenderAngles = 4,
    [string]$TextureType = "diffuse",
    [string]$TargetPlatform = "unity",
    [int]$NormalizeSize = 1024
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$argsList = @(
    "run", "python", "scripts/fleet_pipeline.py",
    "--project-path", $ProjectPath,
    "--blender-url", $BlenderUrl,
    "--unity-url", $UnityUrl,
    "--staging-dir", $StagingDir,
    "--blender-operation", $BlenderOperation,
    "--blender-angles", $BlenderAngles,
    "--texture-type", $TextureType,
    "--target-platform", $TargetPlatform,
    "--normalize-size", $NormalizeSize
)

if ($TexturePath) { $argsList += @("--texture-path", $TexturePath) }
if ($SkipBlender) { $argsList += "--skip-blender" }
if ($SkipValidate) { $argsList += "--skip-validate" }
if ($SkipReview) { $argsList += "--skip-review" }
if ($SkipUnity) { $argsList += "--skip-unity" }

uv @argsList
