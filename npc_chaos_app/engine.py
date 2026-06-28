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
DRIFT_BEATS = {
    "preserve": "the plain truth is awkward enough.",
    "tilt": "the truth tilts toward whoever applies pressure first.",
    "fragment": "half the truth helps and half of it is bait.",
    "invert": "the safest answer is probably backwards.",
    "amplify": "one small lie has already become local policy.",
    "misremember": "the NPC's memory changes under pressure.",
    "bind": "a promise makes the truth expensive.",
}


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

    danger = _danger_level(chaos, trace[-1])
    twist = _twist(mode, chaos, drift, faction, obj, rng)
    problem_now = _problem_with_stakes(problem, danger, mode)
    first_move = _first_move(mode, hook, obj, faction, rng)
    what_they_know = _knowledge_line(knowledge, drift, chaos)
    wants_from_players = _player_request(problem, offer, complication, chaos)
    use_in_play = _use_in_play(use_case, hook, twist)
    table_cues = _table_cues(problem_now, first_move, what_they_know, wants_from_players, use_in_play)
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
        "problem_now": problem_now,
        "object": obj,
        "first_move": first_move,
        "what_they_know": what_they_know,
        "wants_from_players": wants_from_players,
        "quote": quote,
        "use_in_play": use_in_play,
        "table_cues": table_cues,
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
    cues = _normalized_table_cues(npc)
    lines = [
        str(scene.get("title") or npc.get("name") or "NPC"),
        "",
        "RUN THIS SCENE",
        f"Use Now: {cues['use_now']}",
        f"Open With: {cues['open_with']}",
        f"If Ignored: {cues['if_ignored']}",
        f"Ask: {cues['ask']}",
        f"Reward: {cues['reward']}",
        f"Catch: {cues['catch']}",
        f"Read Aloud: \"{npc.get('quote', '')}\"",
        "",
        "EXTRA DETAIL",
        f"Role: {npc.get('role', '')}",
        f"Home: {npc.get('home', '')}",
        f"Faction: {npc.get('faction', '')}",
        f"Wants: {npc.get('wants', '')}",
        f"Secret: {npc.get('secret', '')}",
        f"Contradiction: {npc.get('contradiction', '')}",
        f"Problem Now: {npc.get('problem_now', '')}",
        f"Object: {npc.get('object', '')}",
        f"Clue: {cues['clue']}",
        f"Reveal Trigger: {cues['reveal_trigger']}",
        f"Push: {cues['push']}",
        f"Danger: {npc.get('danger', '')}",
        "",
        f"Seed: {scene.get('seed')} | Mode: {scene.get('mode')} | Chaos: {scene.get('chaos')}",
        "",
        "CHAOS TRACE",
    ]
    lines.extend(str(line) for line in scene.get("trace_lines") or [])
    return "\n".join(lines).strip() + "\n"


def npc_to_html(scene: dict[str, Any]) -> str:
    npc = scene.get("npc") or {}
    cues = _normalized_table_cues(npc)
    title = html.escape(str(scene.get("title") or "NPC Chaos Box Export"))
    trace_lines = scene.get("trace_lines") or []
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
      body {{ background: #f7f8f5; color: #18201f; font-family: Arial, sans-serif; margin: 0; padding: 2rem; }}
      main {{ background: #fff; border: 1px solid #d9e0dc; border-radius: 8px; margin: 0 auto; max-width: 880px; padding: 1.5rem; }}
      h1 {{ font-size: 1.8rem; margin: 0 0 0.35rem; }}
      h2 {{ font-size: 0.95rem; letter-spacing: 0; margin: 1.25rem 0 0.65rem; text-transform: uppercase; }}
      p {{ line-height: 1.5; margin: 0.35rem 0; }}
      .meta {{ color: #64716d; }}
      .run-grid, .detail-grid {{ display: grid; gap: 0.65rem; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .cue {{ background: #fbfcfa; border: 1px solid #d9e0dc; border-radius: 8px; padding: 0.75rem; }}
      .cue strong {{ display: block; font-size: 0.75rem; margin-bottom: 0.25rem; text-transform: uppercase; }}
      blockquote {{ background: #17211f; border-radius: 8px; color: #f7fbf9; margin: 1rem 0; padding: 1rem; }}
      ol {{ color: #64716d; line-height: 1.5; }}
      @media (max-width: 680px) {{ body {{ padding: 1rem; }} .run-grid, .detail-grid {{ grid-template-columns: 1fr; }} }}
    </style>
  </head>
  <body>
    <main>
      <h1>{title}</h1>
      <p class="meta">{html.escape(str(npc.get('role', '')))} from {html.escape(str(npc.get('home', '')))}.</p>
      <h2>Run This Scene</h2>
      <p><strong>Use Now:</strong> {html.escape(cues['use_now'])}</p>
      <div class="run-grid">
        {_html_cue("Open With", cues["open_with"])}
        {_html_cue("If Ignored", cues["if_ignored"])}
        {_html_cue("Ask", cues["ask"])}
        {_html_cue("Reward", cues["reward"])}
        {_html_cue("Catch", cues["catch"])}
      </div>
      <blockquote>{html.escape(str(npc.get('quote', '')))}</blockquote>
      <h2>Extra Detail</h2>
      <div class="detail-grid">
        {_html_cue("Clue", cues["clue"])}
        {_html_cue("Reveal Trigger", cues["reveal_trigger"])}
        {_html_cue("Wants", str(npc.get("wants", "")))}
        {_html_cue("Contradiction", str(npc.get("contradiction", "")))}
        {_html_cue("Secret", str(npc.get("secret", "")))}
        {_html_cue("Object", str(npc.get("object", "")))}
        {_html_cue("Faction", str(npc.get("faction", "")))}
        {_html_cue("Danger", str(npc.get("danger", "")))}
      </div>
      <h2>Chaos Trace</h2>
      <ol>{"".join(f"<li>{html.escape(str(line))}</li>" for line in trace_lines)}</ol>
    </main>
  </body>
</html>
"""


def _html_cue(label: str, value: str) -> str:
    return f"""<div class="cue"><strong>{html.escape(label)}</strong><p>{html.escape(value)}</p></div>"""


def _table_cues(
    problem_now: str,
    first_move: str,
    what_they_know: str,
    wants_from_players: str,
    use_in_play: str,
) -> dict[str, str]:
    return {
        "use_now": _use_now_cue(use_in_play),
        "open_with": _extract_after(first_move, "Open with:"),
        "if_ignored": _extract_after(problem_now, "If ignored:"),
        "ask": _ask_cue(wants_from_players),
        "reward": _extract_between(wants_from_players, "In return:", ". Catch:"),
        "catch": _extract_after(wants_from_players, "Catch:"),
        "clue": _extract_between(what_they_know, "", ". Reveal trigger:"),
        "reveal_trigger": _extract_after(what_they_know, "Reveal trigger:"),
        "push": _extract_after(use_in_play, "Push:"),
    }


def _normalized_table_cues(npc: dict[str, Any]) -> dict[str, str]:
    cues = npc.get("table_cues") if isinstance(npc.get("table_cues"), dict) else {}
    fallback = _table_cues(
        str(npc.get("problem_now", "")),
        str(npc.get("first_move", "")),
        str(npc.get("what_they_know", "")),
        str(npc.get("wants_from_players", "")),
        str(npc.get("use_in_play", "")),
    )
    return {
        key: str(cues.get(key) or fallback.get(key) or "").strip()
        for key in [
            "use_now",
            "open_with",
            "if_ignored",
            "ask",
            "reward",
            "catch",
            "clue",
            "reveal_trigger",
            "push",
        ]
    }


def _use_now_cue(value: str) -> str:
    if ". Scene:" in value:
        value = value.split(". Scene:", 1)[0]
    if value.startswith("Use when "):
        value = value.removeprefix("Use when ")
    return _strip_period(value)


def _ask_cue(value: str) -> str:
    ask = _extract_between(value, "", ". In return:")
    for prefix in [
        "They ask the players to deal with this quietly:",
        "They ask the players to deal with this:",
    ]:
        if ask.startswith(prefix):
            return ask.removeprefix(prefix).strip()
    return ask


def _extract_between(value: str, start: str, end: str) -> str:
    text = str(value).strip()
    if start:
        if start not in text:
            return _strip_period(text)
        text = text.split(start, 1)[1].strip()
    if end and end in text:
        text = text.split(end, 1)[0].strip()
    return _strip_period(text)


def _extract_after(value: str, marker: str) -> str:
    text = str(value).strip()
    if marker and marker in text:
        text = text.split(marker, 1)[1].strip()
    return _strip_period(text)


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
        return f"{line} High chaos: {DRIFT_BEATS.get(drift, 'the truth bends under pressure')}"
    if chaos <= 25:
        return f"{line} Low chaos: keep the problem grounded and let one odd detail carry it."
    return line


def _first_move(mode: str, hook: str, obj: str, faction: str, rng: random.Random) -> str:
    mode_moves = {
        "Fantasy Tavern": [
            f"put {obj} on the nearest dry table where everyone can see it.",
            f"let the room notice that {faction} is listening.",
        ],
        "Village Weird": [
            "ask everyone nearby to vote before the bells notice.",
            f"unwrap {obj} from a parish notice and ask who recognises it.",
        ],
        "Quest Giver Gone Wrong": [
            "start with the apology instead of the quest.",
            "admit the reward has developed opinions.",
        ],
        "Villain Contact": [
            "name the villain only after checking the windows.",
            f"offer a meeting that {faction} will deny arranging.",
        ],
        "Shopkeeper With A Problem": [
            "lock the shop door from the outside.",
            f"price {obj} as if it might bite.",
        ],
    }
    next_beat = rng.choice(mode_moves.get(mode, ["make the room choose a side."]))
    return f"Open with: {_strip_period(hook)}. Then {next_beat}"


def _problem_with_stakes(problem: str, danger: str, mode: str) -> str:
    mode_stakes = {
        "Fantasy Tavern": "the room chooses sides before anyone can leave",
        "Village Weird": "the village turns it into a rule",
        "Quest Giver Gone Wrong": "the job becomes harder and less honest",
        "Villain Contact": "the villain learns the players are interested",
        "Shopkeeper With A Problem": "the price goes up and the shop shuts",
    }
    if danger.startswith("Red"):
        stake = "it spills into the next scene before the players get a clean rest"
    elif danger.startswith("Green"):
        stake = "it stays local for now, but costs someone pride, coin, or leverage"
    else:
        stake = mode_stakes.get(mode, "someone else takes control of the situation")
    return f"{_strip_period(problem)}. If ignored: {stake}."


def _knowledge_line(knowledge: str, drift: str, chaos: int) -> str:
    clue = _drift_text(knowledge, drift, max(chaos - 20, 0))
    if chaos >= 75:
        trigger = "the players accept a messy favour or apply public pressure"
    elif chaos <= 25:
        trigger = "the players ask directly and keep the scene calm"
    else:
        trigger = "the players help with the immediate problem first"
    return f"{_strip_period(clue)}. Reveal trigger: {trigger}."


def _player_request(problem: str, offer: str, complication: str, chaos: int) -> str:
    urgency = ""
    if chaos >= 75:
        urgency = " before the next bell, closing time, or villain move"
    if chaos <= 25:
        return (
            f"They ask the players to deal with this quietly: {_strip_period(problem)}. "
            f"In return: {_strip_period(offer)}. Catch: nobody can make this louder."
        )
    return (
        f"They ask the players to deal with this: {_strip_period(problem)}{urgency}. "
        f"In return: {_strip_period(offer)}. Catch: {_strip_period(complication)}."
    )


def _use_in_play(use_case: str, hook: str, twist: str) -> str:
    return f"Use when {use_case}. Scene: {_strip_period(hook)}. Push: {twist}"


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


def _strip_period(value: str) -> str:
    return str(value).strip().rstrip(".")


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
