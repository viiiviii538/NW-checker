import pytest
from src.port_scan import scan_ports

def test_scan_ports_runs():
    result = scan_ports("127.0.0.1")
    assert isinstance(result, list)
