import unittest
from pathlib import Path


class V:
    def __init__(self, v): self._v=v
    def get(self): return self._v
    def set(self, v): self._v=v


class AppStub:
    def __init__(self, root: Path, python_exec: Path):
        self.config = {"paths": {"comfyui_root": str(root), "python_path": str(python_exec)}}
        self.python_exec = str(python_exec)
        self.logger = None
        self.update_core_var = V(True)
        self.update_frontend_var = V(False)
        self.update_template_var = V(False)
        self.stable_only_var = V(True)
        self.pypi_proxy_mode = V('aliyun')
        self.pypi_proxy_url = V('https://mirrors.aliyun.com/pypi/simple/')
        class Services:
            pass
        self.services = Services()
        from services.version_service import VersionService
        from services.update_service import UpdateService
        self.services.version = VersionService(self)
        self.services.update = UpdateService(self)


class TestServiceUpdate(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        self.base = base
        self.comfy = comfy
        self.py = Path(__import__('sys').executable)

    def test_update_frontend_templates_and_batch(self):
        from services.update_service import UpdateService
        app = AppStub(self.base, self.py)
        us = UpdateService(app)
        fr = us.update_frontend(False)
        tp = us.update_templates(False)
        self.assertEqual(fr.get('component'), 'frontend')
        self.assertEqual(tp.get('component'), 'templates')
        results, summary = us.perform_batch_update()
        self.assertTrue(isinstance(results, list))
        self.assertTrue(isinstance(summary, str))

    def test_get_current_versions(self):
        from services.update_service import UpdateService
        app = AppStub(self.base, self.py)
        us = UpdateService(app)
        fv = us.get_frontend_version()
        tv = us.get_templates_version()
        self.assertTrue((fv is None) or isinstance(fv, str))
        self.assertTrue((tv is None) or isinstance(tv, str))


if __name__ == "__main__":
    unittest.main(verbosity=2)