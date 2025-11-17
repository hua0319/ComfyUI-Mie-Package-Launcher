import unittest
import tempfile
from pathlib import Path
from unittest import mock


class AppStub:
    def __init__(self, root: Path, python_exec: Path):
        self.config = {"paths": {"comfyui_root": str(root), "python_path": str(python_exec)}}
        self.python_exec = str(python_exec)
        self.logger = None
        self.update_core_var = type("V", (), {"get": lambda self: True})()
        self.update_frontend_var = type("V", (), {"get": lambda self: False})()
        self.update_template_var = type("V", (), {"get": lambda self: False})()
        self.stable_only_var = type("V", (), {"get": lambda self: False})()


class TestServicesNoView(unittest.TestCase):
    def setUp(self):
        real = Path(r"F:\ComfyUI_Mie_V7.0\ComfyUI")
        if not real.exists() or not (real / "main.py").exists():
            raise AssertionError("真实环境缺失：请确保 F:\\ComfyUI_Mie_V7.0\\ComfyUI 存在且包含 main.py")
        self.tmp = None
        self.base = real.parent
        self.comfy = real
        self.py = Path(__import__('sys').executable)

    def tearDown(self):
        pass

    def test_config_service_sets_root_and_paths(self):
        from services.config_service import ConfigService
        cfg_file = self.base / "launcher" / "config.json"
        cs = ConfigService(cfg_file)
        data = cs.load()
        cs.set("paths.comfyui_root", str(self.comfy.resolve().parent))
        cs.save(None)
        from utils import paths as PATHS
        r = PATHS.get_comfy_root(cs.get_config().get("paths", {}))
        self.assertEqual(r, (self.comfy.resolve().parent / "ComfyUI").resolve())
        self.assertEqual(PATHS.logs_file(r), r / "user" / "comfyui.log")
        self.assertEqual(PATHS.input_dir(r), r / "input")
        self.assertEqual(PATHS.output_dir(r), r / "output")
        self.assertEqual(PATHS.plugins_dir(r), r / "custom_nodes")
        self.assertEqual(PATHS.workflows_dir(r), r / "user" / "default" / "workflows")

    def test_version_service_repo_root_without_view(self):
        from services.version_service import VersionService
        app = AppStub(self.comfy.parent, self.py)
        vs = VersionService(app)
        self.assertTrue(vs._repo_root().endswith("ComfyUI"))

    def test_update_service_core_summary_without_view(self):
        from services.update_service import UpdateService
        app = AppStub(self.comfy.parent, self.py)
        app.services = type("S", (), {})()
        app.services.version = type("VS", (), {"upgrade_latest": lambda self, stable_only=False: {"component": "core", "error": "no stable"}})()
        app.version_manager = type("VM", (), {"update_to_latest": lambda self, confirm=False, notify=False: {"component": "core", "updated": True, "branch": "main"}})()
        us = UpdateService(app)
        results, summary = us.perform_batch_update()
        self.assertTrue(any(r.get("component") == "core" for r in results))
        self.assertIn("内核", summary)

    def test_git_service_apply_without_view(self):
        from services.git_service import GitService
        from utils.common import run_hidden
        app = AppStub(self.comfy.parent, self.py)
        gs = GitService(app)
        ini_dir = self.comfy / "user" / "default" / "ComfyUI-Manager"
        ini_dir.mkdir(parents=True, exist_ok=True)
        r = run_hidden(["git", "--version"], capture_output=True, text=True)
        assert r.returncode == 0, "系统 Git 不可用"
        gp, _ = gs.resolve_git()
        assert gp, "未能解析到 Git 路径"
        gs.apply_to_manager(gp)
        ini_path = ini_dir / "config.ini"
        self.assertTrue(ini_path.exists())
        content = ini_path.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("git_exe = ", content)

    def test_process_service_start_python_missing_error_and_log(self):
        from services.process_service import ProcessService
        from core.process_manager import ProcessManager
        import tempfile
        tmp = tempfile.TemporaryDirectory()
        base = Path(tmp.name)
        local_comfy = base / "ComfyUI"
        local_comfy.mkdir(parents=True, exist_ok=True)
        (local_comfy / "main.py").write_text("print()", encoding="utf-8")
        app = AppStub(base, self.py)
        app.config["paths"]["python_path"] = str(base / "missing_python.exe")
        # attach simple logger
        class L:
            def __init__(self):
                self.last = {"error": None, "info": []}
            def error(self, msg, *a, **k):
                self.last["error"] = str(msg)
            def info(self, msg, *a, **k):
                self.last["info"].append(str(msg))
        app.logger = L()
        app.headless = True
        app.process_manager = ProcessManager(app)
        ps = ProcessService(app)
        ps.start()
        self.assertTrue("Python不存在" in (app.logger.last.get("error") or ""))
        self.assertIsNotNone(app.logger)

    def test_build_launch_params_python_fallback(self):
        from core.launcher_cmd import build_launch_params
        base = self.comfy.parent
        # create fallback python under root/python_embeded
        py_dir = base / "python_embeded"
        py_dir.mkdir(parents=True, exist_ok=True)
        py_exec = py_dir / "python.exe"
        py_exec.write_text("", encoding="utf-8")
        class A:
            def __init__(self, root, py):
                self.config = {"paths": {"comfyui_root": str(root), "python_path": str(py)}}
                self.compute_mode = type("V", (), {"get": lambda self: "gpu"})()
                self.use_fast_mode = type("V", (), {"get": lambda self: False})()
                self.enable_cors = type("V", (), {"get": True})()
                self.listen_all = type("V", (), {"get": True})()
                self.custom_port = type("V", (), {"get": lambda self: "8188"})()
                self.extra_launch_args = type("V", (), {"get": lambda self: ""})()
                self.selected_hf_mirror = type("V", (), {"get": lambda self: "不使用镜像"})()
                self.hf_mirror_url = type("V", (), {"get": lambda self: ""})()
                self.version_manager = type("VM", (), {"proxy_mode_var": type("V", (), {"get": lambda self: "none"})(), "proxy_url_var": type("V", (), {"get": lambda self: ""})()})()
        app = A(base, base / "missing_python.exe")
        cmd, env, run_cwd, py, main = build_launch_params(app)
        self.assertEqual(py, py_exec)
        self.assertTrue(str(main).endswith("ComfyUI\\main.py") or str(main).endswith("ComfyUI/main.py"))


if __name__ == "__main__":
    unittest.main(verbosity=2)