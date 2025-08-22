from src.dynamic_scan import dns_analyzer


def test_reverse_dns_lookup(monkeypatch):
    monkeypatch.setattr(dns_analyzer.socket, "gethostbyaddr", lambda ip: ("host.example", [], []))
    assert dns_analyzer.reverse_dns_lookup("1.1.1.1") == "host.example"


def test_reverse_dns_lookup_cached(monkeypatch):
    dns_analyzer._dns_cache.clear()
    monkeypatch.setattr(dns_analyzer.socket, "gethostbyaddr", lambda ip: ("host.example", [], []))
    dns_analyzer.reverse_dns_lookup("1.1.1.1")
    monkeypatch.setattr(
        dns_analyzer.socket,
        "gethostbyaddr",
        lambda ip: (_ for _ in ()).throw(AssertionError),
    )
    assert dns_analyzer.reverse_dns_lookup("1.1.1.1") == "host.example"


def test_load_blacklist(monkeypatch, tmp_path):
    path = tmp_path / "bl.txt"
    path.write_text("bad.example\n")
    assert dns_analyzer.load_blacklist(str(path)) == {"bad.example"}
