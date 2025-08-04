#!/usr/bin/env bash
set -e

echo "=== Python 環境構築 ==="
if [ -f requirements.txt ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt が見つかりません。スキップします。"
fi

echo "=== Flutter SDK チェック ==="
# Flutter SDKが無ければclone
FLUTTER_VERSION=3.19.0
FLUTTER_DIR="$HOME/flutter"
if ! command -v flutter &> /dev/null; then
    if [ ! -d "$FLUTTER_DIR" ]; then
        git clone https://github.com/flutter/flutter.git -b $FLUTTER_VERSION $FLUTTER_DIR
    else
        echo "既存のFlutter SDKを使用します"
    fi
    export PATH="$FLUTTER_DIR/bin:$PATH"
    flutter doctor
else
    echo "既にFlutter SDKがインストールされています"
fi

echo "=== Flutter依存関係取得 ==="
flutter pub get

echo "=== Pythonテスト実行 ==="
if command -v pytest &> /dev/null; then
    pytest || { echo "Pythonテスト失敗"; exit 1; }
else
    echo "pytest が見つかりません。インストールします..."
    pip install pytest
    pytest || { echo "Pythonテスト失敗"; exit 1; }
fi

echo "=== Flutterテスト実行 ==="
flutter test || { echo "Flutterテスト失敗"; exit 1; }

echo "=== 動作確認（Python） ==="
if [ -f src/port_scan.py ]; then
    python src/port_scan.py || { echo "Pythonスクリプト実行失敗"; exit 1; }
else
    echo "src/port_scan.py が見つかりません。スキップします。"
fi

echo "=== 動作確認（Flutter / Windowsビルド） ==="
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    flutter run -d windows || { echo "Flutterアプリ実行失敗"; exit 1; }
else
    echo "Windows以外のOSなのでFlutter実行はスキップします。"
fi

echo "=== セットアップ完了 ==="
echo "Python: $(python --version)"
echo "Flutter: $(flutter --version)"
