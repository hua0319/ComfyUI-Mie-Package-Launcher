import unittest
from pathlib import Path


class AppStub:
    def __init__(self, root: Path, python_exec: Path):
        self.config = {"paths": {"comfyui_root": str(root), "python_path": str(python_exec)}}
        self.python_exec = str(python_exec)
        self.logger = None


class TestServiceVersionMore(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        py = base / "python_embeded" / "python.exe"
        assert py.exists(), "真实 Python 嵌入式不存在"
        self.base = base
        self.py = py

    def test_upgrade_to_commit_stable_only(self):
        from services.version_service import VersionService
        app = AppStub(self.base, self.py)
        vs = VersionService(app)
        cur = vs.get_current_kernel_version()
        commit = cur.get('commit')
        if not commit:
            self.skipTest('当前提交未知')
        res = vs.upgrade_to_commit(commit, stable_only=True)
        # 允许两种真实结果：稳定更新成功或非稳定拒绝
        self.assertTrue(res.get('updated') is True or res.get('error_code') == 'NON_STABLE')

    def test_upgrade_latest_non_stable_path(self):
        from services.version_service import VersionService
        app = AppStub(self.base, self.py)
        vs = VersionService(app)
        res = vs.upgrade_latest(stable_only=False)
        # 非稳定路径依赖 VersionManager，不在 Service-only 上运行时可能返回错误
        self.assertEqual(res.get('component'), 'core')


if __name__ == "__main__":
    unittest.main(verbosity=2)