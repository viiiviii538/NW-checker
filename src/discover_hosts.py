"""LAN host discovery utilities."""

import socket
import subprocess
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


def _run_nmap_scan(subnet: str) -> List[Dict[str, Optional[str]]]:
    """Run an nmap scan and return discovered hosts.

    Each host is represented as a dict with ``ip`` and optional ``hostname``
    fields.  The ``-R`` option forces reverse DNS resolution so that nmap tries
    to determine hostnames for all targets.
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
        # Example line: "Host: 192.168.0.1 (router)\tStatus: Up"
        parts = line.split()
        ip = parts[1]
        hostname: Optional[str] = None
        if len(parts) > 2 and parts[2].startswith("("):
            hostname = parts[2].strip("()")
        hosts.append({"ip": ip, "hostname": hostname})
    return hosts


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


def discover_hosts(subnet: str) -> List[Dict[str, str]]:
    """Discover devices in the given subnet.

    The current implementation delegates the heavy lifting to ``nmap`` to obtain
    a list of candidate hosts.  Each candidate is probed via
    :func:`_verify_host` to confirm reachability.  If ``nmap`` did not provide a
    hostname, ``nbtscan`` or ``avahi-resolve`` is invoked to attempt name
    resolution.
    """
    hosts = [h for h in _run_nmap_scan(subnet) if _verify_host(h["ip"]) ]

    for host in hosts:
        if host.get("hostname"):
            continue
        hostname = _get_hostname_nbtscan(host["ip"])
        if not hostname:
            hostname = _get_hostname_avahi(host["ip"])
        if hostname:
            host["hostname"] = hostname
    return hosts
