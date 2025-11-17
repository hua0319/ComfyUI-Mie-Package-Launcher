import unittest
import sys
from pathlib import Path
from unittest import mock


class _Var:
    def __init__(self, v): self._v = v
    def get(self): return self._v
    def set(self, v): self._v = v


class TestViewServices(unittest.TestCase):
    def _app(self):
        from comfyui_launcher_enhanced import ComfyUILauncherEnhanced
        base = Path(r"F:\ComfyUI_Mie_V7.0")
        comfy = base / "ComfyUI"
        assert comfy.exists() and (comfy / "main.py").exists(), "真实 ComfyUI 目录不存在或缺少 main.py"
        with mock.patch("tkinter.filedialog.askdirectory", return_value=str(comfy)):
            return ComfyUILauncherEnhanced()

    def test_di_container_installed(self):
        app = self._app()
        self.assertIsNotNone(getattr(app, 'services', None))
        self.assertTrue(hasattr(app.services, 'process'))
        self.assertTrue(hasattr(app.services, 'version'))
        self.assertTrue(hasattr(app.services, 'config'))

    def test_process_service_delegates(self):
        app = self._app()
        app.process_manager.toggle_comfyui = mock.Mock()
        app.process_manager.start_comfyui = mock.Mock()
        app.process_manager.stop_comfyui = mock.Mock(return_value=True)
        app.process_manager._refresh_running_status = mock.Mock()
        app.process_manager.monitor_process = mock.Mock()
        s = app.services.process
        s.toggle(); s.start(); s.stop(); s.refresh_status(); s.monitor()
        app.process_manager.toggle_comfyui.assert_called()
        app.process_manager.start_comfyui.assert_called()
        app.process_manager.stop_comfyui.assert_called()
        app.process_manager._refresh_running_status.assert_called()
        app.process_manager.monitor_process.assert_called()

    def test_version_service_refresh(self):
        app = self._app()
        with mock.patch("core.version_service.refresh_version_info") as rf:
            app.services.version.refresh("core_only")
            rf.assert_called()

    def test_version_service_is_stable_version(self):
        app = self._app()
        vs = app.services.version
        setattr(app, '_releases_cache', [
            {"tag_name": "v1.2.3", "prerelease": False},
            {"tag_name": "v2.0.0-beta", "prerelease": True},
        ])
        self.assertTrue(vs.is_stable_version('v1.2.3'))
        self.assertFalse(vs.is_stable_version('v2.0.0-beta'))

    def test_version_service_latest_stable(self):
        app = self._app()
        info = app.services.version.get_latest_stable_kernel(force_refresh=True)
        self.assertIn('tag', info)
        self.assertIn('commit', info)

    def test_version_service_upgrade_strategies(self):
        app = self._app()
        with mock.patch.object(app.services.version, '_checkout_commit', return_value={"component": "core", "updated": True}):
            with mock.patch.object(app.services.version, 'get_latest_stable_kernel', return_value={"tag": "v1.0.0", "commit": "abc", "success": True}):
                res = app.services.version.upgrade_latest(stable_only=True)
                self.assertTrue(res.get('updated'))
            with mock.patch.object(app.services.version, '_tag_commit', return_value='hash123'):
                with mock.patch.object(app.services.version, '_list_tags', return_value=['v1.0.0']):
                    res2 = app.services.version.upgrade_to_commit('hash999', stable_only=True)
                    self.assertEqual(res2.get('error_code'), 'NON_STABLE')

    def test_config_service_basic(self):
        app = self._app()
        cs = app.services.config
        cfg = cs.load()
        self.assertIn("paths", cfg)
        cs.set("paths.comfyui_root", str(Path.cwd()))
        cs.save()

    def test_view_save_config_delegates_to_service(self):
        app = self._app()
        with mock.patch.object(app.services.config, 'update_launch_options') as ulo, \
             mock.patch.object(app.services.config, 'update_proxy_settings') as ups, \
             mock.patch.object(app.services.config, 'save') as sv:
            app.save_config()
            self.assertTrue(ulo.called)
            self.assertTrue(ups.called)
            self.assertTrue(sv.called)

    def test_config_service_update_methods(self):
        app = self._app()
        cs = app.services.config
        cs.update_launch_options(default_port="9999", enable_fast_mode=True)
        cs.update_proxy_settings(pypi_proxy_mode="custom", pypi_proxy_url="https://example/simple/")
        cs.save(None)
        self.assertEqual(cs.get("launch_options.default_port"), "9999")
        self.assertTrue(cs.get("launch_options.enable_fast_mode"))
        self.assertEqual(cs.get("proxy_settings.pypi_proxy_mode"), "custom")
        self.assertEqual(cs.get("proxy_settings.pypi_proxy_url"), "https://example/simple/")

    def test_update_service_error_return(self):
        app = self._app()
        with mock.patch("utils.pip.install_or_update_package", return_value={"error": "network"}):
            res = app.services.update.update_frontend(False)
            self.assertIn("error", res)
            self.assertFalse(res.get("updated", False))
            self.assertFalse(res.get("up_to_date", False))

    def test_update_service_templates_error_return(self):
        app = self._app()
        with mock.patch("utils.pip.install_or_update_package", return_value={"error": "network"}):
            res = app.services.update.update_templates(False)
            self.assertIn("error", res)
            self.assertFalse(res.get("updated", False))
            self.assertFalse(res.get("up_to_date", False))

    def test_git_service_apply_writes_ini_and_updates_config(self):
        app = self._app()
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ini_dir = root / "ComfyUI" / "user" / "default" / "ComfyUI-Manager"
            ini_dir.mkdir(parents=True, exist_ok=True)
            app.config["paths"]["comfyui_root"] = str(root)
            gp = str(Path(__import__('sys').executable))
            app.services.git.apply_to_manager(gp)
            ini_path = ini_dir / "config.ini"
            self.assertTrue(ini_path.exists())
            content = ini_path.read_text(encoding="utf-8", errors="ignore")
            self.assertIn("git_exe = ", content)
            self.assertIn(gp, content)
            self.assertEqual(app.services.config.get("integrations.comfyui_manager_git_path"), gp)

    def test_update_service_batch(self):
        app = self._app()
        app.update_core_var.set(True)
        app.update_frontend_var.set(True)
        app.update_template_var.set(False)
        results, summary = app.services.update.perform_batch_update()
        self.assertTrue(isinstance(results, list))
        self.assertTrue(isinstance(summary, str))

    def test_update_service_frontend_index_selection(self):
        app = self._app()
        app.pypi_proxy_mode.set('aliyun')
        res = app.services.update.update_frontend(False)
        self.assertEqual(res.get('component'), 'frontend')

    def test_update_service_templates_custom_index(self):
        app = self._app()
        app.pypi_proxy_mode.set('custom')
        app.pypi_proxy_url.set('https://mirrors.aliyun.com/pypi/simple/')
        res = app.services.update.update_templates(False)
        self.assertEqual(res.get('component'), 'templates')

    def test_git_service_resolve(self):
        app = self._app()
        gp, src = app.services.git.resolve_git()
        self.assertTrue(src in ("使用整合包Git", "使用系统Git", "未找到Git命令"))

    def test_network_service_apply(self):
        app = self._app()
        app.services.network.apply_pip_proxy_settings()

    def test_runtime_service_pre_start(self):
        app = self._app()
        app.config["paths"]["python_path"] = str(Path(__import__('sys').executable))
        app.services.runtime.pre_start_up()

    def test_process_manager_calls_runtime_pre_start(self):
        app = self._app()
        app.services.runtime.pre_start_up = mock.Mock()
        with mock.patch("core.launcher_cmd.build_launch_params") as build:
            py = Path(__import__('sys').executable)
            main = Path(__file__)
            build.return_value = (["python", "-c", "print('x')"], {}, Path.cwd(), py, main)
            with mock.patch("core.runner_start.start") as rs:
                app.process_manager.start_comfyui()
                app.services.runtime.pre_start_up.assert_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)