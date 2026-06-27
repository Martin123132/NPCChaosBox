from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


class ReleaseScriptTests(unittest.TestCase):
    def test_verify_release_zip_accepts_valid_zip(self) -> None:
        if sys.platform != "win32":
            self.skipTest("PowerShell release verification is Windows-first.")

        temp_parent = "D:\\Temp" if Path("D:\\Temp").exists() else None
        with tempfile.TemporaryDirectory(dir=temp_parent) as tmp:
            root = Path(tmp)
            zip_path = root / "release.zip"
            with zipfile.ZipFile(zip_path, "w") as release:
                release.writestr("START_NPCChaos_WINDOWS.bat", "@echo off\n")
                release.writestr("README.md", "# NPC Chaos Box\n")
                release.writestr("npc_chaos_app/app.py", "print('doctor')\n")
                release.writestr("npc_chaos_app/seeds/crooked_lantern.json", "{}\n")
                release.writestr("npc_chaos_app/templates/index.html", "<!doctype html>\n")

            work_root = root / "verify-work"
            result = subprocess.run(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "scripts\\verify_release_zip.ps1",
                    "-ZipPath",
                    str(zip_path),
                    "-WorkRoot",
                    str(work_root),
                    "-SkipDoctor",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("Release ZIP verified", result.stdout)


if __name__ == "__main__":
    unittest.main()

