# nw-checker

## DNS Blacklist

The dynamic scan compares reverse DNS results against a configurable
blacklist. Edit `data/dns_blacklist.txt` to add or remove domains. This
file is loaded at startup; each non-empty line should contain a single
domain name, and lines beginning with `#` are treated as comments.

python -m venv .venv && .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
pip install -e .
$env:FORCE_RUN_PYTEST="1"; pytest -q -rA
