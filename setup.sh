#!/usr/bin/env bash
set -e

# ===== 環境変数設定 =====
export DEBIAN_FRONTEND=noninteractive
PROJECT_DIR="/workspace/NW-checker/nw_checker"
FLUTTER_VERSION=3.32.8   # Dart 3.7.2 同梱の安定版
FLUTTER_DIR="$HOME/flutter"
export PATH="$FLUTTER_DIR/bin:$PATH"

echo "=== プロジェクトルートへ移動 ==="
cd "$PROJECT_DIR"

# ===== OSパッケージインストール =====
echo "=== OSパッケージインストール ==="
apt-get update -y
apt-get install -y git curl unzip nmap clang libgtk-3-dev python3-venv

# ===== Python環境構築 =====
echo "=== Python 仮想環境構築 ==="
python3 -m venv .venv
source .venv/bin/activate

echo "=== Python依存関係インストール ==="
pip install --upgrade pip
pip install python-nmap pytest
REQ_FILE="../requirements.txt"
[ -f "requirements.txt" ] && REQ_FILE="requirements.txt"

if [ -f "$REQ_FILE" ]; then
    pip install -r "$REQ_FILE"
else
    echo "ルートの requirements.txt が見つかりません。スキップします。"
fi

# ---- 追加: black が無ければ入れておく（整形用・任意）----
if ! command -v black >/dev/null 2>&1; then
  pip install black || true
fi

# ===== Flutter SDK セットアップ =====
echo "=== Flutter SDK チェック ==="
if ! command -v flutter &> /dev/null; then
    if [ ! -d "$FLUTTER_DIR" ]; then
        echo "Flutter SDKをインストール中..."
        git clone --depth 1 https://github.com/flutter/flutter.git -b $FLUTTER_VERSION $FLUTTER_DIR
    else
        echo "既存のFlutter SDKを使用します"
    fi
    # 追加: インストール後にPATHを再反映
    export PATH="$FLUTTER_DIR/bin:$PATH"
else
    echo "既にFlutter SDKがインストールされています"
    # 追加: 念のためPATHを再反映
    export PATH="$FLUTTER_DIR/bin:$PATH"
fi

flutter precache || true

# 追加: PATH 永続化（別シェルでも flutter を使えるように）
if [ -w "$HOME" ] && ! grep -q "$FLUTTER_DIR/bin" "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/flutter/bin:$PATH"' >> "$HOME/.bashrc" || true
fi

# ===== Flutter Doctor =====
echo "=== Flutter Doctor 実行 ==="
flutter doctor || echo "Flutter Doctor 警告あり（続行）"

# ===== Flutter依存関係取得 =====
echo "=== Flutter依存関係取得 ==="
flutter pub get || { echo "flutter pub get 失敗"; exit 1; }

# ---- 追加: 改行統一(.gitattributes) & Git設定 ----
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

# ---- 追加: Formatter 実行（既存機能を壊さない範囲で）----
echo "=== コード整形 (Dart / Python) ==="
# Dart
if command -v dart >/dev/null 2>&1; then
  dart format . || true
fi
# Python
if command -v black >/dev/null 2>&1; then
  black . || true
fi

# ---- 追加: 競合マーカー検出（ある場合は早期に知らせる）----
echo "=== マージ競合マーカー検出 ==="
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . >/dev/null 2>&1; then
    echo "ERROR: マージ競合マーカーを検出しました。解消してください。"
    git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . || true
    # 既存フローを止め過ぎないため終了コードは非致命（0）にせず、通知で継続するなら下行をコメントアウト
    # exit 1
  fi
fi

# ---- 追加: pre-commit フック自動配置（競合検出＆整形）----
echo "=== Git pre-commit フック設定 ==="
HOOK=".git/hooks/pre-commit"
if [ -d ".git/hooks" ] && [ ! -f "$HOOK" ]; then
cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
set -e

# 競合マーカー検出
if git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . >/dev/null 2>&1; then
  echo "[pre-commit] Merge conflict markers detected. Resolve them before commit."
  git grep -n '<<<<<<< \|=======\|>>>>>>>' -- .
  exit 1
fi

# 整形（差分全体）
if command -v dart >/dev/null 2>&1; then
  dart format .
fi
if command -v black >/dev/null 2>&1; then
  black .
fi

exit 0
EOF
  chmod +x "$HOOK"
fi

# ===== Pythonテスト実行 =====
echo "=== Pythonテスト実行 ==="
pytest || echo "Pythonテスト失敗（続行）"

# ===== Flutterテスト実行 =====
echo "=== Flutterテスト実行 ==="
flutter test || echo "Flutterテスト失敗（続行）"

# ===== Python動作確認 =====
echo "=== 動作確認（Python） ==="
if [ -f src/scans/ports.py ]; then
    python src/scans/ports.py || echo "Pythonスクリプト実行失敗（続行）"
else
    echo "src/scans/ports.py が見つかりません。スキップします。"
fi

# ===== Flutter動作確認（Windowsのみ） =====
echo "=== 動作確認（Flutter / Windowsビルド） ==="
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    flutter run -d windows || echo "Flutterアプリ実行失敗（続行）"
else
    echo "Windows以外のOSなのでFlutter実行はスキップします。"
fi

# ===== セットアップ完了 =====
echo "=== セットアップ完了 ==="
echo "Python: $(python --version)"
echo "Flutter: $(flutter --version)"
