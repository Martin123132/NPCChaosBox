# NPC Chaos Box Release Checklist

Use this before publishing a public ZIP.

## D-Safe Setup

```powershell
New-Item -ItemType Directory -Force -Path D:\Temp, D:\NPCChaosData, D:\NPCChaosVerifyWork | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:NPC_CHAOS_HOME = "D:\NPCChaosData"
$env:NPC_CHAOS_DISABLE_OPEN = "1"
```

## Local Checks

```powershell
python -m unittest discover -s tests
python -m compileall npc_chaos_app tests scripts
python scripts\first_run_acceptance.py --data-dir D:\NPCChaosAcceptanceData --temp-dir D:\Temp
python scripts\sample_npcs.py --count 5
python scripts\review_npcs.py --count 50
python -m npc_chaos_app.app --doctor
```

## Manual Smoke

```powershell
python -m npc_chaos_app.app --no-open --port 0
```

In the browser:

1. Generate an NPC.
2. Open Tune and change chaos.
3. Regenerate the same seed.
4. Save a favourite.
5. Open Exports.
6. Export TXT.
7. Export HTML.
8. Open Seed Packs and confirm categories are grouped.
9. Check traffic lights.
10. Confirm the game-scene background is visible but panels remain readable.
11. Open Doctor and confirm the data folder is on D.
12. Open Help and confirm known limitations are plain English.
13. Press Copy Debug Report and confirm it contains version, storage paths, seed counts, and current browser details.
14. Confirm the GitHub Issues button points at the public issue chooser.

## Public Alpha Feedback Setup

Check the repo contains these issue forms before publishing:

- `.github\ISSUE_TEMPLATE\app-would-not-open.yml`
- `.github\ISSUE_TEMPLATE\export-save-problem.yml`
- `.github\ISSUE_TEMPLATE\generated-npc-felt-wrong.yml`
- `.github\ISSUE_TEMPLATE\feature-idea.yml`

The release copy should be honest:

- Windows-first public alpha.
- Python 3.10 or newer required.
- No accounts, API keys, cloud calls, Ollama, npm, or installer.
- Feedback goes through GitHub Issues.

## Cleanup

Run this before handing the stage back:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\stop_dev.ps1
```

Then confirm no `python -m npc_chaos_app.app` process is still running.

## Release ZIP

```powershell
powershell -ExecutionPolicy Bypass -File scripts\make_release_zip.ps1
$zip = (Get-ChildItem dist\NPCChaosBox-v*.zip | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
powershell -ExecutionPolicy Bypass -File scripts\verify_release_zip.ps1 -ZipPath $zip -WorkRoot D:\NPCChaosVerifyWork
```

Check the ZIP contains:

- `START_NPCChaos_WINDOWS.bat`
- `README.md`
- `npc_chaos_app\`
- `npc_chaos_app\static\art\npc-chaos-table-mural-v2.png`
- `scripts\`
- `docs\`
- `tests\`

Check the ZIP does not contain:

- `.git\`
- `__pycache__\`
- `.pytest_cache\`
- `user-data\`
- `temp\`
- D-drive maintainer data such as `D:\NPCChaosData`
