from __future__ import annotations

import unittest

from npc_chaos_app.engine import generate_npc
from npc_chaos_app.storage import load_default_state


class EngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = load_default_state()

    def test_same_seed_is_deterministic(self) -> None:
        options = {"seed": 12345, "mode": "Fantasy Tavern", "chaos": 60}
        self.assertEqual(generate_npc(self.state, options), generate_npc(self.state, options))

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
        ]:
            self.assertTrue(npc[key])
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
                self.assertIn("First Move:", text)
                self.assertIn("What They Know:", text)
                self.assertIn("Wants From Players:", text)
                self.assertNotIn("TODO", text)
                self.assertNotIn("placeholder", text.lower())


if __name__ == "__main__":
    unittest.main()
