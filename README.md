# NPC Chaos Box

NPC Chaos Box is a local-first deterministic NPC generator for tabletop games,
writing, solo RPGs, and worldbuilding. It uses seed banks, prime traces, drift,
and collision rules to make immediately usable characters without API keys,
cloud accounts, Ollama, npm, or a build step.

The design principle is simple: every page should teach the next useful action.
The app uses traffic-light status:

- Green: ready.
- Amber: usable, but worth improving.
- Red: blocked or too thin.

The game-scene background is original generated art made for this project. It
is there to make the tool feel like an NPC box for games, without using anyone
else's characters, logos, or settings.

## Start On Windows

1. Unzip the folder somewhere easy, preferably on the D drive.
2. Double-click `START_NPCChaos_WINDOWS.bat`.
3. Your browser opens.
4. Press `Generate NPC`.

The launcher stores data beside the app by default:

```text
user-data\
temp\
```

If Python is missing, install Python 3.10 or newer from:

```text
https://www.python.org/downloads/windows/
```

Tick `Add python.exe to PATH`, then double-click the launcher again.

## Pages

- `Generate`: pull one NPC card, then copy, save, or move to export.
- `Tune`: pick a feel preset, then adjust mode, role, chaos, and seed lock.
- `Seed Packs`: edit names, roles, places, wants, secrets, hooks, knowledge, offers, quotes, and rules.
- `Favourites`: save the current NPC and reload useful ones.
- `Exports`: choose TXT/HTML for the current NPC and find saved files.
- `Doctor`: check storage paths and seed-pack health.

## D-Drive Development Setup

Use these environment variables before local checks:

```powershell
New-Item -ItemType Directory -Force -Path D:\Temp, D:\NPCChaosData, D:\NPCChaosVerifyWork | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:NPC_CHAOS_HOME = "D:\NPCChaosData"
$env:NPC_CHAOS_DISABLE_OPEN = "1"
```

## Manual Start

```powershell
python -m npc_chaos_app.app
```

The app opens at a local address such as:

```text
http://127.0.0.1:53842
```

Close the terminal window, or press `Ctrl+C`, to stop it.

If a test run or agent leaves a local app process open, stop only NPC Chaos Box
dev processes with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\stop_dev.ps1
```

## Health Check

```powershell
python -m npc_chaos_app.app --doctor
```

## Development Checks

```powershell
python -m unittest discover -s tests
python -m compileall npc_chaos_app tests scripts
python scripts\sample_npcs.py --count 5
python scripts\review_npcs.py --count 50
```

Curated reproducible examples can be regenerated with:

```powershell
python scripts\sample_npcs.py --count 10 --output-dir docs\demo-npcs
```

## Release ZIP

Maintainers can build and verify a local ZIP with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\make_release_zip.ps1
$zip = (Get-ChildItem dist\NPCChaosBox-v*.zip | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
powershell -ExecutionPolicy Bypass -File scripts\verify_release_zip.ps1 -ZipPath $zip -WorkRoot D:\NPCChaosVerifyWork
```

## V0.1 Promise

NPC Chaos Box should be explainable over the phone: unzip, double-click,
generate, save/export. It should stay useful before it gets clever.
