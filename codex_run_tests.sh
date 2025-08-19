#!/usr/bin/env bash
set -euo pipefail

# --- 保険：pytest全体skipの回避フラグ（conftest対策）、文字化け防止など ---
export FORCE_RUN_PYTEST=1
export PYTHONUTF8=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

ROOT="$(pwd)"
cd "$ROOT"

# ✅ .venv があれば必ず使う（Linux/macOS & Windows Git Bash対応）
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
elif [[ -f .venv/Scripts/activate ]]; then
  source .venv/Scripts/activate
fi
python -c "import sys; print('PY:', sys.executable)"

echo "== Python env =="
python -V || true
which python || true

echo "== Setup Python deps =="
python -m pip install -U pip wheel
# 本番依存
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt || true
fi
# 開発/テスト依存
if [[ -f requirements-dev.txt ]]; then
  cat requirements-dev.txt
  pip install -r requirements-dev.txt || true
fi
# 必要パッケージを明示（毎回クリーン環境想定）
pip install fastapi uvicorn httpx anyio python-multipart
pip install pytest pytest-benchmark
# src を import できるように（pyproject/ setupが無い環境でも失敗を無視）
python -m pip install -e . || true

echo "== Verify deps =="
python - <<'PY'
import pkgutil
mods = ['fastapi','starlette','httpx','anyio','multipart','pytest']
for m in mods:
    print(f"{m}: {'OK' if pkgutil.find_loader(m) else 'MISSING'}")
try:
    import fastapi, starlette
    print('fastapi', fastapi.__version__)
    print('starlette', starlette.__version__)
except Exception as e:
    print('ver check skipped:', e)
PY

# --- Python tests ---
echo '== PyTest =='
export PYTHONPATH="$ROOT:$ROOT/src:${PYTHONPATH:-}"
pytest -q

# --- Flutter tests ---
if [[ -f "$ROOT/pubspec.yaml" ]]; then
  FLUT_DIR="$ROOT"
elif [[ -f "$ROOT/nw_checker/pubspec.yaml" ]]; then
  FLUT_DIR="$ROOT/nw_checker"
else
  FLUT_DIR=""
fi

if command -v flutter >/dev/null 2>&1 && [[ -n "$FLUT_DIR" ]]; then
  echo "== Flutter test =="
  cd "$FLUT_DIR"
  flutter pub get >/dev/null 2>&1 || true
  flutter test --reporter expanded --concurrency 1
else
  echo "== Flutter test skipped (flutter or pubspec.yaml not found) =="
fi

echo "== ALL TESTS PASSED =="
