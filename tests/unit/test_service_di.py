import unittest
from pathlib import Path


class AppStub:
    def __init__(self):
        self.config_manager = type("CM", (), {"config_file": Path("launcher/config.json")})()
        self.logger = None
        self.process_manager = type("PM", (), {})()


class TestServiceDI(unittest.TestCase):
    def test_service_container_from_app(self):
        from services.di import ServiceContainer
        app = AppStub()
        sc = ServiceContainer.from_app(app)
        self.assertTrue(hasattr(sc, 'process'))
        self.assertTrue(hasattr(sc, 'version'))
        self.assertTrue(hasattr(sc, 'config'))
        self.assertTrue(hasattr(sc, 'update'))
        self.assertTrue(hasattr(sc, 'git'))
        self.assertTrue(hasattr(sc, 'network'))
        self.assertTrue(hasattr(sc, 'runtime'))


if __name__ == "__main__":
    unittest.main(verbosity=2)