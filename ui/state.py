import tkinter as tk

def setup_variables(app):
    app.compute_mode = tk.StringVar(value="gpu")
    app.use_fast_mode = tk.BooleanVar()
    app.enable_cors = tk.BooleanVar(value=True)
    app.listen_all = tk.BooleanVar(value=True)
    app.custom_port = tk.StringVar(value="8188")
    app.extra_launch_args = tk.StringVar(value="")
    app.hf_mirror_options = {"不使用镜像": "", "hf-mirror": "https://hf-mirror.com"}
    app.selected_hf_mirror = tk.StringVar(value="hf-mirror")
    app.comfyui_version = tk.StringVar(value="获取中…")
    app.frontend_version = tk.StringVar(value="获取中…")
    app.template_version = tk.StringVar(value="获取中…")
    app.python_version = tk.StringVar(value="获取中…")
    app.torch_version = tk.StringVar(value="获取中…")
    app.git_status = tk.StringVar(value="检测中…")
    app.git_path = None
    app.update_core_var = tk.BooleanVar(value=True)
    app.update_frontend_var = tk.BooleanVar(value=True)
    app.update_template_var = tk.BooleanVar(value=True)
    proxy_cfg = app.config.get("proxy_settings", {}) if isinstance(app.config, dict) else {}
    default_pypi_mode = proxy_cfg.get("pypi_proxy_mode", "aliyun")
    default_pypi_url = proxy_cfg.get("pypi_proxy_url", "https://mirrors.aliyun.com/pypi/simple/")
    app.pypi_proxy_mode = tk.StringVar(value=default_pypi_mode)
    app.pypi_proxy_url = tk.StringVar(value=default_pypi_url)
    def _pypi_mode_ui_text(mode: str):
        return "阿里云" if mode == "aliyun" else ("自定义" if mode == "custom" else "不使用")
    app.pypi_proxy_mode_ui = tk.StringVar(value=_pypi_mode_ui_text(default_pypi_mode))
    app.pypi_proxy_mode.trace_add("write", lambda *a: (app.save_config(), app.apply_pip_proxy_settings()))
    app.pypi_proxy_url.trace_add("write", lambda *a: (app.save_config(), app.apply_pip_proxy_settings()))
    try:
        _orig_set = app.pypi_proxy_mode.set
        def _set_and_apply(v):
            try:
                _orig_set(v)
            finally:
                try:
                    app.apply_pip_proxy_settings()
                except Exception:
                    pass
        app.pypi_proxy_mode.set = _set_and_apply
    except Exception:
        pass
    app.compute_mode.trace_add("write", lambda *a: app.save_config())
    app.use_fast_mode.trace_add("write", lambda *a: app.save_config())
    app.enable_cors.trace_add("write", lambda *a: app.save_config())
    app.listen_all.trace_add("write", lambda *a: app.save_config())
    app.custom_port.trace_add("write", lambda *a: app.save_config())
    app.extra_launch_args.trace_add("write", lambda *a: app.save_config())
    default_hf_url = proxy_cfg.get("hf_mirror_url", "https://hf-mirror.com")
    app.hf_mirror_url = tk.StringVar(value=default_hf_url)
    try:
        app.selected_hf_mirror.set(proxy_cfg.get("hf_mirror_mode", "hf-mirror"))
    except Exception:
        pass
    app.selected_hf_mirror.trace_add("write", lambda *a: app.save_config())
    app.hf_mirror_url.trace_add("write", lambda *a: app.save_config())