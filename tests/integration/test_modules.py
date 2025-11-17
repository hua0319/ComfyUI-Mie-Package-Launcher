import unittest
from pathlib import Path
import sys


class TestModuleImports(unittest.TestCase):
    def test_utils_paths_import(self):
        from utils import paths as PATHS
        base = PATHS.resolve_base_root()
        self.assertIsInstance(base, Path)

    def test_config_manager(self):
        from config.manager import ConfigManager
        cfg_path = Path.cwd() / "launcher" / "config.test.json"
        cm = ConfigManager(cfg_path)
        cfg = cm.load_config()
        self.assertIn("paths", cfg)
        cm.set("paths.comfyui_path", str(Path.cwd()))
        cm.save_config()
        self.assertTrue(cfg_path.exists())
        # cleanup
        try:
            cfg_path.unlink()
        except Exception:
            pass

    def test_core_version_manager_import(self):
        from core.version_manager import VersionManager
        # instantiate minimally without UI
        vm = VersionManager(parent=None, comfyui_path=Path.cwd(), python_path=Path(sys.executable))
        self.assertIsNotNone(vm)

    def test_core_process_manager_import(self):
        from core.process_manager import ProcessManager
        class Stub:
            def __init__(self):
                class _Var:
                    def get(self):
                        return "8188"
                self.custom_port = _Var()
                class _Logger:
                    def info(self, *a, **k):
                        pass
                    def error(self, *a, **k):
                        pass
                self.logger = _Logger()
                self.root = type("R", (), {"after": lambda *_: None})()
                self.big_btn = type("B", (), {"set_state": lambda *_: None, "set_text": lambda *_: None})()
        pm = ProcessManager(Stub())
        self.assertIsNotNone(pm)


if __name__ == "__main__":
    unittest.main()