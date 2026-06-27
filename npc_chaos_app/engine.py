from __future__ import annotations

import html
import random
import time
from typing import Any


MODES = [
    "Random",
    "Fantasy Tavern",
    "Village Weird",
    "Quest Giver Gone Wrong",
    "Villain Contact",
    "Shopkeeper With A Problem",
]

PRIMES = [17, 19, 23, 29, 31, 37, 41]
DRIFTS = ["preserve", "tilt", "fragment", "invert", "amplify", "misremember", "bind"]


def generate_npc(state: dict[str, Any], options: dict[str, Any] | None = None) -> dict[str, Any]:
    options = options or {}
    seed = _coerce_seed(options.get("seed"))
    rng = random.Random(seed)
    mode = str(options.get("mode") or "Random")
    if mode == "Random" or mode not in MODES:
        mode = rng.choice(MODES[1:])
    chaos = _clamp_int(options.get("chaos"), 0, 100, 55)
    role_filter = str(options.get("role") or "").strip()

    prime = rng.choice(PRIMES)
    trace_seed = rng.randrange(1, prime)
    trace = _prime_trace(trace_seed, prime, rng)
    drift = _choose_drift(trace, chaos)

    name = _pick(state, "names", rng, "Unnamed Local")
    epithet = _pick(state, "epithets", rng, "of the unfinished note")
    roles = _as_list(state.get("roles"), ["person with a problem"])
    role = role_filter if role_filter and role_filter != "Any Role" else rng.choice(roles)
    place = _pick(state, "places", rng, "somewhere awkward")
    faction = _pick(state, "factions", rng, "a committee with no minutes")
    want = _pick(state, "wants", rng, "to get through the day")
    secret = _pick(state, "secrets", rng, "they know more than they admit")
    contradiction = _pick(state, "contradictions", rng, "helpful but alarming")
    problem = _pick(state, "problems", rng, "someone has made this worse")
    obj = _pick(state, "objects", rng, "a suspicious object")
    quote = _pick(state, "quotes", rng, "I can explain, but not cheaply.")
    use_case = _pick(state, "use_cases", rng, "the scene needs a useful complication")
    hook = _pick(state, "hooks", rng, "they interrupt with a problem")
    knowledge = _pick(state, "knowledge", rng, "where the next useful clue is hidden")
    offer = _pick(state, "offers", rng, "help if the players take one small risk")
    complication = _pick(state, "complications", rng, "someone important is watching")
    chaos_rule = _pick(state, "chaos_rules", rng, "The trace makes the motive wobble.")

    twist = _twist(mode, chaos, drift, faction, obj, rng)
    first_move = _first_move(mode, hook, obj, faction, rng)
    danger = _danger_level(chaos, trace[-1])
    guidance = _guidance_for_npc(mode, chaos, danger)
    title = f"{name}, {epithet}"

    npc = {
        "name": name,
        "epithet": epithet,
        "role": role,
        "home": place,
        "faction": faction,
        "wants": _drift_text(want, drift, chaos),
        "secret": _drift_text(secret, drift, chaos),
        "contradiction": contradiction,
        "problem_now": problem,
        "object": obj,
        "first_move": first_move,
        "what_they_know": _drift_text(knowledge, drift, max(chaos - 20, 0)),
        "wants_from_players": _player_offer(offer, complication, chaos),
        "quote": quote,
        "use_in_play": f"Use them when {use_case}. {twist}",
        "danger": danger,
    }
    trace_lines = [
        f"Prime field Z{prime}, seed {trace_seed}, seven-step trace {trace}.",
        f"Drift: {drift}; chaos {chaos}; mode {mode}.",
        f"Rule: {chaos_rule}",
        f"Collision: {name} wants '{want}' but the scene pushes '{problem}'.",
    ]
    return {
        "title": title,
        "seed": seed,
        "mode": mode,
        "chaos": chaos,
        "role_filter": role_filter or "Any Role",
        "world_name": str(state.get("world_name") or "Untitled Seed Pack"),
        "npc": npc,
        "trace": trace,
        "trace_lines": trace_lines,
        "guidance": guidance,
        "card_text": npc_to_text({"title": title, "npc": npc, "trace_lines": trace_lines, "seed": seed, "mode": mode, "chaos": chaos}),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def npc_to_text(scene: dict[str, Any]) -> str:
    npc = scene.get("npc") or {}
    lines = [
        str(scene.get("title") or npc.get("name") or "NPC"),
        "",
        f"Role: {npc.get('role', '')}",
        f"Home: {npc.get('home', '')}",
        f"Faction: {npc.get('faction', '')}",
        f"Wants: {npc.get('wants', '')}",
        f"Secret: {npc.get('secret', '')}",
        f"Contradiction: {npc.get('contradiction', '')}",
        f"Problem Now: {npc.get('problem_now', '')}",
        f"Object: {npc.get('object', '')}",
        f"First Move: {npc.get('first_move', '')}",
        f"What They Know: {npc.get('what_they_know', '')}",
        f"Wants From Players: {npc.get('wants_from_players', '')}",
        f"Quote: \"{npc.get('quote', '')}\"",
        f"Use In Play: {npc.get('use_in_play', '')}",
        f"Danger: {npc.get('danger', '')}",
        "",
        f"Seed: {scene.get('seed')} | Mode: {scene.get('mode')} | Chaos: {scene.get('chaos')}",
        "",
        "CHAOS TRACE",
    ]
    lines.extend(str(line) for line in scene.get("trace_lines") or [])
    return "\n".join(lines).strip() + "\n"


def npc_to_html(scene: dict[str, Any]) -> str:
    text = html.escape(npc_to_text(scene))
    title = html.escape(str(scene.get("title") or "NPC Chaos Box Export"))
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 2rem; color: #18201f; }}
      pre {{ white-space: pre-wrap; line-height: 1.5; }}
    </style>
  </head>
  <body>
    <pre>{text}</pre>
  </body>
</html>
"""


def _prime_trace(seed: int, prime: int, rng: random.Random) -> list[int]:
    value = seed % prime
    factor = rng.randrange(2, prime - 1)
    offset = rng.randrange(1, prime)
    trace: list[int] = []
    for step in range(7):
        value = (value * factor + offset + step) % prime
        trace.append(value)
    return trace


def _choose_drift(trace: list[int], chaos: int) -> str:
    index = (sum(trace) + chaos // 12) % len(DRIFTS)
    return DRIFTS[index]


def _twist(mode: str, chaos: int, drift: str, faction: str, obj: str, rng: random.Random) -> str:
    mode_lines = {
        "Fantasy Tavern": [
            f"They are easiest to introduce when {obj} interrupts a normal drink.",
            f"Let the tavern room go quiet when {faction} is mentioned.",
        ],
        "Village Weird": [
            "Let one ordinary village rule suddenly matter far too much.",
            f"Make {faction} treat this like a civic emergency.",
        ],
        "Quest Giver Gone Wrong": [
            "They give a real quest, but the reason is badly bent.",
            "The reward is useful, embarrassing, or legally alive.",
        ],
        "Villain Contact": [
            "They are not the villain, which somehow makes them worse.",
            f"They can arrange a meeting, but {faction} will hear about it.",
        ],
        "Shopkeeper With A Problem": [
            f"They will sell {obj}, but only if the players fix the immediate mess.",
            "Every price includes one favour and one uncomfortable question.",
        ],
    }
    line = rng.choice(mode_lines.get(mode, ["They make a simple scene harder in a useful way."]))
    if chaos >= 75:
        return f"{line} High chaos: {drift} the truth until the table has to choose a side."
    if chaos <= 25:
        return f"{line} Low chaos: keep the problem grounded and let one odd detail carry it."
    return line


def _first_move(mode: str, hook: str, obj: str, faction: str, rng: random.Random) -> str:
    mode_moves = {
        "Fantasy Tavern": [
            f"{hook}, then put {obj} on the nearest dry table.",
            f"{hook}, while pretending {faction} is not listening.",
        ],
        "Village Weird": [
            f"{hook}, then ask everyone to vote before the bells notice.",
            f"{hook}, carrying {obj} wrapped in a parish notice.",
        ],
        "Quest Giver Gone Wrong": [
            f"{hook}, but start with the apology instead of the quest.",
            f"{hook}, then admit the reward has developed opinions.",
        ],
        "Villain Contact": [
            f"{hook}, then name the villain only after checking the windows.",
            f"{hook}, while offering a meeting that {faction} will deny arranging.",
        ],
        "Shopkeeper With A Problem": [
            f"{hook}, then lock the shop door from the outside.",
            f"{hook}, while pricing {obj} as if it might bite.",
        ],
    }
    return rng.choice(mode_moves.get(mode, [f"{hook}, then makes the room choose a side."]))


def _player_offer(offer: str, complication: str, chaos: int) -> str:
    if chaos >= 75:
        return f"{offer}, but {complication} before sunset."
    if chaos <= 25:
        return f"{offer}, as long as nobody makes this louder."
    return f"{offer}, though {complication}."


def _danger_level(chaos: int, last_trace: int) -> str:
    score = chaos + last_trace
    if score >= 105:
        return "Red: dangerous if ignored"
    if score >= 55:
        return "Amber: complicated but usable"
    return "Green: safe to introduce now"


def _guidance_for_npc(mode: str, chaos: int, danger: str) -> dict[str, str]:
    if danger.startswith("Red"):
        next_step = "Use this NPC as a pressure point, not background colour."
    elif chaos >= 70:
        next_step = "Drop them into a scene when you want the table to react fast."
    else:
        next_step = "Use them as a helpful contact with one strange complication."
    return {
        "status": danger.split(":", 1)[0].lower(),
        "next_step": next_step,
        "mode_tip": f"{mode} is tuned for immediate table use rather than long lore.",
    }


def _drift_text(value: str, drift: str, chaos: int) -> str:
    if chaos < 35 or drift == "preserve":
        return value
    if drift == "invert":
        return f"{value}, but for the opposite reason"
    if drift == "amplify":
        return f"{value}, and they have already gone too far"
    if drift == "fragment":
        return f"{value}, though they only admit half of it"
    if drift == "misremember":
        return f"{value}, except their version keeps changing"
    if drift == "bind":
        return f"{value}, tied to a promise they cannot break"
    return f"{value}, slightly wrong in a useful way"


def _pick(state: dict[str, Any], key: str, rng: random.Random, fallback: str) -> str:
    values = _as_list(state.get(key), [fallback])
    return rng.choice(values)


def _as_list(value: Any, fallback: list[str]) -> list[str]:
    if not isinstance(value, list):
        return fallback
    items = [str(item).strip() for item in value if str(item).strip()]
    return items or fallback


def _coerce_seed(value: Any) -> int:
    if value in (None, ""):
        return int(time.time() * 1000) % 1_000_000_000
    try:
        return int(str(value).strip())
    except ValueError:
        return abs(hash(str(value))) % 1_000_000_000


def _clamp_int(value: Any, low: int, high: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = default
    return max(low, min(high, number))
