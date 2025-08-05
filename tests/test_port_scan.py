import nmap
import pytest
from src.port_scan import scan_ports

def test_scan_ports_returns_only_open_ports(monkeypatch):
    fake_result = {
        "scan": {
            "127.0.0.1": {
                "tcp": {
                    22: {"state": "open"},
                    80: {"state": "closed"},
                    443: {"state": "open"},
                }
            }
        }
    }

    class FakeScanner:
        def scan(self, target_ip, arguments=""):
            return fake_result

    monkeypatch.setattr(nmap, "PortScanner", lambda: FakeScanner())

    result = scan_ports("127.0.0.1")
    assert result == [22, 443]


def test_scan_ports_handles_scan_errors(monkeypatch):
    class ErrorScanner:
        def scan(self, target_ip, arguments=""):
            raise nmap.PortScannerError("scan failed")

    monkeypatch.setattr(nmap, "PortScanner", lambda: ErrorScanner())

    with pytest.raises(nmap.PortScannerError):
        scan_ports("127.0.0.1")
