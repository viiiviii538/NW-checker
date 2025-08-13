import requests
from src.dynamic_scan import blacklist_updater


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


def test_update(monkeypatch, tmp_path):
    called = {"fetch": False, "write": False}

    def fake_fetch(url):
        called["fetch"] = True
        return {"x.com"}

    def fake_write(domains, path="data/dns_blacklist.txt"):
        called["write"] = True
        assert domains == {"x.com"}
        assert path == str(tmp_path / "out.txt")

    monkeypatch.setattr(blacklist_updater, "fetch_feed", fake_fetch)
    monkeypatch.setattr(blacklist_updater, "write_blacklist", fake_write)
    blacklist_updater.update("http://feed", output_path=str(tmp_path / "out.txt"))
    assert called["fetch"] and called["write"]
