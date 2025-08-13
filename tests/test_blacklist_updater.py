import requests
from src.dynamic_scan.blacklist_updater import fetch_feed, write_blacklist, main


def test_fetch_feed_json(monkeypatch):
    class Resp:
        def __init__(self):
            self.text = '{"domains": ["a.com", "b.org"]}'
            self.headers = {"Content-Type": "application/json"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda url, timeout: Resp())
    assert fetch_feed("http://example.com/feed.json") == {"a.com", "b.org"}


def test_write_blacklist(tmp_path):
    path = tmp_path / "dns_blacklist.txt"
    path.write_text("# header\nold.com\n")
    write_blacklist({"new.com"}, path=str(path))
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
    assert fetch_feed("http://example.com/feed.csv") == {"c.com", "d.org"}


def test_fetch_feed_file(tmp_path):
    p = tmp_path / "feed.txt"
    p.write_text("e.com\nf.org\n")
    assert fetch_feed(str(p)) == {"e.com", "f.org"}


def test_main_updates_blacklist(tmp_path):
    feed1 = tmp_path / "feed1.csv"
    feed1.write_text("a.com\n")
    feed2 = tmp_path / "feed2.json"
    feed2.write_text("[\"b.org\"]")

    out = tmp_path / "dns_blacklist.txt"
    main([str(feed1), str(feed2), "--output", str(out)])

    lines = out.read_text().splitlines()
    assert "a.com" in lines
    assert "b.org" in lines
