import threading
import concurrent.futures
from pathlib import Path
from utils.common import run_hidden
from utils import pip as PIPUTILS

def refresh_version_info(app, scope: str = "all"):
    try:
        app.logger.info("开始获取版本信息")
    except Exception:
        pass
    if getattr(app, '_version_info_loading', False):
        return
    app._version_info_loading = True
    if scope == "all":
        for v in (app.comfyui_version, app.frontend_version, app.template_version, app.python_version, app.torch_version):
            v.set("获取中…")
    elif scope == "core_only":
        try:
            app.comfyui_version.set("获取中…")
        except Exception:
            pass
    elif scope == "front_only":
        try:
            app.frontend_version.set("获取中…")
        except Exception:
            pass
    elif scope == "template_only":
        try:
            app.template_version.set("获取中…")
        except Exception:
            pass
    elif scope == "selected":
        try:
            if app.update_core_var.get():
                app.comfyui_version.set("获取中…")
            if app.update_frontend_var.get():
                app.frontend_version.set("获取中…")
            if app.update_template_var.get():
                app.template_version.set("获取中…")
        except Exception:
            pass
    def worker():
        try:
            paths = app.config.get("paths", {}) if isinstance(app.config, dict) else {}
            base = Path(paths.get("comfyui_root") or ".").resolve()
            root = (base / "ComfyUI").resolve()
            git_cmd, git_source_text = app.resolve_git()
            repo_state = ""
            if git_cmd is None:
                repo_state = "未找到Git命令"
            elif not root.exists():
                repo_state = "ComfyUI未找到"
            else:
                try:
                    r_repo = run_hidden([git_cmd, "rev-parse", "--is-inside-work-tree"], cwd=str(root), capture_output=True, text=True, timeout=5)
                    repo_state = "Git正常" if (r_repo.returncode == 0 and r_repo.stdout.strip() == "true") else "非Git仓库"
                except Exception:
                    repo_state = "非Git仓库"
            git_text_to_show = repo_state if repo_state in ("未找到Git命令", "非Git仓库", "ComfyUI未找到") else git_source_text
            app.root.after(0, lambda: app.git_status.set(git_text_to_show))
            def _update_git_controls():
                status = app.git_status.get()
                disable = status in ("非Git仓库", "ComfyUI未找到", "未找到Git命令")
                try:
                    if hasattr(app, 'core_chk'):
                        app.core_chk.config(state='disabled' if disable else 'normal')
                    if hasattr(app, 'front_chk'):
                        app.front_chk.config(state='disabled' if disable else 'normal')
                    if hasattr(app, 'tpl_chk'):
                        app.tpl_chk.config(state='disabled' if disable else 'normal')
                    if hasattr(app, 'batch_update_btn'):
                        app.batch_update_btn.config(state='disabled' if disable else 'normal')
                except:
                    pass
            app.root.after(0, _update_git_controls)
            core_needed = (scope == "all") or (scope == "core_only") or (scope == "selected" and app.update_core_var.get())
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
            futures = []
            def _submit(fn):
                try:
                    f = executor.submit(fn)
                    futures.append(f)
                except Exception:
                    pass
            if scope == "all":
                def _python_ver():
                    try:
                        r = run_hidden([app.python_exec, "--version"], capture_output=True, text=True, timeout=10)
                        if r.returncode == 0:
                            app.root.after(0, lambda v=r.stdout.strip().replace("Python ", ""): app.python_version.set(v))
                        else:
                            app.root.after(0, lambda: app.python_version.set("获取失败"))
                    except Exception:
                        app.root.after(0, lambda: app.python_version.set("获取失败"))
                _submit(_python_ver)
                def _torch_ver():
                    try:
                        r = run_hidden([app.python_exec, "-c", "import torch;print(torch.__version__)"], capture_output=True, text=True, timeout=10)
                        if r.returncode == 0:
                            app.root.after(0, lambda v=r.stdout.strip(): app.torch_version.set(v))
                        else:
                            app.root.after(0, lambda: app.torch_version.set("未安装"))
                    except Exception:
                        app.root.after(0, lambda: app.torch_version.set("获取失败"))
                _submit(_torch_ver)
            if scope == "all" or scope == "front_only" or (scope == "selected" and app.update_frontend_var.get()):
                def _front_ver():
                    try:
                        ver = PIPUTILS.get_package_version("comfyui-frontend-package", app.python_exec, logger=app.logger)
                        if ver:
                            app.root.after(0, lambda v=ver: app.frontend_version.set(v))
                        else:
                            app.root.after(0, lambda: app.frontend_version.set("未安装"))
                    except Exception:
                        app.root.after(0, lambda: app.frontend_version.set("获取失败"))
                _submit(_front_ver)
            if scope == "all" or scope == "template_only" or (scope == "selected" and app.update_template_var.get()):
                def _tpl_ver():
                    try:
                        ver = PIPUTILS.get_package_version("comfyui-workflow-templates", app.python_exec, logger=app.logger)
                        if ver:
                            app.root.after(0, lambda v=ver: app.template_version.set(v))
                        else:
                            app.root.after(0, lambda: app.template_version.set("未安装"))
                    except Exception:
                        app.root.after(0, lambda: app.template_version.set("获取失败"))
                _submit(_tpl_ver)
            if core_needed and root.exists() and app.git_path:
                def _core_ver():
                    try:
                        r = run_hidden([app.git_path, "describe", "--tags", "--abbrev=0"], cwd=str(root), capture_output=True, text=True, timeout=8)
                        if r.returncode != 0:
                            try:
                                target_url = None
                                try:
                                    origin_url = app.version_manager.get_remote_url()
                                    target_url = app.version_manager.compute_proxied_url(origin_url) or origin_url
                                except Exception:
                                    target_url = None
                                fetch_args = [app.git_path, "fetch", "--tags"]
                                if target_url:
                                    fetch_args.append(target_url)
                                run_hidden(fetch_args, cwd=str(root), capture_output=True, text=True, timeout=15)
                                r = run_hidden([app.git_path, "describe", "--tags", "--abbrev=0"], cwd=str(root), capture_output=True, text=True, timeout=8)
                            except Exception:
                                pass
                        if r.returncode == 0:
                            tag = r.stdout.strip()
                            r2 = run_hidden([app.git_path, "rev-parse", "--short", "HEAD"], cwd=str(root), capture_output=True, text=True, timeout=8)
                            commit = r2.stdout.strip() if r2.returncode == 0 else ""
                            def _set():
                                label = ""
                                try:
                                    info = app.services.version.get_latest_stable_kernel(force_refresh=False)
                                    full = info.get("commit") or ""
                                    if full and commit and full.startswith(commit):
                                        label = "（最新稳定版）"
                                except Exception:
                                    label = ""
                                app.comfyui_version.set(f"{tag}（{commit}）{label}")
                            app.root.after(0, _set)
                        else:
                            app.root.after(0, lambda: app.comfyui_version.set("未找到"))
                    except Exception:
                        app.root.after(0, lambda: app.comfyui_version.set("未找到"))
                _submit(_core_ver)
            elif core_needed:
                app.root.after(0, lambda: app.comfyui_version.set("ComfyUI未找到"))
            try:
                executor.shutdown(wait=False)
            except Exception:
                pass
        finally:
            app._version_info_loading = False
    threading.Thread(target=worker, daemon=True).start()