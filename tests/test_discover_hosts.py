import pytest
from src.discover_hosts import discover_hosts

def test_discover_hosts_runs():
    result = discover_hosts("192.168.0.0/24")
    assert isinstance(result, list)
