# NPC Chaos Box Development Plan

## V0.1 Goal

Build a standalone Windows-first local app:

1. Double-click `START_NPCChaos_WINDOWS.bat`.
2. Browser opens.
3. Press `Generate NPC`.
4. Get a usable NPC in under 30 seconds.

## Product Shape

NPC Chaos Box is not a scene writer. It is a guided character workstation.

Core NPC card fields:

- name,
- role,
- home,
- faction,
- wants,
- secret,
- contradiction,
- immediate problem,
- object,
- quote,
- use in play,
- chaos trace.

## UI Rules

- Use separate pages for separate jobs.
- Do not cram every control onto the first page.
- Use traffic-light guidance for readiness and next steps.
- Mobile navigation should stay compact so the working page starts quickly.
- The Generate page is the first screen.
- The first Generate state should have one obvious main action; repeat-seed controls appear only after an NPC exists.
- Generated NPC cards should be scan-first: use-now guidance, read-aloud quote, immediate pressure, then supporting detail.
- Generate guidance should feel like a flow coach: one clear next move, then quieter optional paths.
- Post-generation actions should be grouped as a small action bar, not loose buttons.
- The Generate page should show only the current result actions, not every possible file-format choice.
- Advanced tuning lives on the Tune page, with quick feel presets and a live effect summary.
- TXT/HTML file choices live on the Exports page, with a clear export/open-folder loop.
- Export choices should explain their purpose in place, so the user is picking an outcome rather than a file extension.
- Favourites is a saved-NPC shelf with a clear save/load loop.
- Favourite cards should show one scannable preview, compact metadata, and one clear load action.
- Seed editing lives on the Seed Packs page, with category health, save feedback, and a reset action separated from the main edit loop.
- Seed editing should teach the format, healthy target, and current list preview beside the editor without adding extra action buttons.

## Storage Rules

- Default storage is `user-data` beside the app.
- Launcher also sets `TEMP` and `TMP` to `temp` beside the app.
- `NPC_CHAOS_HOME` can override storage, for example `D:\NPCChaosData`.
- Do not rely on `%LOCALAPPDATA%` for V0.1.

## Deferred

- More seed packs.
- PNG character cards.
- DOCX import.
- Local LLM embellishment.
- EXE packaging.
