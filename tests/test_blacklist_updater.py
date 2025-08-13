import requests
from src.dynamic_scan import analyze, blacklist_updater


def test_fetch_feed_json(monkeypatch):
    class Resp:
        def __init__(self):
            self.text = '{"domains": ["a.com", "b.org"]}'
            self.headers = {"Content-Type": "application/json"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda url, timeout: Resp())
    assert blacklist_updater.fetch_feed("http://example.com/feed.json") == {"a.com", "b.org"}


def test_write_blacklist(tmp_path):
    path = tmp_path / "dns_blacklist.txt"
    path.write_text("# header\nold.com\n")
    blacklist_updater.write_blacklist({"new.com"}, path=str(path))
    content = path.read_text().splitlines()
    assert "old.com" in content
    assert "new.com" in content

def test_fetch_feed_csv(monkeypatch):
    class Resp:
        def __init__(self):
            self.text = "c.com\n#comment\nd.org"
            self.headers = {"Content-Type": "text/csv"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda url, timeout: Resp())
    assert blacklist_updater.fetch_feed("http://example.com/feed.csv") == {"c.com", "d.org"}


def test_load_blacklist(tmp_path):
    blk = tmp_path / "dns_blacklist.txt"
    blk.write_text("# comment\nfoo.example\nbar.example\n")
    assert analyze.load_blacklist(str(blk)) == {"foo.example", "bar.example"}


def test_update_integration(monkeypatch, tmp_path):
    class Resp:
        def __init__(self):
            self.text = "x.com\n#c\ny.org"
            self.headers = {"Content-Type": "text/plain"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda url, timeout: Resp())
    out = tmp_path / "out.txt"
    blacklist_updater.update("http://feed", output_path=str(out))
    lines = out.read_text().splitlines()
    assert "x.com" in lines and "y.org" in lines
    assert lines[0].startswith("#")


def test_fetch_feed_error(monkeypatch):
    def fake_get(url, timeout):  # pragma: no cover - 例外発生の確認用
        raise requests.RequestException("boom")

    monkeypatch.setattr(requests, "get", fake_get)
    assert blacklist_updater.fetch_feed("http://example.com/feed") == set()


def test_write_blacklist_no_domains(tmp_path):
    path = tmp_path / "dns_blacklist.txt"
    blacklist_updater.write_blacklist(set(), path=str(path))
    assert not path.exists()
