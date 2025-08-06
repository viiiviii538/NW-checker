"""SSL certificate inspection."""

import ssl
import socket


def scan(host: str, port: int = 443) -> dict:
    """Fetch SSL certificate details from a host."""
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        return {"category": "ssl_cert", "score": 0, "details": {"subject": cert.get("subject")}}
    except Exception as exc:
        return {"category": "ssl_cert", "score": 0, "details": {"error": str(exc)}}
