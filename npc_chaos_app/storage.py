from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

from .engine import npc_to_html, npc_to_text


APP_NAME = "NPCChaosBox"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def app_data_dir() -> Path:
    override = os.getenv("NPC_CHAOS_HOME")
    root = Path(override).expanduser() if override else repo_root() / "user-data"
    root.mkdir(parents=True, exist_ok=True)
    return root


def exports_dir() -> Path:
    path = app_data_dir() / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_state_path() -> Path:
    return repo_root() / "npc_chaos_app" / "seeds" / "crooked_lantern.json"


def user_state_path() -> Path:
    return app_data_dir() / "seed_pack.json"


def favourites_path() -> Path:
    return app_data_dir() / "favourites.json"


def load_default_state() -> dict[str, Any]:
    return _read_json(default_state_path(), fallback={})


def load_state() -> dict[str, Any]:
    path = user_state_path()
    if not path.exists():
        state = load_default_state()
        save_state(state)
        return state
    state = _read_json(path, fallback=None)
    if not isinstance(state, dict) or not state.get("names"):
        broken = path.with_suffix(f".broken-{int(time.time())}.json")
        try:
            shutil.copy2(path, broken)
        except OSError:
            pass
        state = load_default_state()
        save_state(state)
    return normalize_state(state)


def save_state(state: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_state(state)
    _write_json(user_state_path(), normalized)
    return normalized


def reset_state() -> dict[str, Any]:
    state = load_default_state()
    save_state(state)
    return state


def list_favourites() -> list[dict[str, Any]]:
    data = _read_json(favourites_path(), fallback=[])
    return data if isinstance(data, list) else []


def save_favourite(scene: dict[str, Any]) -> dict[str, Any]:
    favourites = list_favourites()
    item = {
        "id": f"fav-{int(time.time() * 1000)}",
        "title": str(scene.get("title") or "Untitled NPC"),
        "seed": scene.get("seed"),
        "mode": scene.get("mode"),
        "created_at": scene.get("created_at") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scene": scene,
    }
    favourites.insert(0, item)
    _write_json(favourites_path(), favourites[:150])
    return item


def export_npc(scene: dict[str, Any], export_format: str = "txt") -> dict[str, Any]:
    export_format = "html" if str(export_format).lower() == "html" else "txt"
    title = str(scene.get("title") or "npc-chaos-card")
    stem = _slugify(title)[:70] or "npc-chaos-card"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = exports_dir() / f"{stamp}-{stem}.{export_format}"
    content = npc_to_html(scene) if export_format == "html" else npc_to_text(scene)
    path.write_text(content, encoding="utf-8")
    return {"path": str(path), "format": export_format, "title": title}


def open_exports_folder(opener: Any | None = None) -> dict[str, Any]:
    path = exports_dir().resolve()
    root = app_data_dir().resolve()
    if path != root and root not in path.parents:
        raise RuntimeError("Refusing to open a folder outside NPC Chaos Box data.")
    try:
        if os.getenv("NPC_CHAOS_DISABLE_OPEN") == "1":
            return {"opened": False, "path": str(path), "error": "Opening folders is disabled for this run."}
        if opener:
            opener(path)
        elif os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return {"opened": True, "path": str(path)}
    except (OSError, RuntimeError) as exc:
        return {"opened": False, "path": str(path), "error": str(exc)}


def doctor() -> dict[str, Any]:
    state = load_state()
    data_dir = app_data_dir()
    return {
        "data_dir": str(data_dir),
        "state_path": str(user_state_path()),
        "favourites_path": str(favourites_path()),
        "exports_dir": str(exports_dir()),
        "state_ok": bool(state.get("names") and state.get("roles")),
        "category_counts": category_counts(state),
        "favourite_count": len(list_favourites()),
        "portable_default": str((repo_root() / "user-data").resolve()),
    }


def category_counts(state: dict[str, Any]) -> dict[str, int]:
    keys = [
        "names",
        "roles",
        "places",
        "wants",
        "secrets",
        "contradictions",
        "problems",
        "hooks",
        "knowledge",
        "offers",
        "quotes",
    ]
    return {key: len(state.get(key) if isinstance(state.get(key), list) else []) for key in keys}


def normalize_state(state: dict[str, Any]) -> dict[str, Any]:
    default = load_default_state()
    normalized = dict(default)
    if isinstance(state, dict):
        normalized.update(state)
    for key in [
        "names",
        "epithets",
        "roles",
        "places",
        "factions",
        "wants",
        "secrets",
        "contradictions",
        "problems",
        "objects",
        "hooks",
        "knowledge",
        "offers",
        "complications",
        "quotes",
        "use_cases",
        "chaos_rules",
    ]:
        value = normalized.get(key)
        if not isinstance(value, list):
            normalized[key] = default.get(key, [])
        else:
            normalized[key] = [str(item).strip() for item in value if str(item).strip()]
    normalized["version"] = int(normalized.get("version") or 1)
    normalized["world_name"] = str(normalized.get("world_name") or "Untitled Seed Pack")
    normalized["world_note"] = str(normalized.get("world_note") or "")
    return normalized


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _slugify(value: str) -> str:
    value = value.lower()
    value = "".join(ch if ch.isalnum() else "-" for ch in value)
    while "--" in value:
        value = value.replace("--", "-")
    return value.strip("-")
