# Demo NPCs

These NPCs are generated from fixed seeds so output quality can be checked
repeatably before release.

Regenerate from the repo root:

```powershell
New-Item -ItemType Directory -Force -Path D:\Temp, D:\NPCChaosQualityData | Out-Null
$env:TEMP = "D:\Temp"
$env:TMP = "D:\Temp"
$env:NPC_CHAOS_HOME = "D:\NPCChaosQualityData"
python scripts\sample_npcs.py --count 10 --output-dir docs\demo-npcs
```

