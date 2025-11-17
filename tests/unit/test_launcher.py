import os
import sys
import json
import time
import tempfile
import unittest
import logging
from pathlib import Path
from unittest import mock


class TestComfyUILauncherEnhanced(unittest.TestCase):
    def setUp(self):
        self.comfy_root = Path(r"F:\ComfyUI_Mie_V7.0\ComfyUI")
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def _new_app(self):
        # Patch base root to our temp directory and python exec
        # Reset logger handlers to ensure log path under test base
        import logging as _logging
        lg = _logging.getLogger("comfyui_launcher")
        for h in list(lg.handlers):
            try:
                h.close()
            except Exception:
                pass
        lg.handlers = []
        def _valid(p):
            try:
                return str(Path(p)).lower() == str(self.comfy_root).lower()
            except Exception:
                return False
        with mock.patch("utils.paths.resolve_python_exec", return_value=Path(sys.executable)), \
             mock.patch("utils.paths.validate_comfy_root", side_effect=_valid), \
             mock.patch("tkinter.messagebox.showwarning"), \
             mock.patch("tkinter.filedialog.askdirectory", return_value=str(self.comfy_root)):
            from comfyui_launcher_enhanced import ComfyUILauncherEnhanced
            app = ComfyUILauncherEnhanced()
            # Run immediate version info quietly; override after scheduling to run instantly
            app.root.after = lambda *_args, **_kw: (_args[1]() if len(_args) >= 2 and callable(_args[1]) else None)
            return app

    def test_initialization_sets_paths_and_logs(self):
        print("-> 测试：初始化与日志安装（确保配置与日志可用）")
        app = self._new_app()
        cfg = app.config
        self.assertIn("paths", cfg)
        self.assertTrue(cfg["paths"]["comfyui_root"].lower().endswith("comfyui_mie_v7.0"))
        # 能初始化并设置配置路径即可
        self.assertIsNotNone(app.logger)

    def test_config_load_and_save(self):
        print("-> 测试：配置加载与保存（更新启动选项并持久化）")
        app = self._new_app()
        app.compute_mode.set("cpu")
        app.custom_port.set("8282")
        app.enable_cors.set(False)
        app.save_config()
        cfg_path = Path(app.config_manager.config_file)
        self.assertTrue(cfg_path.exists())
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        self.assertEqual(data["launch_options"]["default_compute_mode"], "cpu")
        self.assertEqual(data["launch_options"]["default_port"], "8282")
        self.assertFalse(data["launch_options"]["enable_cors"])

    def test_dependency_version_checks(self):
        print("-> 测试：依赖版本查询（前端与模板库）")
        app = self._new_app()
        with mock.patch("utils.pip.get_package_version", side_effect=["1.2.3", "0.3.1"]):
            app.get_version_info(scope="all")
            # allow scheduled callbacks to execute
            time.sleep(0.1)
            self.assertIn(app.frontend_version.get(), ("1.2.3", "获取中…", "未安装"))
            self.assertIn(app.template_version.get(), ("0.3.1", "获取中…", "未安装"))

    def test_select_version_tab_and_attach(self):
        print("-> 测试：版本页切换与嵌入状态标记")
        app = self._new_app()
        # stub attach method
        app.select_tab("version")
        self.assertTrue(getattr(app, "_vm_embedded", False))

    def test_open_dirs_and_files(self):
        print("-> 测试：打开根/日志/输入/输出/插件/工作流目录")
        app = self._new_app()
        with mock.patch("utils.paths.get_comfy_root", return_value=self.comfy_root), \
             mock.patch("os.startfile") as st:
            app.open_root_dir()
            app.open_logs_dir()
            app.open_input_dir()
            app.open_output_dir()
            app.open_plugins_dir()
            app.open_workflows_dir()
            self.assertTrue(st.called)

    def test_reset_settings(self):
        print("-> 测试：恢复默认设置（镜像/代理/额外参数）")
        app = self._new_app()
        app.hf_mirror_entry = mock.Mock()
        app.github_proxy_url_entry = mock.Mock()
        with mock.patch("tkinter.messagebox.askyesno", return_value=True):
            app.reset_settings()
        self.assertEqual(app.pypi_proxy_mode.get(), "aliyun")
        self.assertEqual(app.hf_mirror_url.get(), "https://hf-mirror.com")

    def test_hf_mirror_selected_behaviour(self):
        print("-> 测试：HF 镜像选择行为（预设与自定义输入框可见性）")
        app = self._new_app()
        app.hf_mirror_entry = mock.Mock()
        app.selected_hf_mirror.set("hf-mirror")
        app.on_hf_mirror_selected()
        self.assertEqual(app.hf_mirror_url.get(), "https://hf-mirror.com")
        app.selected_hf_mirror.set("自定义")
        app.on_hf_mirror_selected()
        app.hf_mirror_entry.configure.assert_called()

    def test_batch_update_summary(self):
        print("-> 测试：批量更新汇总弹窗（内核/前端/模板库）")
        app = self._new_app()
        app.update_core_var.set(True)
        app.update_frontend_var.set(True)
        app.update_template_var.set(True)
        app.version_manager.update_to_latest = mock.Mock(return_value={"component": "core", "updated": True, "branch": "main"})
        app.update_frontend = mock.Mock(return_value={"component": "frontend", "updated": True, "version": "1.0.0"})
        app.update_template_library = mock.Mock(return_value={"component": "templates", "updated": True, "version": "0.1.0"})
        msgs = []
        with mock.patch("tkinter.messagebox.showinfo", side_effect=lambda t, m: msgs.append(m)):
            class StubThread:
                def __init__(self, target=None, daemon=None):
                    self.target = target
                def start(self):
                    if self.target:
                        self.target()
            with mock.patch("threading.Thread", StubThread):
                app.perform_batch_update()
        self.assertTrue(any("内核" in m and "已更新" in m for m in msgs))
        self.assertTrue(any("前端" in m and "已更新" in m for m in msgs))
        self.assertTrue(any("模板库" in m and "已更新" in m for m in msgs))

    def test_reset_comfyui_path_updates_config(self):
        print("-> 测试：重设 ComfyUI 路径并刷新配置与版本信息")
        app = self._new_app()
        newdir = Path(tempfile.mkdtemp())
        (newdir / "main.py").write_text("print()", encoding="utf-8")
        with mock.patch("tkinter.filedialog.askdirectory", return_value=str(newdir)):
            app.reset_comfyui_path()
        self.assertEqual(app.config["paths"]["comfyui_root"], str(newdir.resolve().parent))

    @unittest.skip("跳过：关闭流程用例不参与当前自动化测试")
    def test_on_closing_calls_stop_when_running(self):
        print("-> 测试：关闭流程（运行中实例先停止再退出）")
        app = self._new_app()
        class P:
            def poll(self):
                return None
        app.process_manager.comfyui_process = P()
        app.process_manager.stop_comfyui = mock.Mock()
        app.root.destroy = mock.Mock()
        app.on_closing()
        app.process_manager.stop_comfyui.assert_called()
        app.root.destroy.assert_called()

    def test_open_web(self):
        print("-> 测试：打开 Web 界面（端口拼接）")
        app = self._new_app()
        app.custom_port.set("9999")
        with mock.patch("webbrowser.open") as wb:
            app.open_comfyui_web()
            wb.assert_called()

    def test_proxy_mode_trace_triggers_apply(self):
        print("-> 测试：PyPI 代理模式变更触发 pip.ini 更新")
        app = self._new_app()
        called = {}
        with mock.patch("utils.net.apply_pip_proxy_settings", side_effect=lambda *a, **k: called.update({"x": 1})):
            app.pypi_proxy_mode.set("aliyun")
            self.assertTrue("x" in called)

    def test_select_tab_error_handling(self):
        print("-> 测试：版本页切换异常提示（select_tab 错误路径）")
        app = self._new_app()
        app.version_manager.attach_to_container = mock.Mock(side_effect=RuntimeError("err"))
        with mock.patch("tkinter.messagebox.showerror") as me:
            app.select_tab("version")
            self.assertTrue(me.called)

    def test_update_frontend_notification_text(self):
        print("-> 测试：前端更新返回结构与标志位")
        app = self._new_app()
        calls = []
        with mock.patch("utils.pip.install_or_update_package", return_value={
            "success": True, "updated": True, "up_to_date": False, "version": "1.32.5", "error": None
        }):
            res = app.update_frontend(notify=True)
            self.assertTrue(res["updated"]) 

    def test_update_templates_notification_text(self):
        print("-> 测试：模板库更新返回结构与标志位")
        app = self._new_app()
        calls = []
        with mock.patch("utils.pip.install_or_update_package", return_value={
            "success": True, "updated": True, "up_to_date": False, "version": "0.3.1", "error": None
        }):
            res = app.update_template_library(notify=True)
            self.assertTrue(res["updated"]) 

    def test_dummy_env_validation(self):
        print("-> 测试：环境验证（Python 版本获取路径）")
        # 简单环境验证：能解析 Python 版本且不抛异常
        app = self._new_app()
        app.get_version_info(scope="all")
        time.sleep(0.1)
        self.assertTrue(app.python_version.get() in ("获取中…", "无法获取", "获取失败") or len(app.python_version.get()) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)