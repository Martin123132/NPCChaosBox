from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib import request


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the local first-run acceptance path: doctor, generate, favourite, export, folder check."
    )
    parser.add_argument("--data-dir", default="", help="Runtime data folder. Prefer a D-drive path on Windows.")
    parser.add_argument("--temp-dir", default="", help="Temp folder for the launched app. Prefer D:\\Temp on Windows.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Seconds to wait for server readiness.")
    parser.add_argument("--max-generate-seconds", type=float, default=2.0)
    parser.add_argument("--seed", type=int, default=9090)
    parser.add_argument("--mode", default="Fantasy Tavern")
    parser.add_argument("--chaos", type=int, default=70)
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else _default_data_dir()
    temp_dir = Path(args.temp_dir).expanduser() if args.temp_dir else _default_temp_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["NPC_CHAOS_HOME"] = str(data_dir)
    env["NPC_CHAOS_DISABLE_OPEN"] = "1"
    env["TEMP"] = str(temp_dir)
    env["TMP"] = str(temp_dir)

    print("NPC Chaos Box first-run acceptance")
    print(f"Data: {data_dir}")
    print(f"Temp: {temp_dir}")

    proc = subprocess.Popen(
        [sys.executable, "-m", "npc_chaos_app.app", "--no-open", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    try:
        _wait_for_server(url, args.timeout, proc)

        doctor = _get_json(f"{url}/api/doctor")
        _require(doctor.get("ok"), "Doctor endpoint did not return ok.")
        doctor_data = doctor.get("doctor") or {}
        _require(doctor_data.get("state_ok"), "Seed pack is not ready.")
        _require(_inside(Path(str(doctor_data.get("data_dir"))), data_dir), "Doctor data path is outside data dir.")
        print(f"Doctor: ready, Python {doctor.get('python')}, app {doctor.get('version')}")

        start = time.perf_counter()
        generated = _post_json(
            f"{url}/api/generate",
            {"seed": args.seed, "mode": args.mode, "chaos": args.chaos},
        )
        elapsed = time.perf_counter() - start
        _require(elapsed <= args.max_generate_seconds, f"Generate took {elapsed:.2f}s.")
        _require(generated.get("ok"), "Generate endpoint did not return ok.")
        scene = generated.get("scene") or {}
        _require(scene.get("npc"), "Generated scene did not include an NPC.")
        _require(len(scene.get("trace") or []) == 7, "Generated trace did not include seven steps.")
        print(f"Generate: {scene.get('title')} in {elapsed:.2f}s")

        favourite = _post_json(f"{url}/api/favourites", {"scene": scene})
        _require(favourite.get("ok"), "Favourite save did not return ok.")
        favourite_id = ((favourite.get("favourite") or {}).get("id")) or ""
        _require(favourite_id, "Favourite response did not include an id.")
        favourites = _get_json(f"{url}/api/favourites")
        favourite_ids = [item.get("id") for item in favourites.get("favourites", [])]
        _require(favourite_id in favourite_ids, "Saved favourite was not listed.")
        print(f"Favourite: saved {favourite_id}")

        for export_format in ("txt", "html"):
            exported = _post_json(f"{url}/api/export", {"scene": scene, "format": export_format})
            _require(exported.get("ok"), f"{export_format.upper()} export did not return ok.")
            export_data = exported.get("export") or {}
            path = Path(str(export_data.get("path") or ""))
            _require(path.exists(), f"{export_format.upper()} export file was not created.")
            _require(_inside(path, data_dir), f"{export_format.upper()} export is outside data dir.")
            print(f"Export {export_format.upper()}: {path}")

        folder = _post_json(f"{url}/api/open-exports", {})
        _require(folder.get("ok"), "Open exports endpoint did not return ok.")
        folder_data = folder.get("export_folder") or {}
        _require(folder_data.get("opened") is False, "Folder opening should be disabled during acceptance.")
        _require(_inside(Path(str(folder_data.get("path"))), data_dir), "Exports folder is outside data dir.")
        print(f"Folder: checked without opening Explorer at {folder_data.get('path')}")

        print("PASS: first-run happy path is working.")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        _print_server_output(proc)
        return 1
    finally:
        _stop_process(proc)


def _default_data_dir() -> Path:
    if os.name == "nt" and Path("D:\\").exists():
        return Path("D:\\NPCChaosAcceptanceData")
    return ROOT / "acceptance-data"


def _default_temp_dir() -> Path:
    if os.name == "nt" and Path("D:\\").exists():
        return Path("D:\\Temp")
    return _default_data_dir() / "temp"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(url: str, timeout: float, proc: subprocess.Popen[str]) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Server exited early with code {proc.returncode}.")
        try:
            _get_json(f"{url}/api/doctor", timeout=1.0)
            return
        except Exception as exc:  # noqa: BLE001 - this is a readiness poll.
            last_error = exc
            time.sleep(0.15)
    raise RuntimeError(f"Server did not become ready at {url}: {last_error}")


def _get_json(url: str, timeout: float = 5.0) -> dict:
    with request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(url: str, payload: dict, timeout: float = 5.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"content-type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _inside(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def _require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _print_server_output(proc: subprocess.Popen[str]) -> None:
    if not proc.stdout or proc.poll() is None:
        return
    try:
        output = proc.stdout.read()
    except OSError:
        output = ""
    if output.strip():
        print("Server output:", file=sys.stderr)
        print(output, file=sys.stderr)


def _stop_process(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    if proc.stdout:
        proc.stdout.close()


if __name__ == "__main__":
    raise SystemExit(main())
