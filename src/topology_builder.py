"""Network topology building utilities.

This module constructs simple path representations between the local
network and discovered hosts.  The implementation relies on the system's
``traceroute`` command and optionally augments hop information using
SNMP/LLDP queries via :mod:`pysnmp`.
"""

from __future__ import annotations

import json
import subprocess
from typing import Iterable, List

from . import discover_hosts

try:
    from pysnmp.hlapi import (
        CommunityData,
        ContextData,
        ObjectIdentity,
        ObjectType,
        SnmpEngine,
        UdpTransportTarget,
        nextCmd,
    )
except Exception:  # pragma: no cover - pysnmp may be unavailable
    CommunityData = ContextData = ObjectIdentity = ObjectType = SnmpEngine = UdpTransportTarget = nextCmd = None


LLDP_REMOTE_SYS_NAME_OID = "1.0.8802.1.1.2.1.4.1.1.9"


def _run_traceroute(ip: str) -> str:
    """Run ``traceroute`` and return its raw output."""
    return subprocess.check_output(["traceroute", "-n", ip], text=True)


def _parse_traceroute(output: str) -> List[str]:
    """Parse traceroute output into a list of hop IP addresses."""
    hops: List[str] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("traceroute"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] != "*":
            hops.append(parts[1])
    return hops


def _get_lldp_neighbors(ip: str, community: str = "public") -> List[str]:
    """Retrieve LLDP neighbor names using SNMP."""
    if nextCmd is None:  # pysnmp not available
        return []

    neighbors: List[str] = []
    try:
        for (error_indication, error_status, _error_index, var_binds) in nextCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), timeout=1, retries=0),
            ContextData(),
            ObjectType(ObjectIdentity(LLDP_REMOTE_SYS_NAME_OID)),
            lexicographicMode=False,
        ):
            if error_indication or error_status:
                break
            for var_bind in var_binds:
                neighbors.append(str(var_bind[1]))
    except Exception:
        return []
    return neighbors


def build_topology(hosts: Iterable[str], use_snmp: bool = False, community: str = "public") -> str:
    """Build topology paths for the given hosts.

    Args:
        hosts: Iterable of IP addresses discovered on the network.
        use_snmp: Whether to complement hop information via SNMP/LLDP.
        community: SNMP community string if ``use_snmp`` is ``True``.

    Returns:
        JSON string containing a ``paths`` array.
    """
    paths: List[List[str]] = []
    for ip in hosts:
        raw = _run_traceroute(ip)
        hops = _parse_traceroute(raw)
        path: List[str] = ["LAN"]
        for hop in hops:
            label = "Host" if hop == ip else "Router"
            if use_snmp and hop != ip:
                neighbors = _get_lldp_neighbors(hop, community)
                if neighbors:
                    # Use the first discovered neighbor name
                    path.append(neighbors[0])
                    continue
            path.append(label)
        paths.append(path)
    return json.dumps({"paths": paths})


def build_topology_for_subnet(subnet: str, use_snmp: bool = False, community: str = "public") -> str:
    """Discover hosts in ``subnet`` and build topology paths.

    This is a convenience wrapper around :func:`build_topology` that first
    calls :func:`discover_hosts.discover_hosts` to obtain candidate hosts.

    Args:
        subnet: CIDR notation for the network to scan.
        use_snmp: Whether to complement hop information via SNMP/LLDP.
        community: SNMP community string if ``use_snmp`` is ``True``.

    Returns:
        JSON string containing a ``paths`` array, same as
        :func:`build_topology`.
    """
    hosts = discover_hosts.discover_hosts(subnet)
    return build_topology(hosts, use_snmp=use_snmp, community=community)
