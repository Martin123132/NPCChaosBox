from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest
from urllib import request


class AppSmokeTests(unittest.TestCase):
    def test_first_run_acceptance_script_walks_happy_path(self) -> None:
        temp_parent = "D:\\Temp" if Path("D:\\Temp").exists() else None
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=temp_parent) as tmp:
            env = os.environ.copy()
            env["TEMP"] = tmp
            env["TMP"] = tmp
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/first_run_acceptance.py",
                    "--data-dir",
                    tmp,
                    "--temp-dir",
                    tmp,
                    "--timeout",
                    "8",
                ],
                cwd=repo,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=35,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("PASS: first-run happy path is working.", result.stdout)
            exports = list(Path(tmp, "exports").glob("*"))
            self.assertTrue(any(path.suffix == ".txt" for path in exports), result.stdout)
            self.assertTrue(any(path.suffix == ".html" for path in exports), result.stdout)

    def test_server_doctor_generate_and_open_exports(self) -> None:
        temp_parent = "D:\\Temp" if Path("D:\\Temp").exists() else None
        with tempfile.TemporaryDirectory(dir=temp_parent) as tmp:
            env = os.environ.copy()
            env["NPC_CHAOS_HOME"] = tmp
            env["NPC_CHAOS_DISABLE_OPEN"] = "1"
            proc = subprocess.Popen(
                [sys.executable, "-m", "npc_chaos_app.app", "--no-open", "--port", "0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
            )
            try:
                url = self._read_url(proc)
                doctor = self._json(url + "/api/doctor")
                self.assertTrue(doctor["ok"])
                self.assertTrue(doctor["doctor"]["state_ok"])
                tmp_path = Path(tmp).resolve()
                self.assertTrue(Path(doctor["doctor"]["data_dir"]).resolve().is_relative_to(tmp_path))

                started = time.perf_counter()
                generated = self._post_json(
                    url + "/api/generate",
                    {"seed": 9090, "mode": "Fantasy Tavern", "chaos": 70},
                )
                self.assertLess(time.perf_counter() - started, 2)
                self.assertTrue(generated["ok"])
                self.assertIn("npc", generated["scene"])
                self.assertEqual(len(generated["scene"]["trace"]), 7)

                opened = self._post_json(url + "/api/open-exports", {})
                self.assertTrue(opened["ok"])
                self.assertFalse(opened["export_folder"]["opened"])
                self.assertTrue(Path(opened["export_folder"]["path"]).resolve().is_relative_to(tmp_path))
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                if proc.stdout:
                    proc.stdout.close()

    def _read_url(self, proc: subprocess.Popen[str]) -> str:
        assert proc.stdout is not None
        deadline = time.time() + 8
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            match = re.search(r"http://127\.0\.0\.1:\d+", line)
            if match:
                return match.group(0)
        self.fail("Server did not print a local URL")

    def _json(self, url: str) -> dict:
        with request.urlopen(url, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post_json(self, url: str, payload: dict) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers={"content-type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
