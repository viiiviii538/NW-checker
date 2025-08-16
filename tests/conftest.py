# tests/conftest.py
import pytest

REQUIRED = ["fastapi", "httpx", "geoip2", "impacket", "pysnmp", "python_nmap"]

_missing = []
for m in REQUIRED:
    try:
        __import__(m)
    except Exception:
        _missing.append(m)

if _missing:
    pytest.skip(
        "Skipping Python tests: missing packages -> " + ", ".join(_missing),
        allow_module_level=True,
    )
