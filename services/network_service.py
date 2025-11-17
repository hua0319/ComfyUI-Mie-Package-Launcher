from utils import net as NET


class NetworkService:
    def __init__(self, app):
        self.app = app

    def apply_pip_proxy_settings(self):
        NET.apply_pip_proxy_settings(
            self.app.python_exec,
            self.app.pypi_proxy_mode.get(),
            self.app.pypi_proxy_url.get(),
            "",
            logger=self.app.logger,
        )