# tests/conftest.py
import pytest
import importlib.util

def _has(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None

# ここだけ全体skip（API層が無いとほぼ全部落ちるため）
if not _has("fastapi"):
    pytest.skip("fastapi が無いので Codex/Windows では pytest 全体を skip", allow_module_level=True)

# 他の依存 (impacket, nmap, pysnmp など) は
# 各テストファイルで pytest.importorskip() する
