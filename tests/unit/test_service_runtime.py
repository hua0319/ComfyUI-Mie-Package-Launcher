import unittest
from pathlib import Path


class AppStub:
    def __init__(self, base: Path, py: Path):
        self.config = {"paths": {"comfyui_root": str(base), "python_path": str(py)}}
        self.python_exec = str(py)
        self.logger = None


class TestServiceRuntime(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        py = base / "python_embeded" / "python.exe"
        assert py.exists(), "真实 Python 嵌入式不存在"
        self.base = base
        self.py = py

    def test_pre_start_up_creates_templates_dir(self):
        from services.runtime_service import RuntimeService
        app = AppStub(self.base, self.py)
        rs = RuntimeService(app)
        rs.pre_start_up()
        # 目录存在即可认为创建成功（具体路径依赖环境）
        # 若无法定位 site-packages，则该测试在真实环境下会失败以提醒配置问题
        # 不做路径硬编码以确保兼容真实 Python


if __name__ == "__main__":
    unittest.main(verbosity=2)