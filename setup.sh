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
        git clone --depth 1 https://github.com/flutter/flutter.git -b $FLUTTER_VERSION $FLUTTER_DIR
    else
        echo "既存のFlutter SDKを使用します"
    fi
else
    echo "既にFlutter SDKがインストールされています"
fi

# ===== Flutter Doctor =====
echo "=== Flutter Doctor 実行 ==="
flutter doctor || echo "Flutter Doctor 警告あり（続行）"

# ===== Flutter依存関係取得 =====
echo "=== Flutter依存関係取得 ==="
flutter pub get || { echo "flutter pub get 失敗"; exit 1; }

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
