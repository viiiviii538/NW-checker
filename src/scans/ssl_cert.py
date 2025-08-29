"""Static scan for SSL certificate issues."""

# SSL証明書の期限切れや信頼性をチェックする
from __future__ import annotations

from datetime import datetime, timezone
import socket
import ssl
from typing import Any

# 信頼された証明書発行者の簡易リスト
TRUSTED_ISSUERS = {
    "Let's Encrypt",
    "DigiCert",
    "GlobalSign",
    "Sectigo",
}


def _extract_issuer(cert: dict[str, Any] | None) -> str:
    """抽出した issuer 情報を文字列に整形して返す。"""

    if not cert:
        return ""
    issuer = cert.get("issuer", ())
    names = []
    for part in issuer:
        for key, value in part:
            if key.lower() in {"organizationname", "commonname"}:
                names.append(value)
    return ", ".join(names)


def scan(host: str = "example.com", port: int = 443) -> dict:
    category = "ssl_cert"
    details: dict[str, Any] = {"host": host}

    try:
        expired = False
        days_remaining: int | None = None
        issuer = ""
        cert_data: dict[str, Any] | None = None

        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cert_data = cert
                issuer = _extract_issuer(cert)
                not_after = cert.get("notAfter") if cert else None
                if isinstance(not_after, str):
                    expiry = datetime.strptime(
                        not_after, "%b %d %H:%M:%S %Y %Z"
                    ).replace(tzinfo=timezone.utc)
                    delta = expiry - datetime.now(timezone.utc)
                    days_remaining = delta.days
                    expired = days_remaining < 0

        score = 0
        if expired:
            score = 5
        else:
            if days_remaining is not None and days_remaining < 30:
                score += 2
            if issuer and all(t not in issuer for t in TRUSTED_ISSUERS):
                score += 1

        details.update(
            {
                "expired": expired,
                "issuer": issuer,
                "days_remaining": days_remaining,
                "cert": cert_data,
            }
        )
        return {"category": category, "score": score, "details": details}

    except Exception as exc:
        details["error"] = str(exc)
        return {"category": category, "score": 0, "details": details}
