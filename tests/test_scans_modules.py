from src.scans import ports, os_banner, smb_netbios, upnp, arp_spoof, dhcp, dns, ssl_cert


def test_scan_modules_return_unified_dict():
    modules = [
        (ports.scan, {"target": "127.0.0.1"}),
        (os_banner.scan, {"target": "127.0.0.1"}),
        (smb_netbios.scan, {"target": "127.0.0.1"}),
        (upnp.scan, {}),
        (arp_spoof.scan, {}),
        (dhcp.scan, {}),
        (dns.scan, {"name": "example.com"}),
        (ssl_cert.scan, {"host": "example.com"}),
    ]
    for func, kwargs in modules:
        result = func(**kwargs)
        assert set(result.keys()) == {"category", "score", "details"}
        assert isinstance(result["category"], str)
        assert isinstance(result["score"], int)
        assert isinstance(result["details"], dict)
