from services.interfaces import IProcessService


class ProcessService(IProcessService):
    def __init__(self, app):
        self.app = app
        self.pm = getattr(app, 'process_manager')

    def toggle(self) -> None:
        self.pm.toggle_comfyui()

    def start(self) -> None:
        self.pm.start_comfyui()

    def stop(self) -> bool:
        return self.pm.stop_comfyui()

    def refresh_status(self) -> None:
        try:
            self.pm.refresh_running_status_async()
        except Exception:
            # 回退到同步刷新
            self.pm._refresh_running_status()

    def monitor(self) -> None:
        self.pm.monitor_process()