"""LAN host discovery utilities."""

import re
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import requests


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
    """Return vendor name for *mac* using ``oui.txt`` or external API."""
    prefix = mac.upper().replace("-", "").replace(":", "")[:6]
    oui_path = Path(__file__).resolve().parent.parent / "data" / "oui.txt"
    if oui_path.exists():
        try:
            with oui_path.open() as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split(None, 1)
                    key = parts[0].replace("-", "").replace(":", "").upper()
                    if key == prefix:
                        return parts[1].strip() if len(parts) > 1 else None
        except OSError:
            pass
    try:  # Fallback to API lookup
        resp = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception:
        pass
    return None


def _run_nmap_scan(subnet: str) -> List[Dict[str, Optional[str]]]:
    """Run an nmap scan and return discovered hosts.

    Each host is represented as a dict with ``ip`` and optional ``hostname`` and
    ``vendor`` fields.  The ``-R`` option forces reverse DNS resolution so that
    nmap tries to determine hostnames for all targets.  ``nbtscan`` and
    ``avahi-resolve`` are consulted when nmap does not provide a hostname.
    """
    try:
        output = subprocess.check_output(
            ["nmap", "-sn", "-oG", "-", "-R", subnet], text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    host_map: Dict[str, Dict[str, Optional[str]]] = {}
    host_re = re.compile(r"^Host:\s+(\S+)\s+\(([^)]*)\)")
    mac_re = re.compile(r"MAC Address:\s+([0-9A-Fa-f:]{17})(?:\s+\(([^)]+)\))?")

    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("Host:"):
            continue
        m_host = host_re.search(line)
        if not m_host:
            continue
        ip = m_host.group(1)
        hostname = m_host.group(2) or None
        entry = host_map.setdefault(
            ip, {"ip": ip, "hostname": hostname, "mac": None, "vendor": None}
        )
        if hostname and not entry.get("hostname"):
            entry["hostname"] = hostname
        m_mac = mac_re.search(line)
        if m_mac:
            entry["mac"] = m_mac.group(1)
            if m_mac.group(2):
                entry["vendor"] = m_mac.group(2)

    for host in host_map.values():
        ip = host.get("ip")
        if not host.get("hostname") and ip:
            hostname = _get_hostname_nbtscan(ip)
            if not hostname:
                hostname = _get_hostname_avahi(ip)
            if hostname:
                host["hostname"] = hostname
        mac = host.get("mac")
        if mac and not host.get("vendor"):
            vendor = _lookup_vendor(mac)
            if vendor:
                host["vendor"] = vendor

    results: List[Dict[str, Optional[str]]] = []
    for info in host_map.values():
        entry = {
            "ip": info["ip"],
            "hostname": info.get("hostname"),
            "vendor": info.get("vendor"),
        }
        results.append(entry)
    return results


def _get_hostname_nbtscan(ip: str) -> Optional[str]:
    """Try to resolve hostname using nbtscan."""
    try:
        output = subprocess.check_output(["nbtscan", "-q", ip], text=True)
    except (OSError, subprocess.CalledProcessError):
        return None

    for line in output.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0] == ip:
            return parts[1]
    return None


def _get_hostname_avahi(ip: str) -> Optional[str]:
    """Try to resolve hostname using avahi-resolve."""
    try:
        output = subprocess.check_output(["avahi-resolve", "-a", ip], text=True)
    except (OSError, subprocess.CalledProcessError):
        return None

    for line in output.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0] == ip:
            return parts[1]
    return None


def discover_hosts(subnet: str) -> List[Dict[str, Optional[str]]]:
    """Discover devices in the given subnet.

    The current implementation delegates the heavy lifting to ``nmap`` to obtain
    a list of candidate hosts.  Each candidate is probed via
    :func:`_verify_host` to confirm reachability.  Hostname resolution and
    vendor lookup are handled within :func:`_run_nmap_scan`.
    """
    hosts: List[Dict[str, Optional[str]]] = []
    for h in _run_nmap_scan(subnet):
        ip = h.get("ip")
        if ip and _verify_host(ip):
            hosts.append(h)
    return hosts
