#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
cd "$ROOT"

# ✅ ここを追加：.venv があれば必ず使う
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
elif [[ -f .venv/Scripts/activate ]]; then
  # Windows Git Bash 用
  source .venv/Scripts/activate
fi
python -c "import sys; print('PY:', sys.executable)"

echo "== Python env =="
python -V || true
which python || true

echo "== Setup Python deps =="
python -m pip install -U pip
# 本番依存
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt || true
fi
# 開発/テスト依存
if [[ -f requirements-dev.txt ]]; then
  cat requirements-dev.txt
  pip install -r requirements-dev.txt || true
fi
# 念のため FastAPI/Starlette 周りを明示（足りなければ入る）
pip install fastapi uvicorn httpx anyio python-multipart || true
# src を import できるように
python -m pip install -e . || true

echo "== Verify deps =="
python -c "import pkgutil;mods=['fastapi','starlette','httpx','anyio','multipart'];print('\n'.join([m+' '+('OK' if pkgutil.find_loader(m) else 'MISSING') for m in mods]))"
python -c "import fastapi,starlette;print('fastapi',fastapi.__version__);print('starlette',starlette.__version__)"

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
