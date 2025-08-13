"""LAN host discovery utilities."""

import socket
import subprocess


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


def discover_hosts(subnet: str):
    """Discover devices in the given subnet.

    The current implementation delegates the heavy lifting to an external
    command that lists candidate hosts (one IP address per line).  Each
    candidate is probed via :func:`_verify_host` to confirm that it is
    reachable.

    Returns:
        list of IP addresses for hosts that responded.
    """
    try:
        output = subprocess.check_output(["discover_hosts", subnet], text=True)
    except (OSError, subprocess.CalledProcessError):
        return []

    candidates = [line.strip() for line in output.splitlines() if line.strip()]
    return [ip for ip in candidates if _verify_host(ip)]
