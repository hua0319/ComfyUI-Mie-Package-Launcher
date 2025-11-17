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
        self.update_core_var = V(False)
        self.update_frontend_var = V(True)
        self.update_template_var = V(True)
        self.stable_only_var = V(True)
        self.pypi_proxy_mode = V('none')
        self.pypi_proxy_url = V('')
        class Services:
            pass
        self.services = Services()
        from services.update_service import UpdateService
        self.services.update = UpdateService(self)


class TestServiceUpdateProxies(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        py = base / "python_embeded" / "python.exe"
        assert py.exists(), "真实 Python 嵌入式不存在"
        self.base = base
        self.py = py

    def test_none_proxy_mode(self):
        from services.update_service import UpdateService
        app = AppStub(self.base, self.py)
        us = UpdateService(app)
        fr = us.update_frontend(False)
        tp = us.update_templates(False)
        self.assertEqual(fr.get('component'), 'frontend')
        self.assertEqual(tp.get('component'), 'templates')
        self.assertIsNone(fr.get('error'))
        self.assertIsNone(tp.get('error'))
        self.assertTrue(fr.get('updated') or fr.get('up_to_date'))
        self.assertTrue(tp.get('updated') or tp.get('up_to_date'))

    def test_custom_valid_proxy_url(self):
        from services.update_service import UpdateService
        app = AppStub(self.base, self.py)
        app.pypi_proxy_mode.set('custom')
        app.pypi_proxy_url.set('https://pypi.org/simple/')
        us = UpdateService(app)
        fr = us.update_frontend(False)
        tp = us.update_templates(False)
        self.assertEqual(fr.get('component'), 'frontend')
        self.assertEqual(tp.get('component'), 'templates')
        self.assertIsNone(fr.get('error'))
        self.assertIsNone(tp.get('error'))
        self.assertTrue(fr.get('updated') or fr.get('up_to_date'))
        self.assertTrue(tp.get('updated') or tp.get('up_to_date'))


if __name__ == "__main__":
    unittest.main(verbosity=2)