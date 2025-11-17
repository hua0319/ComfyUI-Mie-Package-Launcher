import unittest
from pathlib import Path


class BigBtnStub:
    def __init__(self):
        self.state = None
        self.text = None
    def set_state(self, s):
        self.state = s
    def set_text(self, t):
        self.text = t


class AppStub:
    def __init__(self, base: Path):
        self.big_btn = BigBtnStub()
        self.custom_port = type("V", (), {"get": lambda self: "8188"})()
        self.config = {"paths": {"comfyui_root": str(base), "python_path": str(base / "python_embeded" / "python.exe")}}


class TestServiceProcessRefresh(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        self.base = base

    def test_refresh_running_status_states(self):
        from core.process_manager import ProcessManager, is_http_reachable as real_is_http
        import core.process_manager as pm_mod
        app = AppStub(self.base)
        pm = ProcessManager(app)
        # 运行态：有进程句柄
        class P:
            def poll(self):
                return None
        pm.comfyui_process = P()
        pm._refresh_running_status()
        self.assertEqual(app.big_btn.state, "running")
        self.assertEqual(app.big_btn.text, "停止")
        # 空句柄 + 可达
        pm.comfyui_process = None
        pm_mod.is_http_reachable = lambda _app: True
        pm._refresh_running_status()
        self.assertEqual(app.big_btn.state, "running")
        self.assertEqual(app.big_btn.text, "停止")
        # 空句柄 + 不可达
        pm_mod.is_http_reachable = lambda _app: False
        pm._refresh_running_status()
        self.assertEqual(app.big_btn.state, "idle")
        self.assertEqual(app.big_btn.text, "一键启动")
        # 恢复原函数
        pm_mod.is_http_reachable = real_is_http


if __name__ == "__main__":
    unittest.main(verbosity=2)