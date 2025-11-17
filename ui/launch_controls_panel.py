import tkinter as tk
from tkinter import ttk
from ui.constants import INTERNAL_HEAD_LABEL_FONT, BODY_FONT, CARD_BG


def build_launch_controls_panel(app, container, rounded_button_cls=None):
    c = app.COLORS
    HEAD_LABEL_FONT = INTERNAL_HEAD_LABEL_FONT
    ROW_GAP = 10
    INLINE_GAP = 26

    form = tk.Frame(container, bg=CARD_BG)
    form.pack(fill=tk.X)
    form.columnconfigure(1, weight=1)

    tk.Label(form, text="模式:", bg=CARD_BG, fg=c["TEXT"],
             font=HEAD_LABEL_FONT) \
        .grid(row=0, column=0, sticky="nw", padx=(0, 14), pady=(0, ROW_GAP))

    mode_frame = tk.Frame(form, bg=CARD_BG)
    mode_frame.grid(row=0, column=1, sticky="w", pady=(0, ROW_GAP))
    ttk.Radiobutton(mode_frame, text="CPU模式",
                    variable=app.compute_mode, value="cpu") \
        .pack(side=tk.LEFT, padx=(0, 20))
    ttk.Radiobutton(mode_frame, text="GPU模式",
                    variable=app.compute_mode, value="gpu") \
        .pack(side=tk.LEFT)

    tk.Label(form, text="选项:", bg=CARD_BG, fg=c["TEXT"],
             font=HEAD_LABEL_FONT) \
        .grid(row=1, column=0, sticky="nw", padx=(0, 14), pady=(0, ROW_GAP))

    checks = tk.Frame(form, bg=CARD_BG)
    checks.grid(row=1, column=1, sticky="w", pady=(0, ROW_GAP))
    tk.Checkbutton(checks, text="快速模式",
                   variable=app.use_fast_mode,
                   bg=CARD_BG, fg=app.COLORS["TEXT"],
                   activebackground=CARD_BG, activeforeground=app.COLORS["TEXT"],
                   selectcolor=CARD_BG) \
        .pack(side=tk.LEFT, padx=(0, INLINE_GAP))
    tk.Checkbutton(checks, text="启用 CORS",
                   variable=app.enable_cors,
                   bg=CARD_BG, fg=app.COLORS["TEXT"],
                   activebackground=CARD_BG, activeforeground=app.COLORS["TEXT"],
                   selectcolor=CARD_BG) \
        .pack(side=tk.LEFT, padx=(0, INLINE_GAP))
    tk.Checkbutton(checks, text="监听 0.0.0.0",
                   variable=app.listen_all,
                   bg=CARD_BG, fg=app.COLORS["TEXT"],
                   activebackground=CARD_BG, activeforeground=app.COLORS["TEXT"],
                   selectcolor=CARD_BG) \
        .pack(side=tk.LEFT)
    tk.Frame(checks, bg=CARD_BG).pack(side=tk.LEFT, expand=True)
    tk.Label(checks, text="额外选项:", bg=CARD_BG, fg=c["TEXT"]) \
        .pack(side=tk.LEFT, padx=(INLINE_GAP, 8))
    ttk.Entry(checks, textvariable=app.extra_launch_args, width=36) \
        .pack(side=tk.LEFT)

    spacer = tk.Frame(form, bg=CARD_BG, width=1, height=1)
    spacer.grid(row=2, column=0)
    port_row = tk.Frame(form, bg=CARD_BG)
    port_row.grid(row=2, column=1, sticky="w", pady=(0, ROW_GAP))

    tk.Label(port_row, text="端口号:", bg=CARD_BG, fg=c["TEXT"], font=BODY_FONT) \
        .pack(side=tk.LEFT, padx=(0, 8))
    ttk.Entry(port_row, textvariable=app.custom_port, width=14) \
        .pack(side=tk.LEFT)

    # —— 网络配置（HF 镜像、GitHub 代理、PyPI 代理） ——
    tk.Label(form, text="网络配置:", bg=CARD_BG, fg=c["TEXT"],
             font=HEAD_LABEL_FONT) \
        .grid(row=3, column=0, sticky="nw", padx=(0, 14), pady=(0, ROW_GAP))

    # 继续复用网络配置面板（已模块化）
    try:
        from ui import network_panel as NETWORK
        NETWORK.build_network_panel(app, form, rounded_button_cls)
    except Exception:
        pass

    tk.Frame(container, bg=CARD_BG, height=2).pack(fill=tk.X)