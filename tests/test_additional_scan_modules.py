import types

from src.scans import ports, os_banner, smb_netbios, upnp


def test_ports_scan_reports_open_ports(monkeypatch):
    """Normal path: socket open triggers score and open_ports list."""

    def fake_connect(addr, timeout=0.5):  # noqa: ARG001
        if addr[1] == 22:

            class Dummy:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):  # noqa: D401, ARG002
                    return False

            return Dummy()
        raise OSError

    monkeypatch.setattr(ports.socket, "create_connection", fake_connect)
    result = ports.scan("host")
    assert result["score"] == 1
    assert result["details"]["open_ports"] == [22]


def test_ports_scan_handles_exception(monkeypatch):
    def boom(*args, **kwargs):  # noqa: D401, ARG001, ARG002
        raise RuntimeError("sock fail")

    monkeypatch.setattr(ports.socket, "create_connection", boom)
    result = ports.scan("host")
    assert result["score"] == 0
    assert "sock fail" in result["details"]["error"]


def test_os_banner_scan_collects_info(monkeypatch):
    class MockScanner:
        def scan(self, target, arguments=""):
            return {
                "scan": {
                    target: {
                        "tcp": {"80": {"name": "http", "version": "Apache"}},
                        "osmatch": [{"name": "Linux"}],
                    }
                }
            }

    monkeypatch.setattr(os_banner.nmap, "PortScanner", lambda: MockScanner())
    result = os_banner.scan("host")
    assert result["score"] == 2
    assert result["details"]["os"] == "Linux"
    assert result["details"]["banners"] == {80: "http Apache"}


def test_os_banner_scan_handles_error(monkeypatch):
    class MockScanner:
        def scan(self, target, arguments=""):
            raise os_banner.nmap.PortScannerError("nmap boom")

    monkeypatch.setattr(os_banner.nmap, "PortScanner", lambda: MockScanner())
    result = os_banner.scan("host")
    assert result["score"] == 0
    assert result["details"]["banners"] == {}
    assert "nmap boom" in result["details"]["error"]


def test_smb_netbios_scan_detects_smb1(monkeypatch):
    class DummyNB:
        def queryIPForName(self, target, timeout=2):  # noqa: D401, ARG002
            return ["HOST"]

        def close(self):
            pass

    class DummyConn:
        def __init__(self, *args, **kwargs):  # noqa: D401, ARG002
            pass

        def getDialect(self):
            return 0x0000

        def logoff(self):
            pass

    monkeypatch.setattr(smb_netbios, "NetBIOS", lambda: DummyNB())
    monkeypatch.setattr(smb_netbios, "SMBConnection", DummyConn)
    result = smb_netbios.scan("host")
    assert result["score"] == 5
    assert result["details"]["smb1_enabled"] is True
    assert result["details"]["netbios_names"] == ["HOST"]


def test_smb_netbios_scan_handles_errors(monkeypatch):
    def failing_nb():
        raise RuntimeError("nb fail")

    class DummyConn:
        def __init__(self, *args, **kwargs):  # noqa: D401, ARG002
            raise OSError("conn fail")

    monkeypatch.setattr(smb_netbios, "NetBIOS", failing_nb)
    monkeypatch.setattr(smb_netbios, "SMBConnection", DummyConn)
    result = smb_netbios.scan("host")
    assert result["score"] == 0
    assert result["details"]["smb1_enabled"] is False
    assert "conn fail" in result["details"]["error"]


def test_upnp_scan_flags_responder(monkeypatch):
    response = types.SimpleNamespace(
        src="1.2.3.4", load=b"HTTP/1.1 200 OK\r\nSERVER: upnp\r\n"
    )
    monkeypatch.setattr(upnp, "sr1", lambda *_, **__: response)
    result = upnp.scan()
    assert result["score"] == 1
    assert result["details"]["responders"] == ["1.2.3.4"]


def test_upnp_scan_handles_error(monkeypatch):
    def boom(*args, **kwargs):  # noqa: D401, ARG001, ARG002
        raise RuntimeError("boom")

    monkeypatch.setattr(upnp, "sr1", boom)
    result = upnp.scan()
    assert result["score"] == 0
    assert "boom" in result["details"]["error"]
