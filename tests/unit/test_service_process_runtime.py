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
    def __init__(self, base: Path):
        self.root = RootStub()
        self.big_btn = BigBtnStub()
        self.logger = type("L", (), {"info": lambda *a, **k: None, "error": lambda *a, **k: None})()
        self.config = {"paths": {"comfyui_root": str(base), "python_path": str((base / "python_embeded" / "python.exe"))}}
        self.compute_mode = type("V", (), {"get": lambda self: "gpu"})()
        self.use_fast_mode = type("V", (), {"get": False})()
        self.enable_cors = type("V", (), {"get": True})()
        self.listen_all = type("V", (), {"get": True})()
        self.custom_port = type("V", (), {"get": lambda self: "8188"})()
        self.extra_launch_args = type("V", (), {"get": lambda self: ""})()
        self.selected_hf_mirror = type("V", (), {"get": lambda self: "不使用镜像"})()
        self.hf_mirror_url = type("V", (), {"get": lambda self: ""})()
        self.version_manager = type("VM", (), {"proxy_mode_var": type("V", (), {"get": lambda self: "none"})(), "proxy_url_var": type("V", (), {"get": lambda self: ""})()})()


class TestServiceProcessRuntime(unittest.TestCase):
    def test_start_stop_with_status_checks(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        assert (base / "python_embeded" / "python.exe").exists(), "真实 Python 嵌入式不存在"
        from services.process_service import ProcessService
        from core.process_manager import ProcessManager
        from core.probe import is_http_reachable
        app = AppStub(base)
        app.process_manager = ProcessManager(app)
        ps = ProcessService(app)
        # 若已有实例运行，先统一停止
        if is_http_reachable(app):
            app.process_manager.stop_all_comfyui_instances()
            deadline0 = time.time() + 15
            while time.time() < deadline0 and is_http_reachable(app):
                time.sleep(1)
            if is_http_reachable(app):
                self.skipTest("已有 ComfyUI 运行且无法在测试前关闭，跳过该测试以避免干扰")
        self.assertFalse(is_http_reachable(app))
        ps.start()
        # 等待可达
        deadline = time.time() + 300
        while time.time() < deadline and not is_http_reachable(app):
            time.sleep(1)
        self.assertTrue(is_http_reachable(app))
        # 停止并验证不可达
        ps.stop()
        deadline2 = time.time() + 60
        while time.time() < deadline2 and is_http_reachable(app):
            time.sleep(1)
        self.assertFalse(is_http_reachable(app))


if __name__ == "__main__":
    unittest.main(verbosity=2)