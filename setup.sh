#!/usr/bin/env bash
set -euo pipefail

# ===== 基本設定 =====
export DEBIAN_FRONTEND=noninteractive
PROJECT_DIR="/workspace/NW-checker"
FLUTTER_VERSION=3.32.8
FLUTTER_DIR="$HOME/flutter"
export PATH="$FLUTTER_DIR/bin:$PATH"

echo "=== プロジェクトルートへ移動 ==="
cd "$PROJECT_DIR"

# ===== OSパッケージ（存在＆権限チェックつき）=====
if command -v apt-get >/dev/null 2>&1; then
  echo "=== OSパッケージインストール ==="
  if [ "$(id -u)" -ne 0 ]; then
    echo "root権限がないため apt-get をスキップまたは sudo を利用してください"; 
  else
    apt-get update -y
    # 既に入ってるものは再インストールしない
    pkgs=(git curl unzip nmap clang libgtk-3-dev python3-venv)
    apt-get install -y "${pkgs[@]}"
  fi
else
  echo "apt-get が無い環境のため OSパッケージ導入はスキップ"
fi

# ===== Python 環境 =====
echo "=== Python 仮想環境構築 ==="
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

if [ -f ".venv/bin/activate" ]; then
  # Linux/macOS
  # shellcheck disable=SC1091
  source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
  # Windows (Git Bash)
  # shellcheck disable=SC1091
  source .venv/Scripts/activate
else
  echo "❌ .venv の activate スクリプトが見つかりません"; exit 1
fi

echo "=== Python依存関係インストール ==="
python -m pip install --upgrade pip
# 依存は requirements.txt で一括

REQ_FILE="../requirements.txt"
[ -f "requirements.txt" ] && REQ_FILE="requirements.txt"
if [ -f "$REQ_FILE" ]; then
  pip install -r "$REQ_FILE"
else
  echo "requirements.txt が見つからないためスキップ ($REQ_FILE)"
fi

# 整形ツール(任意)
if ! command -v black >/dev/null 2>&1; then
  pip install black || true
fi

# ===== Flutter SDK =====
echo "=== Flutter SDK チェック ==="
if ! command -v flutter >/dev/null 2>&1; then
  if [ ! -d "$FLUTTER_DIR" ]; then
    echo "Flutter SDKをインストール中..."
    git clone --depth 1 https://github.com/flutter/flutter.git -b "$FLUTTER_VERSION" "$FLUTTER_DIR"
  else
    echo "既存のFlutter SDKを使用します"
  fi
  export PATH="$FLUTTER_DIR/bin:$PATH"
else
  echo "既にFlutter SDKがインストールされています"
  export PATH="$FLUTTER_DIR/bin:$PATH"
fi

flutter precache || true
if [ -w "$HOME" ] && ! grep -q "$FLUTTER_DIR/bin" "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/flutter/bin:$PATH"' >> "$HOME/.bashrc" || true
fi

# ===== Flutter Doctor / 依存 =====
echo "=== Flutter Doctor 実行 ==="
flutter doctor || echo "Flutter Doctor 警告あり（続行）"

if [ -f "pubspec.yaml" ]; then
  echo "=== Flutter依存関係取得 ==="
  flutter pub get || { echo "flutter pub get 失敗"; exit 1; }
else
  echo "⚠️ pubspec.yaml が無いので Flutter セットアップはスキップ"
fi

# ===== 改行統一 & Git設定 =====
# デフォルトはリポジトリを触らない（Codex対策）
if [ "${ALLOW_GIT_WRITE:-0}" = "1" ]; then
  echo "=== 改行統一設定(.gitattributes) ==="
  if [ ! -f ".gitattributes" ]; then
    cat > .gitattributes <<'EOF'
* text=auto eol=lf
*.dart text eol=lf
*.py   text eol=lf
*.sh   text eol=lf
EOF
    git add .gitattributes || true
  fi
  git config core.autocrlf false || true

  echo "=== Git pre-commit フック設定 ==="
  HOOK=".git/hooks/pre-commit"
  if [ -d ".git/hooks" ] && [ ! -f "$HOOK" ]; then
    cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
set -e
if git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . >/dev/null 2>&1; then
  echo "[pre-commit] Merge conflict markers detected."; exit 1
fi
command -v dart >/dev/null 2>&1 && dart format .
command -v black >/dev/null 2>&1 && black .
exit 0
EOF
    chmod +x "$HOOK"
  fi
else
  echo "Git write is disabled (set ALLOW_GIT_WRITE=1 to enable)."
fi

# ===== フォーマッタ（任意・既存維持）=====
echo "=== コード整形 (Dart / Python) ==="
command -v dart >/dev/null 2>&1 && dart format . || true
command -v black >/dev/null 2>&1 && black . || true

# ===== 競合マーカー検出（通知のみ）=====
echo "=== マージ競合マーカー検出 ==="
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . >/dev/null 2>&1; then
    echo "ERROR: マージ競合マーカーを検出しました。解消してください。"
    git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . || true
  fi
fi

# ===== pre-commit フック（既存維持）=====
echo "=== Git pre-commit フック設定 ==="
HOOK=".git/hooks/pre-commit"
if [ -d ".git/hooks" ] && [ ! -f "$HOOK" ]; then
cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
set -e
if git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . >/dev/null 2>&1; then
  echo "[pre-commit] Merge conflict markers detected. Resolve them before commit."
  git grep -n '<<<<<<< \|=======\|>>>>>>>' -- .; exit 1
fi
command -v dart >/dev/null 2>&1 && dart format .
command -v black >/dev/null 2>&1 && black .
exit 0
EOF
  chmod +x "$HOOK"
fi

# ===== 追加: nmap のセルフチェック =====
echo "=== nmap チェック（モジュール/バイナリ）==="
python - <<'PY' || true
import shutil
print("module nmap:", end=" ")
try:
    import nmap  # python-nmap
    print("OK")
except Exception as e:
    print("NG", e)
print("binary nmap:", shutil.which("nmap") or "NOT FOUND")
PY

# ===== PYTHONPATH を設定（pytestの import 安定化）=====
export PYTHONPATH="$PROJECT_DIR/src:$PROJECT_DIR/src/scans:${PYTHONPATH:-}"

# ===== Pythonテスト =====
echo "=== Pythonテスト実行 ==="
pytest || echo "Pythonテスト失敗（続行）"

# ===== Flutterテスト =====
echo "=== Flutterテスト実行 ==="
flutter test || echo "Flutterテスト失敗（続行）"

# ===== Python動作確認（任意）=====
echo "=== 動作確認（Python） ==="
if [ -f src/scans/ports.py ]; then
  python src/scans/ports.py || echo "Pythonスクリプト実行失敗（続行）"
else
  echo "src/scans/ports.py が見つかりません。スキップします。"
fi

# ===== Flutter実行（Windowsのみ案内）=====
echo "=== 動作確認（Flutter / Windowsビルド） ==="
case "${OSTYPE:-}" in
  msys*|cygwin*|win32*) flutter run -d windows || echo "Flutterアプリ実行失敗（続行）" ;;
  *) echo "Windows以外のOSなのでFlutter実行はスキップします。" ;;
esac

# ===== 完了 =====
echo "=== セットアップ完了 ==="
echo "Python: $(python --version)"
echo "Flutter: $(flutter --version)"
