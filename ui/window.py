import os
import time
from tkinter import ttk
from ui import assets_helper as ASSETS
from ui import theme as THEME
from ui.constants import COLORS

def setup_window(app):
    try:
        app.root.title("ComfyUI启动器 - 黎黎原上咩")
        # 增加默认高度以适应新增的路径配置区域
        # 尝试使用屏幕高度的 85% 或默认 1040，取较小值以防溢出
        screen_height = app.root.winfo_screenheight()
        target_height = 1020
        if screen_height < 1150:
            target_height = min(1020, screen_height - 60)
        
        app.root.geometry(f"1250x{target_height}")
        app.root.minsize(1100, 700)
        try:
            if os.name == 'nt':
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ComfyUILauncher")
        except Exception:
            pass
        try:
            ASSETS.apply_window_icons(app.root, getattr(app, 'logger', None))
        except Exception:
            pass
        app.style = THEME.create_style(logger=getattr(app, 'logger', None))
        if not app.style:
            return
        THEME.apply_theme(app.style, logger=getattr(app, 'logger', None))
        try:
            app.style.layout('Hidden.TNotebook.Tab', [])
        except Exception:
            pass
        try:
            app.root.configure(bg=COLORS.get("BG", "#FFFFFF"))
        except Exception:
            pass
        
        THEME.configure_default_font(app.root, logger=getattr(app, 'logger', None))
        THEME.configure_styles(app.style, COLORS, logger=getattr(app, 'logger', None))
        try:
            def _on_cfg(_=None):
                try:
                    w = app.root.winfo_width()
                    h = app.root.winfo_height()
                except Exception:
                    w = None; h = None
                try:
                    last = getattr(app, '_last_size', None)
                    if last != (w, h):
                        app._last_size = (w, h)
                        app._last_resize_ts = time.perf_counter()
                        app._is_resizing = True
                        tid = getattr(app, '_resizing_reset_timer', None)
                        if tid:
                            app.root.after_cancel(tid)
                        app._resizing_reset_timer = app.root.after(120, lambda: setattr(app, '_is_resizing', False))
                except Exception:
                    pass
            app.root.bind("<Configure>", _on_cfg)
        except Exception:
            pass
    except Exception:
        try:
            app.logger.exception("setup_window 阶段发生异常，继续使用默认外观")
        except Exception:
            pass
