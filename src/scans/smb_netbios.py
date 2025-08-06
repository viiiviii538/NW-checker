"""SMB/NetBIOS checks using Scapy."""

from scapy.all import srp, Ether, IP  # type: ignore


def scan(target: str) -> dict:
    """Placeholder SMB/NetBIOS scan."""
    try:
        # 実際の通信は後で実装予定
        _ = (srp, Ether, IP)  # 参照して未使用警告を抑制
        details = {"hosts": []}
        return {"category": "smb_netbios", "score": 0, "details": details}
    except Exception as exc:
        return {"category": "smb_netbios", "score": 0, "details": {"error": str(exc)}}
