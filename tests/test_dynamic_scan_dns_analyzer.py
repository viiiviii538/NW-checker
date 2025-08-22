import pytest
from src.dynamic_scan import dns_analyzer


def test_load_blacklist_ignores_comments_and_blank_lines(tmp_path):
    file = tmp_path / "bl.txt"
    file.write_text("foo.example\n# comment\n\nBAR.example\n")
    bl = dns_analyzer.load_blacklist(str(file))
    assert bl == {"foo.example", "bar.example"}


def test_reverse_dns_lookup_caches_and_reuses_result():
    dns_analyzer._dns_cache.clear()

    def fake_gethostbyaddr(ip):
        return ("Host.Example.", [], [])

    host = dns_analyzer.reverse_dns_lookup("1.1.1.1", gethostbyaddr=fake_gethostbyaddr)
    assert host == "host.example"
    assert dns_analyzer._dns_cache["1.1.1.1"] == "host.example"

    def failing(_):
        raise RuntimeError("network down")

    # キャッシュされた結果が返るため例外は表に出ない
    cached = dns_analyzer.reverse_dns_lookup("1.1.1.1", gethostbyaddr=failing)
    assert cached == "host.example"


def test_reverse_dns_lookup_failure_without_cache():
    dns_analyzer._dns_cache.clear()

    def failing(_):
        raise RuntimeError("network down")

    assert dns_analyzer.reverse_dns_lookup("2.2.2.2", gethostbyaddr=failing) is None
