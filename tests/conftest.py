"""pytest 共通設定."""

import importlib.util


def _has(mod: str) -> bool:
    """Return True if the module can be imported."""
    return importlib.util.find_spec(mod) is not None


# 他の依存 (impacket, nmap, pysnmp など) は
# 各テストファイルで pytest.importorskip() する
