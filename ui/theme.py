import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont


def skip_theme() -> bool:
    """检查是否跳过主题切换（用于定位卡顿或兼容性问题）。"""
    try:
        env = (os.environ.get('COMFYUI_LAUNCHER_SKIP_THEME') or '').strip().lower() in ('1', 'true', 'yes', 'on')
    except Exception:
        env = False
    file_flag = False
    try:
        file_flag = (Path.cwd() / 'launcher' / 'skip_theme').exists()
    except Exception:
        file_flag = False
    return bool(env or file_flag)


def create_style(logger=None) -> ttk.Style | None:
    """安全创建 ttk.Style，并记录日志。"""
    try:
        if logger:
            try:
                logger.info("样式阶段: 创建 ttk.Style()")
            except Exception:
                pass
        style = ttk.Style()
        if logger:
            try:
                logger.info("样式阶段: ttk.Style 创建成功，当前主题=%s", style.theme_use())
            except Exception:
                pass
        return style
    except Exception:
        if logger:
            try:
                logger.exception("创建 ttk.Style 失败，使用默认主题")
            except Exception:
                pass
        return None


def apply_theme(style: ttk.Style, logger=None) -> None:
    """选择主题：优先使用 'clam'；不可用则保留默认主题。"""
    if style is None:
        return
    try:
        if logger:
            try:
                logger.info("样式阶段: 获取可用主题列表")
            except Exception:
                pass
        themes = list(style.theme_names())
        if logger:
            try:
                logger.info("样式阶段: 可用主题=%s", ", ".join(themes))
            except Exception:
                pass
        if skip_theme():
            if logger:
                try:
                    logger.info("样式阶段: 跳过主题切换 (skip_theme=True)，当前主题=%s", style.theme_use())
                except Exception:
                    pass
            return
        if 'clam' in themes:
            try:
                style.theme_use('clam')
                if logger:
                    try:
                        logger.info("样式阶段: 切换到 clam 主题成功，当前主题=%s", style.theme_use())
                    except Exception:
                        pass
            except Exception:
                if logger:
                    try:
                        logger.warning("切换到 'clam' 主题失败，保留默认主题")
                    except Exception:
                        pass
    except Exception:
        pass


def configure_default_font(root: tk.Tk, logger=None) -> None:
    """配置全局默认字体。"""
    try:
        if logger:
            try:
                logger.info("样式阶段: 配置 TkDefaultFont")
            except Exception:
                pass
        base = tkfont.nametofont("TkDefaultFont")
        base.configure(family="Microsoft YaHei", size=11)
        root.option_add("*Font", "TkDefaultFont")
        if logger:
            try:
                logger.info("样式阶段: TkDefaultFont 配置完成")
            except Exception:
                pass
    except Exception:
        pass


def configure_styles(style: ttk.Style, colors: dict, logger=None) -> None:
    """根据颜色主题配置各组件样式与状态映射。"""
    if style is None:
        return
    try:
        if logger:
            try:
                logger.info("样式阶段: 执行样式配置与映射")
            except Exception:
                pass
        c = colors
        s = style
        s.configure(".", background=c["BG"], foreground=c["TEXT"]) 
        s.configure('TEntry', fieldbackground=c["BG"], bordercolor=c["BORDER"], lightcolor=c["ACCENT"]) 
        s.map('TEntry', bordercolor=[('focus', c["ACCENT"])])
        s.configure('TCombobox', fieldbackground=c["BG"], bordercolor=c["BORDER"]) 
        s.map('TCombobox', bordercolor=[('focus', c["ACCENT"])])

        s.configure('Secondary.TButton',
                    background=c["BG"], foreground=c["TEXT"],
                    padding=(8, 4),
                    borderwidth=1,
                    bordercolor=c["BORDER"],
                    font=("Microsoft YaHei", 10))
        s.map('Secondary.TButton',
              background=[('active', '#F4F6F8'), ('pressed', '#EDF0F3')],
              bordercolor=[('focus', c["ACCENT"])])

        s.configure('Accent.TButton',
                    background=c["ACCENT"],
                    foreground="#FFFFFF",
                    padding=(10, 6),
                    borderwidth=0,
                    font=("Microsoft YaHei", 11, 'bold'))
        s.map('Accent.TButton',
              background=[('active', c["ACCENT_HOVER"]), ('pressed', c["ACCENT_ACTIVE"])],
              foreground=[('disabled', '#FFFFFFAA')])

        s.configure('Nav.TButton', background=c["SIDEBAR_BG"], foreground="#FFFFFF",
                    padding=(14, 10), anchor='w', borderwidth=0, font=("Microsoft YaHei", 11))
        s.map('Nav.TButton', background=[('active', c["SIDEBAR_ACTIVE"])])
        s.configure('NavSelected.TButton', background=c["SIDEBAR_ACTIVE"],
                    foreground="#FFFFFF", padding=(14, 10), anchor='w',
                    borderwidth=0, font=("Microsoft YaHei", 11, 'bold'))
        if logger:
            try:
                logger.info("窗口样式设置完成")
            except Exception:
                pass
    except Exception:
        # 兜底：记录异常但不要让启动器崩溃
        if logger:
            try:
                logger.exception("样式配置阶段发生异常，继续使用默认外观")
            except Exception:
                pass