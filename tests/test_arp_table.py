import sys
import subprocess
import types

from src.scans.arp_spoof import _get_arp_table

scapy_all = types.SimpleNamespace(ARP=object, send=lambda *args, **kwargs: None)
scapy = types.SimpleNamespace(all=scapy_all)
sys.modules.setdefault("scapy", scapy)
sys.modules.setdefault("scapy.all", scapy_all)


def test_get_arp_table_parses_and_ignores_malformed(monkeypatch):
    output = """? (192.168.1.1) at aa:bb:cc:dd:ee:01 on en0 ifscope [ethernet]
? (10.0.0.1) at 11:22:33:44:55:66 on en0 ifscope [ethernet]
? (10.0.0.2) at (incomplete) on en0 ifscope [ethernet]
? 10.0.0.3 at 77:88:99:aa:bb:cc on en0 ifscope [ethernet]
invalid line without expected format
"""

    def fake_check_output(*args, **kwargs):
        return output

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)

    table = _get_arp_table()
    assert table == {
        "192.168.1.1": "aa:bb:cc:dd:ee:01",
        "10.0.0.1": "11:22:33:44:55:66",
    }
    assert "10.0.0.2" not in table
    assert "10.0.0.3" not in table


def test_get_arp_table_handles_subprocess_error(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("arp failed")

    monkeypatch.setattr(subprocess, "check_output", boom)

    assert _get_arp_table() == {}
