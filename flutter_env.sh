#!/bin/bash
set -e

# スクリプトの場所を基準にプロジェクトルートへ移動
cd "$(dirname "$0")"

# Flutter SDKパス設定（Codex環境用）
export PATH="$PATH:$HOME/flutter/bin"

# Flutter依存解決
flutter pub get

echo "✅ Flutter environment ready."
