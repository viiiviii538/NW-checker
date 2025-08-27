import pytest
from src.dynamic_scan import dns_analyzer


def test_load_blacklist_ignores_comments_and_blank_lines(tmp_path):
    file = tmp_path / "bl.txt"
    file.write_text("foo.example\n# comment\n\nBAR.example\n")
    bl = dns_analyzer.load_blacklist(str(file))
    assert bl == {"foo.example", "bar.example"}


def test_reverse_dns_lookup_caches_and_reuses_result():
    dns_analyzer._dns_cache.clear()

    def fake_resolver(ip):
        return ("Host.Example.", [], [])

    host = dns_analyzer.reverse_dns_lookup("1.1.1.1", resolver=fake_resolver)
    assert host == "host.example"
    assert dns_analyzer._dns_cache["1.1.1.1"][0] == "host.example"

    def failing(_):
        raise RuntimeError("network down")

    # キャッシュされた結果が返るため例外は表に出ない
    cached = dns_analyzer.reverse_dns_lookup("1.1.1.1", resolver=failing)
    assert cached == "host.example"


def test_reverse_dns_lookup_failure_without_cache():
    dns_analyzer._dns_cache.clear()

    def failing(_):
        raise RuntimeError("network down")

    assert dns_analyzer.reverse_dns_lookup("2.2.2.2", resolver=failing) is None


def test_reverse_dns_lookup_cache_ttl(monkeypatch):
    dns_analyzer._dns_cache.clear()
    times = iter([0, 1, 7200])
    monkeypatch.setattr(dns_analyzer.time, "time", lambda: next(times))

    def first(ip):
        return ("first.example", [], [])

    def second(ip):
        return ("second.example", [], [])

    host1 = dns_analyzer.reverse_dns_lookup("1.1.1.1", resolver=first, cache_ttl=3600)
    # TTL 内なのでキャッシュが利用され second は呼ばれない
    host2 = dns_analyzer.reverse_dns_lookup("1.1.1.1", resolver=second, cache_ttl=3600)
    assert host1 == host2 == "first.example"

    # TTL 失効後は second の結果になる
    host3 = dns_analyzer.reverse_dns_lookup("1.1.1.1", resolver=second, cache_ttl=3600)
    assert host3 == "second.example"


def test_is_blacklisted(monkeypatch, tmp_path):
    file = tmp_path / "bl.txt"
    file.write_text("bad.example\n")
    bl = dns_analyzer.load_blacklist(str(file))
    monkeypatch.setattr(dns_analyzer, "DOMAIN_BLACKLIST", bl, raising=False)
    assert dns_analyzer.is_blacklisted("bad.example")
    assert dns_analyzer.is_blacklisted("Bad.Example")
    assert not dns_analyzer.is_blacklisted("good.example")


def test_load_blacklist_missing_file(tmp_path):
    assert dns_analyzer.load_blacklist(str(tmp_path / "none.txt")) == set()
