"""Network mapping utilities."""

import argparse
import json
import sys

from .discover_hosts import discover_hosts


def network_map(subnet: str):
    """Return a list of reachable hosts in *subnet*.

    This function is a thin wrapper around :func:`discover_hosts` to allow
    for straightforward unit testing and potential future extensions.
    """

    return discover_hosts(subnet)


def main(argv=None):
    """CLI entry point for building a network map."""

    parser = argparse.ArgumentParser(description="Scan a subnet for hosts")
    parser.add_argument("subnet", help="CIDR subnet to scan")
    args = parser.parse_args(argv)
    try:
        hosts = network_map(args.subnet)
    except Exception as exc:
        print(f"Host discovery failed: {exc}", file=sys.stderr)
        return 1
    json.dump(hosts, sys.stdout)
    sys.stdout.write("\n")
    print("Host discovery succeeded", file=sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
