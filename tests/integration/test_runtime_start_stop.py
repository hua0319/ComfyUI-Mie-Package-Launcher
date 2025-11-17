import unittest
import time
from pathlib import Path


class RootStub:
    def after(self, _delay, cb):
        try:
            if callable(cb):
                cb()
        except Exception:
            pass


class BigBtnStub:
    def set_state(self, *_):
        pass
    def set_text(self, *_):
        pass


class AppStub:
    def __init__(self, root_dir: Path):
        self.root = RootStub()
        self.big_btn = BigBtnStub()
        self.logger = type("L", (), {"info": lambda *a, **k: None, "error": lambda *a, **k: None})()
        self.config = {"paths": {"comfyui_root": str(root_dir), "python_path": str((root_dir / "python_embeded" / "python.exe"))}}
        self.compute_mode = type("V", (), {"get": lambda self: "gpu"})()
        self.use_fast_mode = type("V", (), {"get": False})()
        self.enable_cors = type("V", (), {"get": True})()
        self.listen_all = type("V", (), {"get": True})()
        self.custom_port = type("V", (), {"get": lambda self: "8188"})()
        self.extra_launch_args = type("V", (), {"get": lambda self: ""})()
        self.selected_hf_mirror = type("V", (), {"get": lambda self: "不使用镜像"})()
        self.hf_mirror_url = type("V", (), {"get": lambda self: ""})()
        self.version_manager = type("VM", (), {"proxy_mode_var": type("V", (), {"get": lambda self: "none"})(), "proxy_url_var": type("V", (), {"get": lambda self: ""})()})()


class TestRuntimeStartStop(unittest.TestCase):
    def test_start_and_stop_real(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy_dir = base / "ComfyUI"
        assert comfy_dir.exists() and (comfy_dir / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        assert (base / "python_embeded" / "python.exe").exists(), "真实 Python 嵌入式不存在"
        from core.process_manager import ProcessManager
        from core.probe import is_http_reachable
        app = AppStub(base)
        pm = ProcessManager(app)
        # 启动前状态应不可达
        self.assertFalse(is_http_reachable(app))
        pm.start_comfyui()
        # 等待服务可达
        deadline = time.time() + 300
        while time.time() < deadline and not is_http_reachable(app):
            time.sleep(1)
        self.assertTrue(is_http_reachable(app))
        killed = pm.stop_comfyui()
        # 等待服务关闭
        deadline2 = time.time() + 60
        while time.time() < deadline2 and is_http_reachable(app):
            time.sleep(1)
        self.assertTrue(killed or pm.comfyui_process is None)
        self.assertFalse(is_http_reachable(app))


if __name__ == "__main__":
    unittest.main(verbosity=2)