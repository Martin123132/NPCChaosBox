# NPC Chaos Box Tester Script

This is the phone-call test. A non-technical tester should be able to generate
and export an NPC without opening a command prompt.

## What To Say

1. Download or unzip NPC Chaos Box somewhere easy.
2. Open the folder.
3. Double-click `START_NPCChaos_WINDOWS.bat`.
4. When the browser opens, press `Generate NPC`.
5. Copy or save the NPC.
6. Open `Exports`.
7. Export TXT.

## What To Watch For

- Time to first NPC.
- Did Python block them?
- Did Windows show a warning?
- Did the browser open by itself?
- Did the traffic lights make the next step obvious?
- Did separate pages make the app calmer?
- Did the Generate page feel focused rather than crowded?
- Could they understand that file formats live on the Exports page?
- Was the NPC useful at a table or in a story?

## Pass Standard

The tester should generate, save, and export an NPC in under 10 minutes with
plain-English guidance only.

## Maintainer Shortcut

Before handing a build to a human tester, run:

```powershell
python scripts\first_run_acceptance.py --data-dir D:\NPCChaosAcceptanceData --temp-dir D:\Temp
```

This does not replace the phone-call test, but it proves the local happy path is alive first.
