#!/usr/bin/env bash
set -euo pipefail

ROOT="/workspace/NW-checker"
cd "$ROOT"

echo "== Python env =="
python -V || true
which python || true

# --- Python tests ---
echo "== PyTest =="
# src が見えるように（pytest.ini でもOKだが念のため）
export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"
python -m pytest -q

# --- Flutter tests ---
if [ -f "$ROOT/pubspec.yaml" ]; then
  # ルートがFlutterプロジェクトならそのまま
  FLUT_DIR="$ROOT"
elif [ -f "$ROOT/nw_checker/pubspec.yaml" ]; then
  # サブフォルダ構成の場合
  FLUT_DIR="$ROOT/nw_checker"
else
  FLUT_DIR=""
fi

if command -v flutter >/dev/null 2>&1 && [ -n "$FLUT_DIR" ]; then
  echo "== Flutter test =="
  cd "$FLUT_DIR"
  # 依存解決（早い＆冪等。無ければ即時終了）
  flutter pub get >/dev/null 2>&1 || true
  # 詳細出力＆並列落ち対策
  flutter test --reporter expanded --concurrency 1
else
  echo "== Flutter test skipped (flutter or pubspec.yaml not found) =="
fi

echo "== ALL TESTS PASSED =="
