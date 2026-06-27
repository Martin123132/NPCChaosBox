from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from npc_chaos_app.engine import generate_npc, npc_to_text
from npc_chaos_app.storage import load_state


DEMO_OPTIONS = [
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic NPC Chaos Box samples.")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    state = load_state()
    output_dir = Path(args.output_dir) if args.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    for index in range(args.count):
        options = _options_for_index(index)
        scene = generate_npc(state, options)
        text = npc_to_text(scene)
        if output_dir:
            path = output_dir / f"{index + 1:02d}-{scene['mode'].lower().replace(' ', '-')}-{scene['seed']}.txt"
            path.write_text(text, encoding="utf-8")
        else:
            print("=" * 78)
            print(text)


def _options_for_index(index: int) -> dict:
    base = dict(DEMO_OPTIONS[index % len(DEMO_OPTIONS)])
    cycle = index // len(DEMO_OPTIONS)
    if cycle:
        base["seed"] = int(base["seed"]) + (cycle * 1009)
        base["chaos"] = max(0, min(100, int(base["chaos"]) + ((cycle * 11) % 31) - 15))
    return base


if __name__ == "__main__":
    main()
