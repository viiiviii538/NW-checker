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


def traceroute(ip: str) -> List[str]:
    """Return hop IP addresses for ``ip`` using the system's traceroute."""
    output = subprocess.check_output(["traceroute", "-n", ip], text=True)
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


def _augment_with_snmp(hops: List[str], path: List[str], community: str = "public") -> None:
    """Replace hop labels with LLDP neighbor names when available."""
    if nextCmd is None:
        return
    for idx, hop in enumerate(hops[:-1]):  # 最終ホストは除外
        neighbors = _get_lldp_neighbors(hop, community)
        if neighbors:
            path[idx + 1] = neighbors[0]


def build_paths(hosts: Iterable[str], use_snmp: bool = False, community: str = "public") -> dict:
    """Construct labelled paths for ``hosts``.

    Each path starts with ``LAN`` and converts hop IPs to generic labels
    such as ``Router`` and ``Host``. When ``use_snmp`` is true and
    :mod:`pysnmp` is available, the path is augmented with LLDP neighbor
    names via :func:`_augment_with_snmp`.
    """
    results = []
    for ip in hosts:
        hops = traceroute(ip)
        path: List[str] = ["LAN"]
        for hop in hops:
            path.append("Host" if hop == ip else "Router")
        if use_snmp and nextCmd is not None:
            _augment_with_snmp(hops, path, community)
        results.append({"ip": ip, "path": path})
    return {"paths": results}


def build_topology(hosts: Iterable[str], use_snmp: bool = False, community: str = "public") -> str:
    """Backward compatible wrapper returning JSON string paths."""
    data = build_paths(hosts, use_snmp=use_snmp, community=community)
    # Historical format expected only the list of path arrays
    return json.dumps({"paths": [entry["path"] for entry in data["paths"]]})


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
    from . import discover_hosts  # local import to avoid heavy dependency during import

    discovered = discover_hosts.discover_hosts(subnet)
    hosts = [h["ip"] if isinstance(h, dict) else h for h in discovered]
    return build_topology(hosts, use_snmp=use_snmp, community=community)
