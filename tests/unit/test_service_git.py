import unittest
from pathlib import Path


class AppStub:
    def __init__(self, base: Path):
        self.config = {"paths": {"comfyui_root": str(base)}}
        self.logger = None


class TestServiceGit(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        self.base = base

    def test_resolve_git_real(self):
        from services.git_service import GitService
        app = AppStub(self.base)
        gs = GitService(app)
        gp, src = gs.resolve_git()
        self.assertTrue(src in ("使用整合包Git", "使用系统Git", "未找到Git命令"))

    def test_apply_to_manager_twice(self):
        from services.git_service import GitService
        app = AppStub(self.base)
        gs = GitService(app)
        ini_path = (self.base / "ComfyUI" / "user" / "default" / "ComfyUI-Manager" / "config.ini")
        ini_path.parent.mkdir(parents=True, exist_ok=True)
        gp, src = gs.resolve_git()
        if not gp:
            self.skipTest("git 路径不可用")
        gs.apply_to_manager(gp)
        content1 = ini_path.read_text(encoding="utf-8", errors="ignore")
        gs.apply_to_manager(gp)
        content2 = ini_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("git_exe = ", content1)
        self.assertEqual(content1, content2)

    def test_apply_to_manager_invalid_root(self):
        from services.git_service import GitService
        bad = Path(r"Z:\not_exists_root")
        app = AppStub(bad)
        gs = GitService(app)
        gs.apply_to_manager("git")
        # 无异常即可视为安全返回


if __name__ == "__main__":
    unittest.main(verbosity=2)