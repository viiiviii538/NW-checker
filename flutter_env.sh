#!/bin/bash
set -e

# Flutter SDKパス設定（Codex環境用）
export PATH="$PATH:/usr/local/flutter/bin"

# Flutter依存解決
flutter pub get

echo "✅ Flutter environment ready."
