#!/bin/bash
set -e

# スクリプトの場所を基準にプロジェクトルートへ移動
cd "$(dirname "$0")"

# Flutter SDKパス設定（Codex環境用）
export PATH="$PATH:$HOME/flutter/bin"

# pubspec.yaml がある時だけ flutter pub get 実行
if [ -f "pubspec.yaml" ]; then
  flutter pub get
  echo "✅ Flutter environment ready."
else
  echo "⚠️ pubspec.yaml が見つからないので Flutter セットアップはスキップしました。"
fi
