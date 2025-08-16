from src.dynamic_scan import analyze, blacklist_updater


def test_load_blacklist_reads_domains(tmp_path):
    blk = tmp_path / "dns_blacklist.txt"
    blk.write_text("# comment\nfoo.example\nbar.example\n")
    assert analyze.load_blacklist(str(blk)) == {"foo.example", "bar.example"}


def test_merge_blacklist_deduplicates(tmp_path):
    path = tmp_path / "dns_blacklist.txt"
    path.write_text("old.com\n")
    blacklist_updater.merge_blacklist({"old.com", "new.com"}, path=str(path))
    lines = path.read_text().splitlines()
    assert lines.count("old.com") == 1
    assert "new.com" in lines


def test_fetch_feed_parses_json(monkeypatch):
    class FakeResp:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def raise_for_status(self):
            pass

        def json(self):
            return {"domains": ["a.com", "b.com"]}

    monkeypatch.setattr(blacklist_updater.requests, "get", lambda url, timeout=10: FakeResp())
    assert blacklist_updater.fetch_feed("http://example.com/feed.json") == {"a.com", "b.com"}


def test_fetch_feed_parses_text(monkeypatch):
    class FakeResp:
        status_code = 200
        headers = {"Content-Type": "text/plain"}
        text = "#c\n d.com \n"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(blacklist_updater.requests, "get", lambda url, timeout=10: FakeResp())
    assert blacklist_updater.fetch_feed("http://example.com/feed.txt") == {"d.com"}


def test_update_fetches_and_writes(monkeypatch, tmp_path):
    blk = tmp_path / "dns_blacklist.txt"
    monkeypatch.setattr(
        blacklist_updater,
        "fetch_feed",
        lambda url: {"foo.example"},
    )
    blacklist_updater.update("http://feed", path=str(blk))
    assert "foo.example" in blk.read_text()
