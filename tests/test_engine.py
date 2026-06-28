from __future__ import annotations

import unittest

from npc_chaos_app.engine import generate_npc
from npc_chaos_app.storage import load_default_state


class EngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = load_default_state()

    def test_same_seed_is_deterministic(self) -> None:
        options = {"seed": 12345, "mode": "Fantasy Tavern", "chaos": 60}
        first = generate_npc(self.state, options)
        second = generate_npc(self.state, options)
        first.pop("created_at", None)
        second.pop("created_at", None)
        self.assertEqual(first, second)

    def test_different_seed_changes_output(self) -> None:
        first = generate_npc(self.state, {"seed": 111, "mode": "Village Weird"})
        second = generate_npc(self.state, {"seed": 222, "mode": "Village Weird"})
        self.assertNotEqual(first["title"], second["title"])

    def test_trace_has_seven_steps(self) -> None:
        scene = generate_npc(self.state, {"seed": 9})
        self.assertEqual(len(scene["trace"]), 7)

    def test_output_has_required_npc_fields(self) -> None:
        scene = generate_npc(self.state, {"seed": 5150, "mode": "Quest Giver Gone Wrong", "chaos": 80})
        npc = scene["npc"]
        for key in [
            "name",
            "role",
            "wants",
            "secret",
            "contradiction",
            "problem_now",
            "first_move",
            "what_they_know",
            "wants_from_players",
            "quote",
            "use_in_play",
            "table_cues",
        ]:
            self.assertTrue(npc[key])
        cues = npc["table_cues"]
        self.assertIn("If ignored:", npc["problem_now"])
        self.assertIn("Open with:", npc["first_move"])
        self.assertIn("Reveal trigger:", npc["what_they_know"])
        self.assertIn("In return:", npc["wants_from_players"])
        self.assertIn("Catch:", npc["wants_from_players"])
        self.assertIn("Scene:", npc["use_in_play"])
        self.assertIn("Push:", npc["use_in_play"])
        for key in ["use_now", "open_with", "if_ignored", "ask", "reward", "catch", "clue", "reveal_trigger", "push"]:
            self.assertTrue(cues[key])
        self.assertIn("CHAOS TRACE", scene["card_text"])

    def test_chaos_changes_intensity(self) -> None:
        low = generate_npc(self.state, {"seed": 777, "mode": "Villain Contact", "chaos": 10})
        high = generate_npc(self.state, {"seed": 777, "mode": "Villain Contact", "chaos": 95})
        self.assertNotEqual(low["npc"]["wants"], high["npc"]["wants"])
        self.assertNotEqual(low["guidance"], high["guidance"])

    def test_demo_style_seeds_include_practical_table_fields(self) -> None:
        options = [
            {"seed": 101, "mode": "Fantasy Tavern", "chaos": 55},
            {"seed": 404, "mode": "Villain Contact", "chaos": 80},
            {"seed": 1001, "mode": "Shopkeeper With A Problem", "chaos": 76},
        ]
        for option in options:
            scene = generate_npc(self.state, option)
            with self.subTest(seed=option["seed"]):
                text = scene["card_text"]
                self.assertLess(text.index("RUN THIS SCENE"), text.index("EXTRA DETAIL"))
                self.assertIn("Use Now:", text)
                self.assertIn("Open With:", text)
                self.assertIn("If Ignored:", text)
                self.assertIn("Ask:", text)
                self.assertIn("Reward:", text)
                self.assertIn("Catch:", text)
                self.assertIn("Clue:", text)
                self.assertIn("Reveal Trigger:", text)
                self.assertNotIn("TODO", text)
                self.assertNotIn("placeholder", text.lower())

    def test_demo_style_seeds_have_actionable_scene_cues(self) -> None:
        options = [
            {"seed": 101, "mode": "Fantasy Tavern", "chaos": 55},
            {"seed": 202, "mode": "Village Weird", "chaos": 72},
            {"seed": 303, "mode": "Quest Giver Gone Wrong", "chaos": 66},
            {"seed": 404, "mode": "Villain Contact", "chaos": 80},
            {"seed": 505, "mode": "Shopkeeper With A Problem", "chaos": 48},
            {"seed": 606, "mode": "Fantasy Tavern", "chaos": 25},
            {"seed": 707, "mode": "Village Weird", "chaos": 90},
            {"seed": 808, "mode": "Quest Giver Gone Wrong", "chaos": 42},
            {"seed": 909, "mode": "Villain Contact", "chaos": 58},
            {"seed": 1001, "mode": "Shopkeeper With A Problem", "chaos": 76},
        ]
        required_markers = {
            "problem_now": "If ignored:",
            "first_move": "Open with:",
            "what_they_know": "Reveal trigger:",
            "wants_from_players": "In return:",
            "use_in_play": "Scene:",
        }
        for option in options:
            scene = generate_npc(self.state, option)
            npc = scene["npc"]
            cues = npc["table_cues"]
            with self.subTest(seed=option["seed"]):
                for key, marker in required_markers.items():
                    self.assertIn(marker, npc[key])
                self.assertIn("Catch:", npc["wants_from_players"])
                self.assertIn("Push:", npc["use_in_play"])
                for key in ["use_now", "open_with", "if_ignored", "ask", "reward", "catch"]:
                    self.assertTrue(cues[key])
                    self.assertNotIn("Open with:", cues[key])
                    self.assertNotIn("If ignored:", cues[key])
                self.assertLessEqual(len(npc["first_move"]), 240)
                self.assertLessEqual(len(npc["use_in_play"]), 320)


if __name__ == "__main__":
    unittest.main()
