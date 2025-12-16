from torsh.config import AppConfig
from torsh.ui.app import TorshApp


def test_app_initializes_with_defaults():
    app = TorshApp(AppConfig())
    assert app.refresh_interval > 0
    assert app._files_cache == {}
