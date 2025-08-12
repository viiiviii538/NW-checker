# nw-checker

## DNS Blacklist

The dynamic scan compares reverse DNS results against a configurable
blacklist. Edit `data/dns_blacklist.txt` to add or remove domains. Each
non-empty line should contain a single domain name; lines beginning with
`#` are treated as comments.

