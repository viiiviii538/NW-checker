# tests/conftest.py
import os
import platform
import importlib.util
import pytest


def _has(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


# ---- 強制実行フラグ（CI/Codex用）------------------------------------------
# codex_run_tests.sh で  export FORCE_RUN_PYTEST=1  を立てている想定。
if os.getenv("FORCE_RUN_PYTEST") == "1":
    pass  # 常に続行

else:
    # 本当に Windows かつ fastapi が無いときだけ全体 skip
    if platform.system() == "Windows" and not _has("fastapi"):
        pytest.skip(
            "fastapi が無いので Windows では pytest 全体を skip",
            allow_module_level=True,
        )
