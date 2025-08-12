import argparse
import csv
import json
import logging
import os
from io import StringIO
from typing import Iterable, Set

import requests

logger = logging.getLogger(__name__)


def fetch_feed(url: str) -> Set[str]:
    """Fetch a blacklist feed and return set of domains."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        logger.error("failed to fetch %s: %s", url, exc)
        return set()

    content_type = resp.headers.get("Content-Type", "")
    text = resp.text

    try:
        if "json" in content_type or url.endswith(".json"):
            data = json.loads(text)
            if isinstance(data, dict):
                domains = data.get("domains") or data.get("blacklist") or []
            elif isinstance(data, list):
                domains = data
            else:
                domains = []
        else:
            domains = []
            reader = csv.reader(StringIO(text))
            for row in reader:
                if row:
                    domains.append(row[0].strip())
    except Exception as exc:
        logger.error("failed to parse feed %s: %s", url, exc)
        return set()

    return {d for d in (dom.strip() for dom in domains) if d and not d.startswith("#")}


def write_blacklist(domains: Set[str], path: str = "data/dns_blacklist.txt") -> None:
    """Write domains to blacklist file, keeping existing entries."""
    if not domains:
        logger.info("no domains fetched; skipping update")
        return

    tmp_path = f"{path}.tmp"

    try:
        existing: Set[str] = set()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = {line.strip() for line in f if line.strip() and not line.startswith("#")}

        combined = existing | domains

        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("# DNS blacklist\n")
            for domain in sorted(combined):
                f.write(domain + "\n")

        os.replace(tmp_path, path)
    except Exception as exc:
        logger.error("failed to write blacklist: %s", exc)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Update DNS blacklist from feeds")
    parser.add_argument("feeds", nargs="+", help="Feed URLs (CSV or JSON)")
    parser.add_argument("--output", default="data/dns_blacklist.txt", help="Blacklist file path")
    args = parser.parse_args(argv)

    all_domains: Set[str] = set()
    for url in args.feeds:
        all_domains |= fetch_feed(url)

    write_blacklist(all_domains, args.output)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    logging.basicConfig(level=logging.INFO)
    main()
