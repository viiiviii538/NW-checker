#!/usr/bin/env bash
set -euo pipefail

# 全体skip回避＆文字化け防止
export FORCE_RUN_PYTEST=1
export PYTHONUTF8=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

ROOT="$(pwd)"; cd "$ROOT"

# venvがあれば使う
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
elif [[ -f .venv/Scripts/activate ]]; then
  source .venv/Scripts/activate
fi

# 以降はこのPythonに統一
PY="$(command -v python || command -v python3)"
[ -n "$PY" ] || { echo "python not found"; exit 1; }
echo "== Using PY == $PY"
"$PY" -c "import sys; print('PY:', sys.executable)"

echo "== Setup Python deps =="
"$PY" -m pip install -U pip wheel
[[ -f requirements.txt ]] && "$PY" -m pip install -r requirements.txt || true
[[ -f requirements-dev.txt ]] && "$PY" -m pip install -r requirements-dev.txt || true
"$PY" -m pip install fastapi uvicorn httpx anyio python-multipart pytest pytest-benchmark
"$PY" -m pip install -e . || true

echo "== Verify deps =="
"$PY" - <<'PY'
import pkgutil, sys
mods = ['fastapi','starlette','httpx','anyio','multipart','pytest']
print('PY:', sys.executable)
for m in mods:
    print(f"{m}: {'OK' if pkgutil.find_loader(m) else 'MISSING'}")
try:
    import fastapi, starlette
    print('fastapi', fastapi.__version__)
    print('starlette', starlette.__version__)
except Exception as e:
    print('ver check skipped:', e)
PY

echo '== PyTest =='
export PYTHONPATH="$ROOT:$ROOT/src:${PYTHONPATH:-}"
"$PY" -m pytest -q

# Flutter tests（あれば）
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
