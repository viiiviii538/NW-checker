"""LAN host discovery utilities."""

import socket
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional


def _verify_host(ip: str, port: int = 80, timeout: float = 0.1) -> bool:
    """Verify that a host responds on the given port.

    A simple TCP connection attempt is used to check reachability.  This
    function is intentionally lightweight so that it can be easily mocked in
    tests without performing real network operations.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.connect((ip, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _lookup_vendor(mac: str) -> Optional[str]:
    """Return the vendor name for *mac*.

    The lookup first tries a local ``oui.txt`` file (if present).  When the
    file is missing or the entry cannot be found, the public API
    ``api.macvendors.com`` is queried as a fallback.
    """

    mac = mac.upper().replace(":", "").replace("-", "")
    if len(mac) < 6:
        return None
    prefix = mac[:6]
    oui_path = Path(__file__).resolve().parent.parent / "data" / "oui.txt"
    try:
        with open(oui_path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key = line.split()[0].replace("-", "").upper()
                if key == prefix and len(line.split(None, 1)) == 2:
                    return line.split(None, 1)[1].strip()
    except FileNotFoundError:
        pass
    # Fallback to external API
    try:
        with urllib.request.urlopen(
            f"https://api.macvendors.com/{mac}", timeout=5
        ) as resp:
            data = resp.read().decode().strip()
            return data or None
    except Exception:
        return None


def _run_nmap_scan(subnet: str) -> List[Dict[str, Optional[str]]]:
    """Run an nmap scan and return discovered hosts.

    Each host is represented as a dict with ``ip`` and optional ``hostname``
    and ``vendor`` fields.  The ``-R`` option forces reverse DNS resolution so
    that nmap tries to determine hostnames for all targets.
    """
    try:
        output = subprocess.check_output(
            ["nmap", "-sn", "-oG", "-", "-R", subnet], text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    hosts: List[Dict[str, Optional[str]]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("Host:"):
            continue
        # Example line: "Host: 192.168.0.1 (router)\tStatus: Up MAC: aa:bb:cc:dd:ee:ff (Vendor)"
        parts = line.split()
        ip = parts[1]
        hostname: Optional[str] = None
        if len(parts) > 2 and parts[2].startswith("("):
            hostname = parts[2].strip("()")
        mac: Optional[str] = None
        vendor: Optional[str] = None
        if "MAC:" in parts:
            idx = parts.index("MAC:")
            if idx + 1 < len(parts):
                mac = parts[idx + 1]
            if idx + 2 < len(parts) and parts[idx + 2].startswith("("):
                vendor = parts[idx + 2].strip("()")
        if mac and not vendor:
            vendor = _lookup_vendor(mac)
        host: Dict[str, Optional[str]] = {"ip": ip, "hostname": hostname}
        if vendor:
            host["vendor"] = vendor
        hosts.append(host)

    # Complement hostnames using nbtscan and avahi-resolve if necessary
    for host in hosts:
        if host.get("hostname"):
            continue
        try:
            output = subprocess.check_output(["nbtscan", "-q", host["ip"]], text=True)
        except (OSError, subprocess.CalledProcessError):
            output = ""
        for line in output.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0] == host["ip"]:
                host["hostname"] = parts[1]
                break
        if host.get("hostname"):
            continue
        try:
            output = subprocess.check_output(
                ["avahi-resolve", "-a", host["ip"]], text=True
            )
        except (OSError, subprocess.CalledProcessError):
            continue
        for line in output.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0] == host["ip"]:
                host["hostname"] = parts[1]
                break
    return hosts


def discover_hosts(subnet: str) -> List[Dict[str, str]]:
    """Discover devices in the given subnet.

    Candidate hosts are gathered via :func:`_run_nmap_scan` and each address is
    verified for reachability using :func:`_verify_host`.  Hostname resolution
    and vendor lookups are performed within ``_run_nmap_scan``.
    """
    hosts = [h for h in _run_nmap_scan(subnet) if _verify_host(h["ip"])]
    return hosts
