from src.scans import os_banner


class FakeScanner:
    def scan(self, target, arguments):
        assert "-O" in arguments and "-sV" in arguments
        return {
            "scan": {
                target: {
                    "osmatch": [{"name": "Linux 5.x"}],
                    "tcp": {22: {"name": "ssh", "version": "OpenSSH 8.2"}},
                }
            }
        }


def fake_portscanner():
    return FakeScanner()


def test_os_banner_collects_os_and_services(monkeypatch):
    monkeypatch.setattr(os_banner.nmap, "PortScanner", fake_portscanner)
    result = os_banner.scan("1.2.3.4")
    assert result["details"]["banners"] == {22: "ssh OpenSSH 8.2"}
    assert result["details"]["os"] == "Linux 5.x"
    assert result["score"] == 2
