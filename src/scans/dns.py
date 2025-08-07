"""Static scan for DNS resolution using scapy."""

from scapy.all import IP, UDP, DNS, DNSQR, sr1  # type: ignore


def scan(domain: str = "example.com", server: str = "8.8.8.8") -> dict:
    """Query *domain* using DNS and return any answers."""

    answers = []
    try:
        pkt = IP(dst=server) / UDP(sport=12345, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain))
        resp = sr1(pkt, timeout=2, verbose=False)
        if resp and resp.haslayer(DNS) and resp[DNS].ancount > 0:
            for i in range(resp[DNS].ancount):
                ans = resp[DNS].an[i]
                if getattr(ans, "rdata", None):
                    answers.append(str(ans.rdata))
    except Exception:  # pragma: no cover
        pass

    return {
        "category": "dns",
        "score": len(answers),
        "details": {"domain": domain, "answers": answers},
    }

