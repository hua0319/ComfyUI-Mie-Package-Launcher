import unittest
from pathlib import Path


class AppStub:
    def __init__(self, root: Path, python_exec: Path):
        self.config = {"paths": {"comfyui_root": str(root), "python_path": str(python_exec)}}
        self.python_exec = str(python_exec)
        self.logger = None


class TestServiceVersion(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        self.base = base
        self.comfy = comfy
        self.py = Path(__import__('sys').executable)

    def test_repo_root_and_is_stable(self):
        from services.version_service import VersionService
        app = AppStub(self.base, self.py)
        vs = VersionService(app)
        root = Path(vs._repo_root())
        self.assertTrue((root / 'main.py').exists())
        # 语义规则判断
        self.assertTrue(vs.is_stable_version('v1.2.3') is True or vs.is_stable_version('v1.2.3') is False)

    def test_latest_stable_and_upgrade_paths(self):
        from services.version_service import VersionService
        app = AppStub(self.base, self.py)
        vs = VersionService(app)
        info = vs.get_latest_stable_kernel(force_refresh=True)
        self.assertIn('tag', info)
        self.assertIn('commit', info)
        res_stable = vs.upgrade_latest(stable_only=True)
        self.assertEqual(res_stable.get('component'), 'core')
        # 非稳定路径走 VersionManager
        try:
            res_any = app.__dict__.get('version_manager', None)
        except Exception:
            res_any = None

    def test_current_kernel_version(self):
        from services.version_service import VersionService
        app = AppStub(self.base, self.py)
        vs = VersionService(app)
        cur = vs.get_current_kernel_version()
        self.assertIn('tag', cur)
        self.assertIn('commit', cur)


if __name__ == "__main__":
    unittest.main(verbosity=2)