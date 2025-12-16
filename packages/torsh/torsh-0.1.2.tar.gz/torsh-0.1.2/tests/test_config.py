import importlib
from pathlib import Path


def reload_config(tmp_path: Path):
    import os

    os.environ["TORSH_CONFIG_DIR"] = str(tmp_path)
    import torsh.config as config  # noqa: WPS433

    importlib.reload(config)
    return config


def test_load_config_creates_file(tmp_path):
    config = reload_config(tmp_path)

    cfg = config.load_config()

    assert cfg.paths.config_dir == tmp_path
    assert config.CONFIG_FILE.exists()
    payload = config._load_yaml(config.CONFIG_FILE)  # noqa: SLF001
    assert payload["rpc"]["port"] == cfg.rpc.port
    assert payload["paths"]["config_dir"] == str(tmp_path)


def test_save_config_idempotent(tmp_path):
    config = reload_config(tmp_path)
    cfg = config.load_config()
    cfg.rpc.port = 12345

    config.save_config(cfg)
    first = config.CONFIG_FILE.read_text()

    config.save_config(cfg)
    second = config.CONFIG_FILE.read_text()

    assert first == second
