param(
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$launcherPath = Join-Path $repoRoot "START_NPCChaos_WINDOWS.bat"
$launcherPattern = [regex]::Escape($launcherPath)

function Is-NpcChaosProcess($Process) {
  if (-not $Process.CommandLine) {
    return $false
  }
  if ($Process.ProcessId -eq $PID) {
    return $false
  }
  return (
    $Process.CommandLine -match "npc_chaos_app\.app" -or
    $Process.CommandLine -match $launcherPattern
  )
}

$matches = @(Get-CimInstance Win32_Process | Where-Object { Is-NpcChaosProcess $_ })
$stopped = 0

foreach ($process in $matches) {
  $label = "$($process.Name) PID $($process.ProcessId)"
  if ($DryRun) {
    Write-Host "Would stop $label"
    continue
  }

  try {
    Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
    Write-Host "Stopped $label"
    $stopped += 1
  } catch {
    Write-Host "Could not stop $label`: $($_.Exception.Message)"
  }
}

$pidFiles = @()
$pidFiles += @(Get-ChildItem -Path (Join-Path $repoRoot "temp") -Filter "npc-chaos-*-server.pid" -ErrorAction SilentlyContinue)
$pidFiles += @(Get-ChildItem -Path "D:\Temp" -Filter "npc-chaos-*-server.pid" -ErrorAction SilentlyContinue)

foreach ($pidFile in $pidFiles) {
  $pidText = Get-Content -LiteralPath $pidFile.FullName -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $pidText) {
    continue
  }
  $pidValue = 0
  if (-not [int]::TryParse($pidText, [ref]$pidValue)) {
    continue
  }
  $process = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
  if (-not $process) {
    Write-Host "Stale PID file: $($pidFile.FullName)"
  }
}

if ($DryRun) {
  Write-Host "NPC Chaos Box cleanup dry run complete. Matching process count: $($matches.Count)"
} else {
  Write-Host "NPC Chaos Box cleanup complete. Stopped $stopped process(es)."
}
