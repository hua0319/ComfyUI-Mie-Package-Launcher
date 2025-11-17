import unittest
from pathlib import Path


class TestPathsRoot(unittest.TestCase):
    def test_get_comfy_root_default(self):
        from utils.paths import get_comfy_root
        r = get_comfy_root({})
        self.assertTrue(str(r).endswith("ComfyUI") or str(r))

    def test_get_comfy_root_from_config(self):
        from utils.paths import get_comfy_root
        base = Path.cwd()
        cfg = {"comfyui_root": str(base)}
        r = get_comfy_root(cfg)
        self.assertEqual(r, (base / "ComfyUI").resolve())

    def test_child_dirs_join(self):
        from utils import paths as PATHS
        base = Path.cwd() / "ComfyUI"
        self.assertEqual(PATHS.logs_file(base), base / "user" / "comfyui.log")
        self.assertEqual(PATHS.input_dir(base), base / "input")
        self.assertEqual(PATHS.output_dir(base), base / "output")
        self.assertEqual(PATHS.plugins_dir(base), base / "custom_nodes")
        self.assertEqual(PATHS.workflows_dir(base), base / "user" / "default" / "workflows")


if __name__ == "__main__":
    unittest.main(verbosity=2)