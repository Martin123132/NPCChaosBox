param(
  [string]$Version = "",
  [string]$OwnerRepo = "",
  [string]$ZipPath = "",
  [string]$WorkRoot = "",
  [switch]$SkipDoctor
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

if (-not $ZipPath -and -not $OwnerRepo) {
  throw "Pass -ZipPath for a local ZIP, or -OwnerRepo to download a published release."
}

$safeVersion = $Version -replace "[^a-zA-Z0-9._-]", "-"
if ($WorkRoot) {
  New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
  $tempBase = (Resolve-Path -LiteralPath $WorkRoot).Path
} else {
  $tempBase = [System.IO.Path]::GetTempPath()
}
$work = Join-Path $tempBase "NPCChaosVerify-$safeVersion-$([System.Guid]::NewGuid().ToString('N'))"
$downloadedZip = Join-Path $work "NPCChaosBox-$Version.zip"
$extractDir = Join-Path $work "unzipped"
$dataDir = Join-Path $work "data"

function Remove-TempWork {
  if (-not (Test-Path -LiteralPath $work)) {
    return
  }
  $baseResolved = (Resolve-Path -LiteralPath $tempBase).Path
  $workResolved = (Resolve-Path -LiteralPath $work).Path
  if (-not $workResolved.StartsWith($baseResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to remove path outside work root: $workResolved"
  }
  Remove-Item -LiteralPath $workResolved -Recurse -Force
}

try {
  New-Item -ItemType Directory -Force -Path $work, $extractDir, $dataDir | Out-Null

  if ($ZipPath) {
    $sourceZip = (Resolve-Path -LiteralPath $ZipPath).Path
    Copy-Item -LiteralPath $sourceZip -Destination $downloadedZip -Force
    Write-Host "Using local ZIP: $sourceZip"
  } else {
    $url = "https://github.com/$OwnerRepo/releases/download/$Version/NPCChaosBox-$Version.zip"
    Write-Host "Downloading $url"
    Invoke-WebRequest -Uri $url -OutFile $downloadedZip
  }

  Expand-Archive -LiteralPath $downloadedZip -DestinationPath $extractDir -Force

  $required = @(
    "START_NPCChaos_WINDOWS.bat",
    "README.md",
    "npc_chaos_app\app.py",
    "npc_chaos_app\seeds\crooked_lantern.json",
    "npc_chaos_app\templates\index.html"
  )
  foreach ($relative in $required) {
    $path = Join-Path $extractDir $relative
    if (-not (Test-Path -LiteralPath $path)) {
      throw "Missing required release file: $relative"
    }
  }

  $forbidden = Get-ChildItem -LiteralPath $extractDir -Force -Recurse |
    Where-Object { $_.Name -in @(".git", "__pycache__", ".pytest_cache", "user-data", "temp") }
  if ($forbidden) {
    throw "Release ZIP contains forbidden generated files: $($forbidden[0].FullName)"
  }

  if (-not $SkipDoctor) {
    Push-Location $extractDir
    try {
      $env:NPC_CHAOS_HOME = $dataDir
      $env:NPC_CHAOS_DISABLE_OPEN = "1"
      python -m npc_chaos_app.app --doctor | Out-Host
      if ($LASTEXITCODE -ne 0) {
        throw "Doctor command failed."
      }
    } finally {
      Pop-Location
      Remove-Item Env:\NPC_CHAOS_HOME -ErrorAction SilentlyContinue
      Remove-Item Env:\NPC_CHAOS_DISABLE_OPEN -ErrorAction SilentlyContinue
    }
  }

  Write-Host "Release ZIP verified for $Version"
} finally {
  Remove-TempWork
}

