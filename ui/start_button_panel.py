import tkinter as tk


def build_start_button_panel(app, parent, big_button_cls=None):
    """
    构建右侧“一键启动”大按钮区域。
    从主文件抽取，保持原有布局与事件绑定一致：
    - 使用传入的 big_button_cls（建议为 BigLaunchButton）以保持视觉风格；
    - 绑定指令至 app.toggle_comfyui；
    - 将实例赋值到 app.big_btn，供状态切换使用。
    """
    # 回退：若未传入类，使用一个简易按钮以保障可用性
    def _fallback_button(parent_, text, size, color, hover, active, command):
        btn = tk.Button(parent_, text=text, command=command)
        return btn

    ButtonCls = big_button_cls or _fallback_button

    # 构建按钮（参数与原实现保持一致）
    btn = ButtonCls(
        parent,
        text="一键启动",
        size=170,
        color=app.COLORS.get("ACCENT", "#2F6EF6"),
        hover=app.COLORS.get("ACCENT_HOVER", "#2760DB"),
        active=app.COLORS.get("ACCENT_ACTIVE", "#1F52BE"),
        command=app.toggle_comfyui,
    )

    # 原排版逻辑：居中或顶部对齐
    if getattr(app, 'LAUNCH_BUTTON_CENTER', False):
        try:
            btn.pack(expand=True)
        except Exception:
            # 兼容 tk.Button 回退
            btn.pack()
    else:
        try:
            btn.pack(anchor='n', pady=4)
        except Exception:
            btn.pack()

    # 暴露到 app 上供状态管理（start/stop 文案与样式）
    try:
        app.big_btn = btn
    except Exception:
        pass

    return btn