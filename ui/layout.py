import tkinter as tk
from tkinter import ttk
from pathlib import Path
from ui.custom_widges import BigLaunchButton, RoundedButton, SectionCard
from ui import version_panel as VERSION
from ui import quick_links_panel as QUICK
from ui import launch_controls_panel as LAUNCH
from ui import about_tab as ABOUT
from ui import comfyui_tab as COMFY
from ui import start_button_panel as START
from ui import launcher_about_tab as LAUNCHER_ABOUT
from ui import external_models_tab as EXT_MODELS
from ui.constants import COLORS, LAUNCH_BUTTON_CENTER, SIDEBAR_DIVIDER_SHADOW, SIDEBAR_DIVIDER_COLOR, SHADOW_WIDTH, LEFT_RIGHT_GAP, CARD_BORDER_COLOR, CARD_BG, SECTION_TITLE_FONT, INTERNAL_HEAD_LABEL_FONT, BODY_FONT

def build_layout(app):
    c = COLORS
    app.main_container = tk.Frame(app.root, bg=c["BG"])
    app.main_container.pack(fill=tk.BOTH, expand=True)
    app.sidebar = tk.Frame(app.main_container, width=176, bg=c["SIDEBAR_BG"])
    app.sidebar.pack(side=tk.LEFT, fill=tk.Y)
    app.sidebar.pack_propagate(False)
    sidebar_header = tk.Frame(app.sidebar, bg=c["SIDEBAR_BG"])
    sidebar_header.pack(fill=tk.X, pady=(18, 12))
    tk.Label(sidebar_header, text="ComfyUI\n启动器", bg=c["SIDEBAR_BG"], fg="#FFFFFF", font=("Microsoft YaHei", 18, 'bold'), anchor='center', justify='center').pack(fill=tk.X)
    tk.Label(sidebar_header, text="by 黎黎原上咩", bg=c["SIDEBAR_BG"], fg=c.get("TEXT_MUTED", "#A0A4AA"), font=("Microsoft YaHei", 11), anchor='center', justify='center').pack(fill=tk.X, pady=(4, 0))
    app.nav_buttons = {}
    for key, label in [("launch", "🚀 启动与更新"), ("version", "🧬 内核版本管理"), ("external_models", "📦 外置模型库管理"), ("about", "👤 关于我"), ("comfyui", "📚 关于ComfyUI"), ("about_launcher", "🧰 关于启动器")]:
        btn = ttk.Button(app.sidebar, text=label, style='Nav.TButton', command=lambda k=key: app.select_tab(k))
        btn.pack(fill=tk.X, padx=8, pady=3)
        app.nav_buttons[key] = btn
    if True:
        if SIDEBAR_DIVIDER_SHADOW:
            shadow_canvas = tk.Canvas(app.main_container, width=1 + SHADOW_WIDTH, highlightthickness=0, bd=0, bg=c["BG"])
            shadow_canvas.pack(side=tk.LEFT, fill=tk.Y)
            shadow_canvas.create_rectangle(0, 0, 1, 9999, fill=SIDEBAR_DIVIDER_COLOR, outline="")
        else:
            divider = tk.Frame(app.main_container, width=1, bg=SIDEBAR_DIVIDER_COLOR)
            divider.pack(side=tk.LEFT, fill=tk.Y)
    app.content_area = tk.Frame(app.main_container, bg=c["BG"])
    app.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    app.notebook = ttk.Notebook(app.content_area, style='Hidden.TNotebook')
    app.notebook.pack(fill=tk.BOTH, expand=True)
    app.tab_frames = {
        "launch": tk.Frame(app.notebook, bg=c["BG"]),
        "version": tk.Frame(app.notebook, bg=c["BG"]),
        "external_models": tk.Frame(app.notebook, bg=c["BG"]),
        "comfyui": tk.Frame(app.notebook, bg=c["BG"]),
        "about": tk.Frame(app.notebook, bg=c["BG"]),
        "about_launcher": tk.Frame(app.notebook, bg=c["BG"]),
    }
    app.notebook.add(app.tab_frames["launch"], text="启动与更新")
    app.notebook.add(app.tab_frames["version"], text="内核版本管理")
    app.notebook.add(app.tab_frames["external_models"], text="外置模型库管理")
    app.notebook.add(app.tab_frames["about"], text="关于我")
    app.notebook.add(app.tab_frames["comfyui"], text="关于 ComfyUI")
    app.notebook.add(app.tab_frames["about_launcher"], text="关于启动器")
    build_launch_tab(app, app.tab_frames["launch"])
    build_version_tab(app, app.tab_frames["version"])
    EXT_MODELS.build_external_models_tab(app, app.tab_frames["external_models"])
    ABOUT.build_about_tab(app, app.tab_frames["about"])
    LAUNCHER_ABOUT.build_about_launcher(app, app.tab_frames["about_launcher"])
    COMFY.build_about_comfyui(app, app.tab_frames["comfyui"])
    app.notebook.select(app.notebook.tabs()[0])
    app.current_tab_name = "launch"
    

def build_launch_tab(app, parent):
    c = app.COLORS
    header = tk.Frame(parent, bg=c["BG"]) 
    header.pack(fill=tk.X, pady=(6, 6))
    launch_card = SectionCard(parent, "启动控制", icon="⚙", border_color=CARD_BORDER_COLOR, bg=CARD_BG, title_font=SECTION_TITLE_FONT, padding=(20, 16, 20, 18))
    launch_card.pack(fill=tk.X, pady=(0, 16))
    body = launch_card.get_body()
    container = tk.Frame(body, bg=CARD_BG)
    container.pack(fill=tk.X)
    container.columnconfigure(0, weight=3)
    container.columnconfigure(1, weight=0)
    container.columnconfigure(2, weight=0)
    if LAUNCH_BUTTON_CENTER:
        container.rowconfigure(0, weight=1)
    left = tk.Frame(container, bg=CARD_BG)
    left.grid(row=0, column=0, sticky="nsew")
    sep = tk.Frame(container, bg=SIDEBAR_DIVIDER_COLOR, width=1)
    sep.grid(row=0, column=1, sticky="ns", padx=(LEFT_RIGHT_GAP // 2, LEFT_RIGHT_GAP // 2))
    right = tk.Frame(container, bg=CARD_BG)
    right.grid(row=0, column=2, sticky="n")
    if LAUNCH_BUTTON_CENTER:
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
    LAUNCH.build_launch_controls_panel(app, left, RoundedButton)
    START.build_start_button_panel(app, right, BigLaunchButton)
    
    # 路径配置区域
    path_card = SectionCard(parent, "路径配置", icon="📁", border_color=CARD_BORDER_COLOR, bg=CARD_BG, title_font=SECTION_TITLE_FONT, padding=(16, 12, 16, 12))
    path_card.pack(fill=tk.X, pady=(0, 16))
    build_path_config_panel(app, path_card.get_body(), RoundedButton)
    
    version_card = SectionCard(parent, "版本与更新", icon="🔄", border_color=CARD_BORDER_COLOR, bg=CARD_BG, title_font=SECTION_TITLE_FONT, padding=(16, 12, 16, 12))
    version_card.pack(fill=tk.X, pady=(0, 10))
    VERSION.build_version_panel(app, version_card.get_body(), RoundedButton)
    quick_card = SectionCard(parent, "快捷目录", icon="🗂", border_color=CARD_BORDER_COLOR, bg=CARD_BG, title_font=SECTION_TITLE_FONT, padding=(14, 8, 14, 10), inner_gap=10)
    quick_card.pack(fill=tk.X, pady=(0, 10))
    try:
        from utils import paths as PATHS
        _path = str(PATHS.get_comfy_root(app.config.get("paths", {})))
    except Exception:
        _path = str(Path("ComfyUI").resolve())
    QUICK.build_quick_links_panel(app, quick_card.get_body(), path=_path, rounded_button_cls=RoundedButton)
    app.get_version_info()

def build_path_config_panel(app, parent, button_class):
    """构建路径配置面板"""
    from tkinter import filedialog, messagebox
    from pathlib import Path
    from utils import paths as PATHS
    
    c = app.COLORS
    
    # 当前路径显示框架
    path_frame = tk.Frame(parent, bg=CARD_BG)
    path_frame.pack(fill=tk.X, pady=(0, 8))
    
    # ComfyUI根目录路径
    comfyui_path_frame = tk.Frame(path_frame, bg=CARD_BG)
    comfyui_path_frame.pack(fill=tk.X, pady=(0, 8))
    
    tk.Label(comfyui_path_frame, text="ComfyUI根目录:", bg=CARD_BG, fg=c["TEXT"], 
             font=INTERNAL_HEAD_LABEL_FONT).pack(side=tk.LEFT, padx=(0, 8))
    
    app.comfyui_path_label = tk.Label(comfyui_path_frame, text="", bg=CARD_BG, fg=c["TEXT"], 
                                       font=BODY_FONT, anchor="w")
    app.comfyui_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def update_comfyui_path_display():
        """更新ComfyUI路径显示"""
        try:
            comfy_root = PATHS.get_comfy_root(app.config.get("paths", {}))
            app.comfyui_path_label.config(text=str(comfy_root))
        except Exception:
            app.comfyui_path_label.config(text="未设置")
    
    # Python路径框架
    python_path_frame = tk.Frame(path_frame, bg=CARD_BG)
    python_path_frame.pack(fill=tk.X, pady=(8, 0))
    
    tk.Label(python_path_frame, text="Python路径:", bg=CARD_BG, fg=c["TEXT"], 
             font=INTERNAL_HEAD_LABEL_FONT).pack(side=tk.LEFT, padx=(0, 8))
    
    app.python_path_label = tk.Label(python_path_frame, bg=CARD_BG, fg=c["TEXT"], 
                                      font=BODY_FONT, anchor="w")
    app.python_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def update_python_path_display():
        """更新Python路径显示（优先自定义；否则按 ComfyUI 根目录的 python_embeded/python.exe 检测）"""
        try:
            from pathlib import Path as _P
            # 优先使用用户自定义配置
            cfg_py = app.config.get("paths", {}).get("python_path")
            if cfg_py:
                p = _P(cfg_py)
                if p.exists():
                    app.python_path_label.config(text=str(p))
                    return
            # 回退到默认逻辑：ComfyUI 根目录下的 python_embeded/python.exe
            comfy_root = PATHS.get_comfy_root(app.config.get("paths", {}))
            default_py = PATHS.resolve_python_exec(comfy_root, "python_embeded/python.exe")
            if _P(default_py).exists():
                app.python_path_label.config(text=str(default_py))
            else:
                app.python_path_label.config(text="未找到")
        except Exception:
            app.python_path_label.config(text="未找到")
    
    def reset_comfyui_root():
        """重设ComfyUI根目录"""
        try:
            current_root = app.config.get("paths", {}).get("comfyui_root", "")
            initial_dir = current_root if current_root and Path(current_root).exists() else None
            
            selected = filedialog.askdirectory(
                title="请选择ComfyUI根目录",
                initialdir=initial_dir
            )
            
            if selected:
                selected_path = Path(selected).resolve()
                comfyui_path = selected_path / "ComfyUI"
                
                # 验证路径
                if PATHS.validate_comfy_root(comfyui_path):
                    if getattr(app, 'services', None):
                        app.services.config.set("paths.comfyui_root", str(selected_path))
                        # 同时更新 python_path，因为 resolve_python_exec 依赖 root
                        py_exec = PATHS.resolve_python_exec(comfyui_path, app.config["paths"].get("python_path", "python_embeded/python.exe"))
                        app.python_exec = str(py_exec)
                        app.services.config.set("paths.python_path", app.python_exec)
                        
                        app.services.config.save()
                        app.config = app.services.config.get_config()
                    else:
                        app.config.setdefault("paths", {})["comfyui_root"] = str(selected_path)
                        py_exec = PATHS.resolve_python_exec(comfyui_path, app.config["paths"].get("python_path", "python_embeded/python.exe"))
                        app.python_exec = str(py_exec)
                        app.config["paths"]["python_path"] = app.python_exec
                        app.config_manager.save_config(app.config)
                    
                    # 更新显示
                    update_comfyui_path_display()
                    update_python_path_display()
                    
                    # 重新初始化版本管理器
                    app.version_manager = app.version_manager.__class__(
                        app,
                        str(comfyui_path),
                        app.config["paths"]["python_path"]
                    )
                    
                    # 触发版本信息刷新
                    try:
                        app.get_version_info()
                    except Exception:
                        pass
                    
                    messagebox.showinfo("成功", "ComfyUI根目录已更新")
                else:
                    messagebox.showerror("错误", "所选目录似乎不是有效的ComfyUI根目录（缺少main.py或.git）")
        except Exception as e:
            messagebox.showerror("错误", f"设置ComfyUI根目录失败: {str(e)}")
    
    def set_custom_python_path():
        """设置自定义Python路径"""
        try:
            current_python = app.config.get("paths", {}).get("python_path", "")
            initial_dir = str(Path(current_python).parent) if current_python and Path(current_python).exists() else None
            
            selected = filedialog.askopenfilename(
                title="请选择Python可执行文件",
                filetypes=[("Python可执行文件", "python.exe;python"), ("所有文件", "*.*")],
                initialdir=initial_dir
            )
            
            if selected:
                selected_path = Path(selected).resolve()
                
                # 验证是否为有效的Python可执行文件
                if selected_path.exists() and selected_path.is_file():
                    if getattr(app, 'services', None):
                        app.services.config.set("paths.python_path", str(selected_path))
                        app.services.config.save()
                        app.config = app.services.config.get_config()
                    else:
                        app.config.setdefault("paths", {})["python_path"] = str(selected_path)
                        app.config_manager.save_config(app.config)
                    
                    app.python_exec = str(selected_path)
                    
                    # 更新显示
                    update_python_path_display()
                    
                    # 重新初始化版本管理器
                    comfyui_path = PATHS.get_comfy_root(app.config.get("paths", {}))
                    app.version_manager = app.version_manager.__class__(
                        app,
                        str(comfyui_path),
                        app.config["paths"]["python_path"]
                    )
                    
                    # 触发版本信息刷新（仅Python相关）
                    try:
                        app.get_version_info(scope="python_related")
                    except Exception:
                        pass
                    
                    messagebox.showinfo("成功", "Python路径已更新")
                else:
                    messagebox.showerror("错误", "所选文件不是有效的Python可执行文件")
        except Exception as e:
            messagebox.showerror("错误", f"设置Python路径失败: {str(e)}")
    
    # 行内按钮：与当前行在同一行显示
    def _mk_btn(parent, cmd):
        return button_class(
            parent,
            text="重设",
            width=120,
            height=36,
            color=app.COLORS["ACCENT"],
            hover=app.COLORS["ACCENT_HOVER"],
            active=app.COLORS["ACCENT_ACTIVE"],
            radius=10,
            command=cmd,
            font=("Microsoft YaHei", 11, "bold"),
        )
    _mk_btn(comfyui_path_frame, reset_comfyui_root).pack(side=tk.RIGHT, padx=(8, 0))
    _mk_btn(python_path_frame, set_custom_python_path).pack(side=tk.RIGHT, padx=(8, 0))
    
    # 初始化显示
    update_comfyui_path_display()
    update_python_path_display()

def build_version_tab(app, parent):
    app.version_container = tk.Frame(parent, bg=app.COLORS["BG"]) 
    app.version_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
