import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from pathlib import Path
from ui.constants import CARD_BG, INTERNAL_HEAD_LABEL_FONT
from ui.helpers import compute_elided_path_text


def build_quick_links_panel(app, container, path=None, rounded_button_cls=None):
    c = app.COLORS

    # 容器：自然高度的自适应网格
    grid = tk.Frame(container, bg=CARD_BG)
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
        try:
            width = max(0, grid.winfo_width())
        except Exception:
            width = 800
        cols = len(app.quick_buttons)
        for i, btn in enumerate(app.quick_buttons):
            btn.grid(row=0, column=i, padx=4, pady=(2, 6), sticky='nsew')
        for ci in range(cols):
            grid.grid_columnconfigure(ci, weight=1, uniform='quick')

    app.root.after(0, _relayout)
