import argparse
import json
import logging
import os
from typing import Iterable

import requests

logger = logging.getLogger(__name__)


def fetch_feed(url: str) -> set[str]:
    """Fetch a blacklist feed and return a set of domains."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as exc:  # pragma: no cover - ログ確認用
        logger.error("failed to fetch %s: %s", url, exc)
        return set()

    content_type = resp.headers.get("Content-Type", "")
    try:
        if "json" in content_type or url.endswith(".json"):
            data = resp.json()
            if isinstance(data, dict):
                domains = data.get("domains") or data.get("blacklist") or []
            elif isinstance(data, list):
                domains = data
            else:
                domains = []
        else:
            domains = resp.text.splitlines()
    except Exception as exc:  # pragma: no cover - ログ確認用
        logger.error("failed to parse feed %s: %s", url, exc)
        return set()

    return {d.strip() for d in domains if d and not d.strip().startswith("#")}


def merge_blacklist(feed_domains: set[str], path: str = "data/dns_blacklist.txt") -> None:
    """Merge feed domains into blacklist file atomically."""
    if not feed_domains:
        logger.info("no domains to merge")
        return

    tmp_path = f"{path}.tmp"
    try:
        existing: set[str] = set()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = {line.strip() for line in f if line.strip() and not line.startswith("#")}

        combined = existing | {d for d in feed_domains if d}

        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("# DNS blacklist\n")
            for domain in sorted(combined):
                f.write(domain + "\n")

        os.replace(tmp_path, path)
    except Exception as exc:  # pragma: no cover - エラー時は既存ファイル保持
        logger.error("failed to update blacklist: %s", exc)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def update(feed_url: str, path: str = "data/dns_blacklist.txt") -> None:
    """Fetch feed and merge into blacklist file."""
    domains = fetch_feed(feed_url)
    merge_blacklist(domains, path)


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Update DNS blacklist from feed")
    parser.add_argument("feed_url", help="Blacklist feed URL")
    parser.add_argument("--output", default="data/dns_blacklist.txt", help="Blacklist file path")
    args = parser.parse_args(argv)

    update(args.feed_url, args.output)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    logging.basicConfig(level=logging.INFO)
    main()
