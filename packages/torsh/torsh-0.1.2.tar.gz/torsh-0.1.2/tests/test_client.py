from types import SimpleNamespace

from torsh.client import TransmissionController
from torsh.config import AppConfig


def test_map_torrent_uses_size_when_done():
    controller = TransmissionController(AppConfig())
    torrent = SimpleNamespace(
        id=1,
        name="example",
        percentDone=None,
        progress=0.0,
        sizeWhenDone=100,
        leftUntilDone=50,
        eta=120,
        rate_download=1024,
        rate_upload=0,
        ratio=0.5,
        total_size=1024,
        added_date=None,
        download_dir="/tmp",
        peers_connected=2,
        peers_sending_to_us=1,
        peers_getting_from_us=0,
        status="downloading",
    )

    view = controller._map_torrent(torrent)  # noqa: SLF001

    assert view.percent_done == 50.0
    assert view.rate_down.endswith("/s")
    assert view.status == "downloading"


def test_map_torrent_fallback_progress():
    controller = TransmissionController(AppConfig())
    torrent = SimpleNamespace(
        id=2,
        name="progress",
        percentDone=0.75,
        eta=-1,
        rate_download=0,
        rate_upload=0,
        ratio=1.2,
        total_size=2048,
        added_date=None,
        download_dir="/tmp",
        peers_connected=0,
        peers_sending_to_us=0,
        peers_getting_from_us=0,
        status="seeding",
    )

    view = controller._map_torrent(torrent)  # noqa: SLF001

    assert view.percent_done == 75.0
    assert view.eta == "∞"


def test_map_torrent_handles_string_numbers():
    controller = TransmissionController(AppConfig())
    torrent = SimpleNamespace(
        id=3,
        name="stringy",
        percentDone=None,
        progress="0.25",
        sizeWhenDone="200",
        leftUntilDone="50",
        eta=None,
        rate_download="2048",
        rate_upload="1024",
        ratio="0.1",
        total_size="4096",
        added_date=None,
        download_dir="/tmp",
        peers_connected="3",
        peers_sending_to_us="2",
        peers_getting_from_us="1",
        status="paused",
    )

    view = controller._map_torrent(torrent)  # noqa: SLF001

    assert view.percent_done == 75.0
    assert view.rate_down.endswith("/s")
    assert view.peers == 3
