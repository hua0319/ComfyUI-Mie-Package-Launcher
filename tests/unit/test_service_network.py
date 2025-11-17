import unittest
from pathlib import Path


class AppStub:
    def __init__(self, root: Path, python_exec: Path):
        self.config = {"paths": {"comfyui_root": str(root), "python_path": str(python_exec)}}
        self.python_exec = str(python_exec)
        self.logger = None
        self.pypi_proxy_mode = type("V", (), {"get": lambda self: "aliyun"})()
        self.pypi_proxy_url = type("V", (), {"get": lambda self: "https://mirrors.aliyun.com/pypi/simple/"})()


class TestServiceNetwork(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        self.base = base
        self.py = Path(__import__('sys').executable)

    def test_apply_pip_proxy_settings_real(self):
        from services.network_service import NetworkService
        app = AppStub(self.base, self.py)
        ns = NetworkService(app)
        ns.apply_pip_proxy_settings()


if __name__ == "__main__":
    unittest.main(verbosity=2)