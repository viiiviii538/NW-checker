#!/usr/bin/env bash
set -euo pipefail

echo "=== codex_run_tests.sh START ==="

ROOT="$(pwd)"
export PYTHONPATH="$ROOT/src:${PYTHONPATH:-}"

SOFT_CL="${SOFT_CL:-0}"   # 1なら緩め
PY_MIN_COV="${PY_MIN_COV:-80}"
FL_MIN_LINE_RATE="${FL_MIN_LINE_RATE:-80.0}"

run_or_warn () {
  local cmd="$1" name="$2"
  if [[ "$SOFT_CL" == "1" ]]; then
    echo "🔵 SOFT: $name"
    bash -lc "$cmd" || echo "⚠️ $name failed (ignored in soft mode)"
  else
    echo "🟥 HARD: $name"
    bash -lc "$cmd"
  fi
}

# --- Python lint/type ---
run_or_warn "ruff check src tests" "ruff"
run_or_warn "black --check src tests" "black"
run_or_warn "mypy src" "mypy"

# --- Python tests ---
pytest -m "not fastapi" -vv --cov=src --cov-report=xml

if [[ "$SOFT_CL" != "1" ]]; then
  python3 - <<PY
import sys, xml.etree.ElementTree as ET
cov = ET.parse('coverage.xml').getroot().get('line-rate')
rate = float(cov) * 100
thr = float("$PY_MIN_COV")
print(f"Python coverage: {rate:.1f}% (min {thr}%)")
sys.exit(0 if rate >= thr else 1)
PY
fi

# --- Flutter tests ---
FLUT_DIR=""
if [ -f "$ROOT/pubspec.yaml" ]; then FLUT_DIR="$ROOT"; fi
if [ -f "$ROOT/nw_checker/pubspec.yaml" ]; then FLUT_DIR="$ROOT/nw_checker"; fi

if command -v flutter >/dev/null 2>&1 && [ -n "$FLUT_DIR" ]; then
  cd "$FLUT_DIR"
  flutter pub get

  run_or_warn "flutter analyze" "flutter analyze"
  run_or_warn "dart format --output=none --set-exit-if-changed ." "dart format check"

  flutter test --coverage --reporter expanded --concurrency 1
  cd "$ROOT"

  if [[ "$SOFT_CL" != "1" ]]; then
    python3 check_coverage.py --lcov "$FLUT_DIR/coverage/lcov.info" --min-line-rate "$FL_MIN_LINE_RATE"
  else
    echo "SOFT: Flutter coverage skipped"
  fi
else
  echo "== Flutter test skipped =="
fi

echo "=== codex_run_tests.sh DONE ==="
