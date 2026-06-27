param(
  [string]$Version = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Get-AppVersion {
  $initPath = Join-Path $repoRoot "npc_chaos_app\__init__.py"
  $initText = Get-Content -Raw -LiteralPath $initPath
  $match = [regex]::Match($initText, '__version__\s*=\s*"([^"]+)"')
  if (-not $match.Success) {
    throw "Could not read NPC Chaos Box version from $initPath"
  }
  return "v$($match.Groups[1].Value)"
}

if (-not $Version) {
  $Version = Get-AppVersion
}

$dist = Join-Path $repoRoot "dist"
$packageName = "NPCChaosBox-$Version"
$stage = Join-Path $dist $packageName
$zipPath = Join-Path $dist "$packageName.zip"

New-Item -ItemType Directory -Force -Path $dist | Out-Null

function Remove-If-In-Dist($PathToRemove) {
  if (-not (Test-Path -LiteralPath $PathToRemove)) {
    return
  }
  $distResolved = (Resolve-Path -LiteralPath $dist).Path
  $targetResolved = (Resolve-Path -LiteralPath $PathToRemove).Path
  if (-not $targetResolved.StartsWith($distResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to remove path outside dist: $targetResolved"
  }
  Remove-Item -LiteralPath $targetResolved -Recurse -Force
}

Remove-If-In-Dist $stage
if (Test-Path -LiteralPath $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

New-Item -ItemType Directory -Force -Path $stage | Out-Null

function Should-Include($File) {
  if ($File -in @(".gitignore", "README.md", "START_NPCChaos_WINDOWS.bat", "pyproject.toml")) {
    return $true
  }
  if ($File -eq ".github/workflows/tests.yml") {
    return $true
  }
  if ($File -like "npc_chaos_app/*") {
    return $true
  }
  if ($File -like "scripts/*" -or $File -like "tests/*" -or $File -like "docs/*") {
    return $true
  }
  return $false
}

$files = git -C $repoRoot ls-files --cached --others --exclude-standard | Where-Object { Should-Include $_ }
foreach ($file in $files) {
  $source = Join-Path $repoRoot $file
  $target = Join-Path $stage $file
  $targetDir = Split-Path -Parent $target
  New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
  Copy-Item -LiteralPath $source -Destination $target -Force
}

Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zipPath -Force

$size = [math]::Round((Get-Item -LiteralPath $zipPath).Length / 1KB, 1)
Write-Host "Created $zipPath ($size KB)"
