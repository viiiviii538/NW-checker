"""Static scan for SSL certificate issues."""

from __future__ import annotations

from datetime import datetime, timezone
import socket
import ssl

# 信頼された証明書発行者の簡易リスト
TRUSTED_ISSUERS = {
    "Let's Encrypt",
    "DigiCert",
    "GlobalSign",
    "Sectigo",
}


def _extract_issuer(cert: dict) -> str:
    """抽出した issuer 情報を文字列に整形して返す。"""

    issuer = cert.get("issuer", ())
    names = []
    for part in issuer:
        for key, value in part:
            if key.lower() in {"organizationname", "commonname"}:
                names.append(value)
    return ", ".join(names)


def scan(host: str = "example.com", port: int = 443) -> dict:
    """Retrieve the server certificate and evaluate expiry and issuer."""

    expired = False
    days_remaining: int | None = None
    issuer = ""
    cert_data: dict = {}
    error = ""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cert_data = cert
                issuer = _extract_issuer(cert)
                not_after = cert.get("notAfter")
                if not_after:
                    expiry = datetime.strptime(
                        not_after, "%b %d %H:%M:%S %Y %Z"
                    ).replace(tzinfo=timezone.utc)
                    delta = expiry - datetime.now(timezone.utc)
                    days_remaining = delta.days
                    expired = days_remaining < 0
    except Exception as exc:  # pragma: no cover
        error = str(exc)

    # スコア算出
    score = 0
    if expired:
        score = 5
    else:
        if days_remaining is not None and days_remaining < 30:
            score += 2
        if issuer and all(t not in issuer for t in TRUSTED_ISSUERS):
            score += 1

    details = {
        "host": host,
        "expired": expired,
        "issuer": issuer,
        "days_remaining": days_remaining,
        "cert": cert_data,
    }
    if error:
        details["error"] = error
    return {
        "category": "ssl_cert",
        "score": score,
        "details": details,
    }

