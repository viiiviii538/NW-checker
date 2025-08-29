# nw-checker

## DNS Blacklist

The dynamic scan compares reverse DNS results against a configurable
blacklist. Edit `data/dns_blacklist.txt` to add or remove domains. This
file is loaded at startup; each non-empty line should contain a single
domain name, and lines beginning with `#` are treated as comments.

## Local reproduction

```bash
ruff check . && black --check . && mypy src && pytest -m "not fastapi and not slow" --cov=src
pytest -m fastapi
(cd nw_checker && flutter analyze && flutter test --coverage)
```

