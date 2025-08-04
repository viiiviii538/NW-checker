#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Installing Flutter SDK ==="
# Flutter SDK バージョン指定（必要に応じて変更）
FLUTTER_VERSION=3.19.0
FLUTTER_DIR="$HOME/flutter"

if [ ! -d "$FLUTTER_DIR" ]; then
  git clone https://github.com/flutter/flutter.git -b $FLUTTER_VERSION $FLUTTER_DIR
else
  echo "Flutter SDK already exists. Skipping clone."
fi

# Flutter PATH設定
export PATH="$FLUTTER_DIR/bin:$PATH"
flutter doctor

echo "=== Getting Flutter dependencies ==="
flutter pub get

echo "=== Setup Complete! ==="
echo "Python: $(python --version)"
echo "Flutter: $(flutter --version)"
