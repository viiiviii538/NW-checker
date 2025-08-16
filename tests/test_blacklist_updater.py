import requests
from src.dynamic_scan import analyze, blacklist_updater


def test_fetch_feed(monkeypatch):
    class Resp:
        def __init__(self):
            self.text = "a.com\n#comment\nb.org"
            self.headers = {"Content-Type": "text/plain"}

        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda url, timeout=10: Resp())
    assert blacklist_updater.fetch_feed("http://example.com/feed") == {"a.com", "b.org"}


def test_merge_blacklist(tmp_path):
    path = tmp_path / "dns_blacklist.txt"
    path.write_text("# header\nold.com\n")
    blacklist_updater.merge_blacklist({"new.com"}, path=str(path))
    content = path.read_text().splitlines()
    assert "old.com" in content
    assert "new.com" in content


def test_merge_blacklist_error(tmp_path, monkeypatch):
    path = tmp_path / "dns_blacklist.txt"
    path.write_text("original.com\n")

    def fail_replace(src, dst):
        raise OSError("boom")

    monkeypatch.setattr(blacklist_updater.os, "replace", fail_replace)
    try:
        blacklist_updater.merge_blacklist({"new.com"}, path=str(path))
    except OSError:
        pass
    assert path.read_text() == "original.com\n"


def test_update_integration(tmp_path, monkeypatch):
    monkeypatch.setattr(blacklist_updater, "fetch_feed", lambda url: {"x.com"})
    out = tmp_path / "out.txt"
    blacklist_updater.update("http://feed", path=str(out))
    assert "x.com" in out.read_text()


def test_load_blacklist(tmp_path):
    blk = tmp_path / "dns_blacklist.txt"
    blk.write_text("# comment\nfoo.example\nbar.example\n")
    assert analyze.load_blacklist(str(blk)) == {"foo.example", "bar.example"}
