"""Probe SMB/NetBIOS services using impacket.

This scan attempts a NetBIOS name query and negotiates an SMB connection to
determine whether SMBv1 is enabled on the target host.
"""

from __future__ import annotations

from impacket.nmb import NetBIOS
from impacket.smbconnection import SMBConnection


def scan(target: str = "127.0.0.1") -> dict:
    """Inspect *target* for SMB/NetBIOS exposure.

    The function gathers NetBIOS names and checks if the server accepts the
    legacy SMBv1 dialect. Presence of SMBv1 increases the returned score.
    """

    details = {"target": target, "netbios_names": []}
    smb1_enabled = False

    # --- NetBIOS name lookup -------------------------------------------------
    try:
        nb = NetBIOS()
        try:
            names = nb.queryIPForName(target, timeout=2)
            if names:
                details["netbios_names"] = names
        finally:
            nb.close()
    except Exception:  # pragma: no cover - ネットワークエラー等は無視
        pass

    # --- SMB dialect negotiation --------------------------------------------
    try:
        conn = SMBConnection(target, target, sess_port=445, timeout=2)
        try:
            dialect = conn.getDialect()
            # SMBv1 のダイアレクトIDは SMB2(0x0202) 未満
            smb1_enabled = isinstance(dialect, int) and dialect < 0x0202
        finally:
            conn.logoff()
    except Exception as exc:
        details["error"] = str(exc)

    details["smb1_enabled"] = smb1_enabled
    score = 5 if smb1_enabled else 0
    return {"category": "smb_netbios", "score": score, "details": details}

