import unittest
from pathlib import Path


class AppStub:
    def __init__(self, base: Path):
        self.config = {"paths": {"comfyui_root": str(base)}, "proxy_settings": {}}


class TestServiceVersionProxy(unittest.TestCase):
    def setUp(self):
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        self.base = base

    def test_compute_api_url_modes(self):
        from services.version_service import VersionService
        app = AppStub(self.base)
        vs = VersionService(app)
        # 默认 none
        url_none = vs._compute_api_url("owner", "repo")
        self.assertTrue(url_none.startswith("https://api.github.com/repos/owner/repo/releases"))
        # gh-proxy
        app.config["proxy_settings"] = {"git_proxy_mode": "gh-proxy"}
        url_gp = vs._compute_api_url("owner", "repo")
        self.assertTrue(url_gp.startswith("https://gh-proxy.com/https://api.github.com/repos/owner/repo/releases"))
        # custom
        app.config["proxy_settings"] = {"git_proxy_mode": "custom", "git_proxy_url": "https://example.com/"}
        url_c = vs._compute_api_url("owner", "repo")
        self.assertTrue(url_c.startswith("https://example.com/https://api.github.com/repos/owner/repo/releases"))


if __name__ == "__main__":
    unittest.main(verbosity=2)