from concurrent.futures import ThreadPoolExecutor


class StartupService:
    def __init__(self, app):
        self.app = app

    def start_all(self):
        try:
            ex = ThreadPoolExecutor(max_workers=2)
        except Exception:
            ex = None
        # 版本信息（后台刷新，界面先显示“获取中…”）
        def _version_task():
            try:
                from core.version_service import refresh_version_info
                refresh_version_info(self.app, scope="all")
            except Exception:
                pass
        # 公告检查（异步弹窗）
        def _announcement_task():
            try:
                if getattr(self.app, 'services', None) and getattr(self.app.services, 'announcement', None):
                    self.app.services.announcement.show_if_available()
            except Exception:
                pass
        # 其他可扩展任务占位
        tasks = [_version_task, _announcement_task]
        for t in tasks:
            try:
                if ex:
                    ex.submit(t)
                else:
                    import threading
                    threading.Thread(target=t, daemon=True).start()
            except Exception:
                pass
