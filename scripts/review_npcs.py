from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from npc_chaos_app.engine import MODES, generate_npc
from npc_chaos_app.storage import load_state


CHAOS_LEVELS = [18, 35, 55, 72, 90]


def main() -> None:
    parser = argparse.ArgumentParser(description="Review NPC Chaos Box output variety.")
    parser.add_argument("--count", type=int, default=50)
    args = parser.parse_args()

    state = load_state()
    scenes = []
    modes = MODES[1:]
    for index in range(args.count):
        scenes.append(
            generate_npc(
                state,
                {
                    "seed": 1000 + index * 37,
                    "mode": modes[index % len(modes)],
                    "chaos": CHAOS_LEVELS[index % len(CHAOS_LEVELS)],
                },
            )
        )

    print(f"Reviewed {len(scenes)} deterministic NPCs")
    print()
    _print_counter("Modes", (scene["mode"] for scene in scenes))
    _print_counter("Danger", (scene["npc"]["danger"].split(":", 1)[0] for scene in scenes))
    _print_counter("Roles", (scene["npc"]["role"] for scene in scenes))
    _print_counter("Quotes", (scene["npc"]["quote"] for scene in scenes))
    _print_counter("Problems", (scene["npc"]["problem_now"] for scene in scenes))

    missing = []
    for scene in scenes:
        npc = scene["npc"]
        for key in ["first_move", "what_they_know", "wants_from_players", "use_in_play"]:
            if not str(npc.get(key) or "").strip():
                missing.append((scene["seed"], key))
    print()
    print(f"Missing practical fields: {len(missing)}")
    if missing:
        for seed, key in missing[:10]:
            print(f"- seed {seed}: {key}")


def _print_counter(label: str, values) -> None:
    counter = Counter(values)
    print(label)
    for value, count in counter.most_common(8):
        print(f"- {count:>2} {value}")
    print()


if __name__ == "__main__":
    main()
