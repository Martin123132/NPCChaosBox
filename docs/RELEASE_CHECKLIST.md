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
5. Export TXT.
6. Export HTML.
7. Open Exports.
8. Open Seed Packs and check traffic lights.
9. Open Doctor and confirm the data folder is on D.

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
