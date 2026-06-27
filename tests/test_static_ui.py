from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StaticUiTests(unittest.TestCase):
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

    def test_exports_page_has_guided_export_loop(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="exportsGuide"', html)
        self.assertIn('id="lastExportPath"', html)
        self.assertIn("Export Loop", html)
        self.assertIn("renderExportsGuide", js)
        self.assertIn("HTML is best for a clean saved card", js)
        self.assertIn(".exports-layout", css)
        self.assertIn(".export-folder-card", css)

    def test_seed_page_has_guided_edit_loop(self) -> None:
        html = (ROOT / "npc_chaos_app" / "templates" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "npc_chaos_app" / "static" / "app.js").read_text(encoding="utf-8")
        css = (ROOT / "npc_chaos_app" / "static" / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="seedGuide"', html)
        self.assertIn('id="seedActionMessage"', html)
        self.assertIn("Seed Pack Loop", html)
        self.assertIn("renderSeedGuide", js)
        self.assertIn("Unsaved seed edits", js)
        self.assertIn(".seeds-layout", css)
        self.assertIn(".maintenance-card", css)

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


if __name__ == "__main__":
    unittest.main()
