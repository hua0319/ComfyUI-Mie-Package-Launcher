import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from pathlib import Path


def build_quick_links_panel(app, container, path=None, rounded_button_cls=None):
    c = app.COLORS
    # 顶部一排：左侧路径，右侧“重设ComfyUI根目录”按钮
    top_bar = tk.Frame(container, bg=app.CARD_BG)
    top_bar.pack(fill=tk.X, padx=(4, 0), pady=(0, 6))
    if path:
        # 左侧：路径标题与值并排
        left_path = tk.Frame(top_bar, bg=app.CARD_BG)
        left_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        app.path_label_title = tk.Label(
            left_path,
            text="路径:",
            bg=app.CARD_BG, fg=c["TEXT"],
            font=app.INTERNAL_HEAD_LABEL_FONT
        )
        app.path_label_title.pack(side=tk.LEFT, padx=(0, 8))
        try:
            path_resolved = str(Path(path).resolve())
        except Exception:
            path_resolved = str(path)
        # 保存完整路径用于后续截断显示
        app._path_full_text = path_resolved
        app.path_value_var = tk.StringVar(value=path_resolved)
        app.path_value_label = tk.Label(
            left_path,
            textvariable=app.path_value_var,
            bg=app.CARD_BG, fg=c["TEXT"]
        )
        app.path_value_label.pack(side=tk.LEFT)

        # 记录布局引用，便于根据可用宽度动态截断
        app._path_top_bar = top_bar
        try:
            app._path_label_font = tkfont.nametofont(app.path_value_label.cget("font"))
        except Exception:
            try:
                app._path_label_font = tkfont.nametofont("TkDefaultFont")
            except Exception:
                app._path_label_font = None

        # 将“重设ComfyUI根目录”按钮紧随具体路径值右侧
        if rounded_button_cls is not None:
            app.reset_root_btn = rounded_button_cls(
                left_path,
                text="重设ComfyUI根目录",
                width=160,
                height=36,
                color=app.COLORS["ACCENT"],
                hover=app.COLORS["ACCENT_HOVER"],
                active=app.COLORS["ACCENT_ACTIVE"],
                radius=10,
                font=("Microsoft YaHei", 11),
                command=app.reset_comfyui_path,
            )
        else:
            app.reset_root_btn = ttk.Button(left_path, text="重设ComfyUI根目录", command=app.reset_comfyui_path)
        app.reset_root_btn.pack(side=tk.LEFT, padx=(12, 0))

        # 绑定尺寸变化事件以动态更新截断文本
        def _on_resize(_evt=None):
            try:
                app._update_path_label_elide()
            except Exception:
                pass
        top_bar.bind('<Configure>', _on_resize)
        app.root.after(0, _on_resize)
    else:
        # 若无路径信息，保持按钮在顶栏右侧作为回退布局
        if rounded_button_cls is not None:
            app.reset_root_btn = rounded_button_cls(
                top_bar,
                text="重设ComfyUI根目录",
                width=160,
                height=36,
                color=app.COLORS["ACCENT"],
                hover=app.COLORS["ACCENT_HOVER"],
                active=app.COLORS["ACCENT_ACTIVE"],
                radius=10,
                font=("Microsoft YaHei", 11),
                command=app.reset_comfyui_path,
            )
        else:
            app.reset_root_btn = ttk.Button(top_bar, text="重设ComfyUI根目录", command=app.reset_comfyui_path)
        app.reset_root_btn.pack(side=tk.RIGHT)

    # 容器：自然高度的自适应网格
    grid = tk.Frame(container, bg=app.CARD_BG)
    grid.pack(fill=tk.X)
    app.quick_grid_frame = grid

    app.quick_buttons = []
    for txt, cmd in [
        ("根目录", app.open_root_dir),
        ("日志文件", app.open_logs_dir),
        ("输入目录", app.open_input_dir),
        ("输出目录", app.open_output_dir),
        ("插件目录", app.open_plugins_dir),
        ("工作流目录", app.open_workflows_dir),
    ]:
        btn = ttk.Button(grid, text=txt, style='Secondary.TButton', command=cmd)
        app.quick_buttons.append(btn)

    def _relayout(_evt=None):
        # 单行网格布局
        try:
            width = max(0, grid.winfo_width())
        except Exception:
            width = 800
        cols = len(app.quick_buttons)
        for i, btn in enumerate(app.quick_buttons):
            btn.grid(row=0, column=i, padx=4, pady=(2, 6), sticky='nsew')
        for ci in range(cols):
            grid.grid_columnconfigure(ci, weight=1, uniform='quick')

    grid.bind('<Configure>', _relayout)
    app.root.after(0, _relayout)