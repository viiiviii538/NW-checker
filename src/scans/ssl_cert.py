"""Static scan for SSL certificate issues."""

from datetime import datetime
import socket
import ssl


def scan(host: str = "example.com", port: int = 443) -> dict:
    """Retrieve the server certificate and check for expiration."""

    expired = False
    cert_data = {}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=2) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cert_data = cert
                not_after = cert.get("notAfter")
                if not_after:
                    expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    expired = expiry < datetime.utcnow()
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "ssl_cert",
        "score": 1 if expired else 0,
        "details": {"host": host, "expired": expired, "cert": cert_data},
    }

