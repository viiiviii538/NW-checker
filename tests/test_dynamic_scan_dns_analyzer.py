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

    host, blacklisted = dns_analyzer.reverse_dns_lookup(
        "1.1.1.1", gethostbyaddr=fake_gethostbyaddr
    )
    assert host == "host.example"
    assert blacklisted is False
    assert dns_analyzer._dns_cache["1.1.1.1"] == ("host.example", False)

    def failing(_):
        raise RuntimeError("network down")

    # キャッシュされた結果が返るため例外は表に出ない
    cached_host, cached_bl = dns_analyzer.reverse_dns_lookup(
        "1.1.1.1", gethostbyaddr=failing
    )
    assert cached_host == "host.example"
    assert cached_bl is False


def test_reverse_dns_lookup_failure_without_cache():
    dns_analyzer._dns_cache.clear()

    def failing(_):
        raise RuntimeError("network down")

    assert dns_analyzer.reverse_dns_lookup("2.2.2.2", gethostbyaddr=failing) == (
        None,
        None,
    )


def test_reverse_dns_lookup_blacklisted():
    dns_analyzer._dns_cache.clear()
    dns_analyzer.DOMAIN_BLACKLIST.add("bad.example")

    def fake_gethostbyaddr(_):
        return ("bad.example", [], [])

    host, blacklisted = dns_analyzer.reverse_dns_lookup(
        "3.3.3.3", gethostbyaddr=fake_gethostbyaddr
    )
    assert host == "bad.example"
    assert blacklisted is True
