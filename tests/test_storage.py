from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest


class StorageTests(unittest.TestCase):
    def test_storage_uses_override_and_exports_inside_it(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\Temp" if Path("D:\\Temp").exists() else None) as tmp:
            old_home = os.environ.get("NPC_CHAOS_HOME")
            old_disable_open = os.environ.get("NPC_CHAOS_DISABLE_OPEN")
            os.environ["NPC_CHAOS_HOME"] = tmp
            os.environ.pop("NPC_CHAOS_DISABLE_OPEN", None)
            try:
                from npc_chaos_app import storage
                from npc_chaos_app.engine import generate_npc

                state = storage.load_default_state()
                state["names"][0] = "Test NPC"
                storage.save_state(state)
                loaded = storage.load_state()
                self.assertEqual(loaded["names"][0], "Test NPC")

                scene = generate_npc(loaded, {"seed": 42})
                favourite = storage.save_favourite(scene)
                self.assertEqual(storage.list_favourites()[0]["id"], favourite["id"])

                exported = storage.export_npc(scene, "txt")
                self.assertTrue(Path(exported["path"]).exists())
                self.assertTrue(str(exported["path"]).startswith(tmp))

                opened_paths = []
                result = storage.open_exports_folder(opener=lambda path: opened_paths.append(path))
                self.assertTrue(result["opened"])
                self.assertEqual(opened_paths[0], Path(tmp, "exports").resolve())
            finally:
                if old_home is None:
                    os.environ.pop("NPC_CHAOS_HOME", None)
                else:
                    os.environ["NPC_CHAOS_HOME"] = old_home
                if old_disable_open is None:
                    os.environ.pop("NPC_CHAOS_DISABLE_OPEN", None)
                else:
                    os.environ["NPC_CHAOS_DISABLE_OPEN"] = old_disable_open


if __name__ == "__main__":
    unittest.main()
