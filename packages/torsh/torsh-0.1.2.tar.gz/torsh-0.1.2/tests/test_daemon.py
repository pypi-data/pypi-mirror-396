import json

import torsh.daemon as daemon
from torsh.config import AppConfig


def test_write_settings_ports(tmp_path):
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()

    daemon._write_settings_ports(cfg_dir, rpc_port=9091, peer_port=51413)  # noqa: SLF001

    data = json.loads((cfg_dir / "settings.json").read_text())
    assert data["rpc-port"] == 9091
    assert data["peer-port"] == 51413


def test_ensure_transmission_respects_install_flag(monkeypatch):
    cfg = AppConfig()
    cfg.daemon.binary = "nonexistent-daemon"
    cfg.daemon.install_missing = False

    monkeypatch.setattr(daemon.shutil, "which", lambda _: None)

    assert daemon.ensure_transmission_available(cfg) is False
