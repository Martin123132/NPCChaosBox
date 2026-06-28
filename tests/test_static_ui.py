from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StaticUiTests(unittest.TestCase):
    def test_release_docs_include_first_run_acceptance(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        checklist = (ROOT / "docs" / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
        tester_script = (ROOT / "docs" / "TESTER_SCRIPT.md").read_text(encoding="utf-8")

        self.assertIn("first_run_acceptance.py", readme)
        self.assertIn("first_run_acceptance.py", checklist)
        self.assertIn("Maintainer Shortcut", tester_script)
        self.assertIn("plain-English local health", readme)

    def test_launcher_copy_stays_phone_call_simple(self) -> None:
        launcher = (ROOT / "START_NPCChaos_WINDOWS.bat").read_text(encoding="utf-8")

        self.assertIn("Python 3.10 or newer", launcher)
        self.assertIn("Add python.exe to PATH", launcher)
        self.assertIn("Temp folder:", launcher)
        self.assertIn("Press Generate NPC when it opens.", launcher)

    def test_tune_page_has_self_teaching_controls(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="tunePresets"', html)
        self.assertIn('id="tunePreview"', html)
        self.assertIn("What This Will Do", html)
        self.assertIn("TUNE_PRESETS", js)
        self.assertIn("renderTunePreview", js)
        self.assertIn(".preset-grid", css)
        self.assertIn(".tune-preview", css)

    def test_favourites_page_has_save_loop_guidance(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="favouritesSummary"', html)
        self.assertIn('id="favouritesGuide"', html)
        self.assertIn("Save Loop", html)
        self.assertIn("renderFavouritesStatus", js)
        self.assertIn("saveFromFavouritesButton", js)
        self.assertIn(".favourites-layout", css)
        self.assertIn(".favourite-card", css)
        self.assertIn("favourite-card-preview", js)
        self.assertIn("favourite-card-meta", js)
        self.assertIn("load-favourite-button", js)
        self.assertIn(".favourite-card-main", css)
        self.assertIn(".favourite-card-preview", css)

    def test_exports_page_has_guided_export_loop(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="exportsGuide"', html)
        self.assertIn('id="lastExportPath"', html)
        self.assertIn('id="exportFormatGuide"', html)
        self.assertIn("Table Notes", html)
        self.assertIn("Clean Card", html)
        self.assertIn("Export Loop", html)
        self.assertIn("renderExportsGuide", js)
        self.assertIn("TXT for table notes", js)
        self.assertIn("Last file:", js)
        self.assertIn(".exports-layout", css)
        self.assertIn(".export-option-grid", css)
        self.assertIn(".export-option-card", css)
        self.assertIn(".export-folder-card", css)

    def test_doctor_page_has_plain_english_health_summary(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="doctorPanel"', html)
        self.assertIn("find local files", html)
        self.assertIn("NPC Chaos Box is ready", js)
        self.assertIn("Quick Check", js)
        self.assertIn("Local Files", js)
        self.assertIn("Seed Counts", js)
        self.assertIn("seedCountSummary", js)
        self.assertIn(".doctor-status-card", css)
        self.assertIn(".doctor-grid", css)
        self.assertIn(".doctor-count-pill", css)

    def test_seed_page_has_guided_edit_loop(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="seedGuide"', html)
        self.assertIn('id="seedActionMessage"', html)
        self.assertIn('id="seedEditorCoach"', html)
        self.assertIn('id="seedLineTarget"', html)
        self.assertIn("Healthy Target", html)
        self.assertIn("Seed Pack Loop", html)
        self.assertIn("renderSeedGuide", js)
        self.assertIn("seedSample", js)
        self.assertIn("Unsaved seed edits", js)
        self.assertIn(".seed-editor-coach", css)
        self.assertIn(".seed-coach-card", css)
        self.assertIn(".seeds-layout", css)
        self.assertIn(".maintenance-card", css)
        self.assertIn(".seed-reset-card", css)

    def test_generate_card_has_scan_first_character_sheet(self) -> None:
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn("npc-sheet", js)
        self.assertIn("Use Now", js)
        self.assertIn("Read Aloud", js)
        self.assertIn("trace-details", js)
        self.assertIn("npcSpotlight", js)
        self.assertIn(".npc-table-callout", css)
        self.assertIn(".npc-priority-grid", css)
        self.assertIn(".trace-details", css)

    def test_generate_page_has_quiet_repeat_seed_control(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="repeatSeedPanel" hidden', html)
        self.assertIn("Repeat Seed", html)
        self.assertIn("repeatSeedPanel", js)
        self.assertIn("Seed repeated.", js)
        self.assertIn(".repeat-seed-panel", css)
        self.assertIn(".quiet-action", css)

    def test_generate_next_move_uses_flow_coach(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn("Next Move", html)
        self.assertIn("scene-window", html)
        self.assertIn("coachCard", js)
        self.assertIn("coachOption", js)
        self.assertIn("Use this NPC", js)
        self.assertIn("Tune if nearly right", js)
        self.assertIn("npc-chaos-table-mural-v2.png", css)
        self.assertIn(".scene-window", css)
        self.assertIn(".coach-card", css)
        self.assertIn(".coach-option-grid", css)

    def test_generate_result_actions_are_grouped(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn("result-action-head", html)
        self.assertIn("result-action-buttons", html)
        self.assertIn("Card Actions", html)
        self.assertIn(".result-action-head", css)
        self.assertIn(".result-action-buttons", css)
        self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr))", css)

    def test_mobile_shell_uses_compact_navigation(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('aria-label="Generate"', html)
        self.assertIn("Make one now", html)
        self.assertIn("Set the feel", html)
        self.assertIn("Bring back keepers", html)
        self.assertIn(".nav-copy", css)
        self.assertIn(".nav-hint", css)
        self.assertIn(".nav-list::-webkit-scrollbar", css)
        self.assertIn("overflow-x: auto", css)
        self.assertIn("white-space: nowrap", css)
        self.assertIn(".sidebar-foot", css)
        self.assertIn("display: none", css)


if __name__ == "__main__":
    unittest.main()
