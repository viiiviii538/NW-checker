#!/usr/bin/env bash
set -e

# ===== 環境変数設定 =====
export DEBIAN_FRONTEND=noninteractive
PROJECT_DIR="/workspace/NW-checker/nw_checker"
FLUTTER_VERSION=3.32.8   # Dart 3.8.1 同梱の安定版
FLUTTER_DIR="$HOME/flutter"
export PATH="$FLUTTER_DIR/bin:$PATH"

# 追加: リポジトリ（ルート）推定
REPO_DIR="$(dirname "$PROJECT_DIR")"
[ -d "$REPO_DIR/.git" ] || REPO_DIR="$PROJECT_DIR"

echo "=== プロジェクトルートへ移動 ==="
cd "$PROJECT_DIR"

# ===== OSパッケージインストール =====
echo "=== OSパッケージインストール ==="
apt-get update -y
apt-get install -y git curl unzip nmap clang libgtk-3-dev python3-venv

# ===== Python環境構築 =====
echo "=== Python 仮想環境構築 ==="
python3 -m venv .venv
# 追加: 仮想環境有効化前に安全のため存在確認
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  echo "ERROR: .venv/bin/activate が見つかりません"; exit 1
fi

echo "=== Python依存関係インストール ==="
pip install --upgrade pip
pip install python-nmap pytest  # 既存要件
# 追加: black はあれば使う（整形用）。失敗しても続行。
pip install --upgrade black || true
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt が見つかりません。スキップします。"
fi

# ===== Flutter SDK セットアップ =====
echo "=== Flutter SDK チェック ==="
if ! command -v flutter &> /dev/null; then
    if [ ! -d "$FLUTTER_DIR" ]; then
        echo "Flutter SDKをインストール中..."
        git clone --depth 1 https://github.com/flutter/flutter.git -b "$FLUTTER_VERSION" "$FLUTTER_DIR"
    else
        echo "既存のFlutter SDKを使用します"
    fi
    # 追加: インストール後にPATHを確実に再反映
    export PATH="$FLUTTER_DIR/bin:$PATH"
else
    echo "既にFlutter SDKがインストールされています"
    # 追加: 念のためPATHを再反映
    export PATH="$FLUTTER_DIR/bin:$PATH"
fi

# 追加: PATH 永続化（別プロセスでも有効）
if ! grep -q "$FLUTTER_DIR/bin" "$HOME/.bashrc" 2>/dev/null; then
  echo "export PATH=\"$FLUTTER_DIR/bin:\$PATH\"" >> "$HOME/.bashrc"
fi

# 追加: 再チェック
if ! command -v flutter &> /dev/null; then
    echo "flutter コマンドが見つかりません。PATH設定を確認してください。"; exit 1
fi

# ===== Flutter Doctor =====
echo "=== Flutter Doctor 実行 ==="
flutter doctor || echo "Flutter Doctor 警告あり（続行）"

# ===== Flutter依存関係取得 =====
echo "=== Flutter依存関係取得 ==="
flutter pub get || { echo "flutter pub get 失敗"; exit 1; }

# === ここから“追記ユーティリティ”: 競合撲滅＆整形＆改行統一 ==================

echo "=== 改行統一設定（.gitattributes） ==="
# リポジトリ直下に .gitattributes（なければ作成）
if [ ! -f "$REPO_DIR/.gitattributes" ]; then
  cat > "$REPO_DIR/.gitattributes" <<'EOF'
* text=auto eol=lf
*.dart text eol=lf
*.py   text eol=lf
*.sh   text eol=lf
EOF
  git -C "$REPO_DIR" add .gitattributes || true
fi
# Windows系の自動CRLF変換を抑止（安全のため）
git -C "$REPO_DIR" config core.autocrlf false || true

echo "=== 競合マーカー検出（ある場合は即中断） ==="
# 競合マーカーの有無をリポジトリ全体でチェック
if git -C "$REPO_DIR" grep -n '<<<<<<< \|=======\|>>>>>>>' -- . >/dev/null 2>&1; then
  echo "ERROR: merge-conflict markers detected in repository."
  git -C "$REPO_DIR" grep -n '<<<<<<< \|=======\|>>>>>>>' -- .
  exit 1
fi

echo "=== コード整形（失敗してもビルドは続行） ==="
# Dart整形
dart format "$REPO_DIR" || true
# Python整形（blackがあれば）
if command -v black >/dev/null 2>&1; then
  black "$REPO_DIR" || true
fi

echo "=== pre-commit フック自動配置（競合/整形チェック）==="
HOOK="$REPO_DIR/.git/hooks/pre-commit"
if [ -d "$REPO_DIR/.git/hooks" ] && [ ! -f "$HOOK" ]; then
  cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
set -e
# 競合マーカー検出
if git grep -n '<<<<<<< \|=======\|>>>>>>>' -- . >/dev/null 2>&1; then
  echo "[pre-commit] Merge conflict markers detected. Resolve them before commit."
  git grep -n '<<<<<<< \|=======\|>>>>>>>' -- .
  exit 1
fi
# 整形（存在する場合のみ）
command -v dart >/dev/null 2>&1 && dart format .
command -v black >/dev/null 2>&1 && black .
exit 0
EOF
  chmod +x "$HOOK"
fi

# === “追記ユーティリティ”ここまで =============================================

# ===== Pythonテスト実行 =====
echo "=== Pythonテスト実行 ==="
pytest || echo "Pythonテスト失敗（続行）"

# ===== Flutterテスト実行 =====
echo "=== Flutterテスト実行 ==="
flutter test || echo "Flutterテスト失敗（続行）"

# ===== Python動作確認 =====
echo "=== 動作確認（Python） ==="
if [ -f src/port_scan.py ]; then
    python src/port_scan.py || echo "Pythonスクリプト実行失敗（続行）"
else
    echo "src/port_scan.py が見つかりません。スキップします。"
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
