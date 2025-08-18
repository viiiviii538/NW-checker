"""Probe SMB/NetBIOS services using impacket.

This scan tries a NetBIOS name query and negotiates an SMB connection to
determine whether SMBv1 is enabled on the target host.
"""

# SMBv1の有効化やNetBIOS名の公開状況を確認する
from __future__ import annotations

import subprocess
from typing import Any, Dict, List

# Import as module-level names so tests can monkeypatch smb_netbios.NetBIOS / SMBConnection
try:
    from impacket.nmb import NetBIOS  # type: ignore
    from impacket.smbconnection import SMBConnection  # type: ignore
    HAS_IMPACKET = True
except Exception:  # pragma: no cover
    NetBIOS = None  # type: ignore
    SMBConnection = None  # type: ignore
    HAS_IMPACKET = False


def _nmblookup_names(target: str) -> list[str]:
    try:
        output = subprocess.check_output(["nmblookup", "-A", target], text=True, timeout=3)
    except Exception:  # pragma: no cover
        return []
    names: list[str] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Looking up") or "MAC Address" in line:
            continue
        name = line.split("<", 1)[0].strip()
        if name:
            names.append(name.upper())  # テストは大文字 "HOSTNAME" を期待
    return names

def scan(target: str) -> Dict[str, Any]:
    category = "smb_netbios"
    details: Dict[str, Any] = {"target": target, "netbios_names": [], "smb1_enabled": False}
    last_error: str | None = None

    try:
        # --- NetBIOS name lookup ---
        names: List[str] = []
        try:
            if NetBIOS is not None:
                nb = NetBIOS()  # type: ignore
                try:
                    names = nb.queryIPForName(target, timeout=2) or []
                finally:
                    try: nb.close()
                    except Exception: pass
        except Exception as e:
            # NetBIOS失敗は記録だけ。後で nmblookup フォールバック。
            last_error = str(e)
            names = []

        if not names:
            # フォールバック: nmblookup
            names = _nmblookup_names(target)
        if names:
            details["netbios_names"] = names

        # --- SMB dialect negotiation ---
        try:
            if SMBConnection is not None:
                conn = SMBConnection(target, target, sess_port=445, timeout=2)  # type: ignore
                try:
                    details["smb1_enabled"] = (conn.getDialect() == 0x0000)  # SMB1
                finally:
                    try: conn.logoff()
                    except Exception: pass
        except Exception as e:
            # SMBのエラーは優先（テストが"connection refused"等を期待）
            last_error = str(e)

        if last_error:
            details["error"] = last_error

        score = 5 if details["smb1_enabled"] else 0
        return {"category": category, "score": score, "details": details}

    except Exception as e:
        details["error"] = str(e)
        return {"category": category, "score": 0, "details": details}
