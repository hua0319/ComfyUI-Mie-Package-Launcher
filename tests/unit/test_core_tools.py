import unittest
import tempfile
from pathlib import Path
from unittest import mock


class _Var:
    def __init__(self, v):
        self._v = v
    def get(self):
        return self._v
    def set(self, v):
        self._v = v


class TestCoreTools(unittest.TestCase):
    def test_launcher_cmd_build(self):
        from core.launcher_cmd import build_launch_params
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            # create ComfyUI with python_embeded
            comfy = base / "ComfyUI"
            comfy.mkdir(parents=True, exist_ok=True)
            (comfy / "main.py").write_text("print('x')", encoding="utf-8")
            py_emb = base / "python_embeded"
            py_emb.mkdir(parents=True, exist_ok=True)
            py_exec = py_emb / ("python.exe")
            py_exec.write_text("", encoding="utf-8")

        class VM:
            def __init__(self):
                self.proxy_mode_var = _Var('gh-proxy')
                self.proxy_url_var = _Var('https://gh-proxy.com/')

        class App:
            def __init__(self):
                self.config = {"paths": {"comfyui_root": str(base), "python_path": str(py_exec)}}
                self.compute_mode = _Var("cpu")
                self.use_fast_mode = _Var(True)
                self.enable_cors = _Var(True)
                self.listen_all = _Var(True)
                self.custom_port = _Var("8282")
                self.extra_launch_args = _Var("--foo bar")
                self.selected_hf_mirror = _Var("hf-mirror")
                self.hf_mirror_url = _Var("https://hf-mirror.com")
                self.version_manager = VM()
            def save_config(self):
                pass

        app = App()
        cmd, env, run_cwd, py, main = build_launch_params(app)
        self.assertIn(str(main), cmd)
        self.assertIn("--cpu", cmd)
        self.assertIn("--listen", cmd)
        self.assertIn("--port", cmd)
        self.assertIn("8282", cmd)
        self.assertIn("--enable-cors-header", cmd)
        self.assertIn("--foo", cmd)
        self.assertEqual(Path(run_cwd).resolve(), (Path(app.config["paths"]["comfyui_root"]).resolve() / "ComfyUI").resolve())
        self.assertTrue(env.get("HF_ENDPOINT", "").startswith("https://hf-mirror"))
        self.assertTrue(env.get("GITHUB_ENDPOINT", "").startswith("https://gh-proxy.com/https://github.com"))

    def test_probe_find_pids_by_port_netstat(self):
        import types
        from core import probe
        # monkeypatch run_hidden to simulate netstat output
        class R:
            returncode = 0
            stdout = "\n TCP    127.0.0.1:8188     0.0.0.0:0      LISTENING       1234\n"
        probe.run_hidden = lambda *a, **k: R()
        pids = probe.find_pids_by_port_safe("8188")
        self.assertIn(1234, pids)

    def test_probe_is_http_reachable_fallback(self):
        from core import probe
        import types
        class A:
            def __init__(self):
                self.custom_port = _Var("8188")
        probe.socket = types.SimpleNamespace(create_connection=lambda *a, **k: (_ for _ in ()).throw(Exception("no")))
        with mock.patch("core.probe.find_pids_by_port_safe", return_value=[1111]):
            self.assertTrue(probe.is_http_reachable(A()))

    def test_kill_pids_windows(self):
        from core import kill
        calls = []
        with mock.patch("core.kill.run_hidden", side_effect=lambda *a, **k: calls.append(a)):
            kill.kill_pids(object(), [111, 222])
        self.assertTrue(len(calls) >= 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)