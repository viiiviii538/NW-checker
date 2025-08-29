# Codex Agent Guide

## プロジェクト概要
Python + Flutter 製のネットワーク診断ツール「NWC伝説」。
社内ネットワーク機器をスキャンし、脆弱性を判定・採点する。

## 実装ルール
- 既存機能は壊さない（後方互換性必須）
- Python側は `src/` に配置、Flutter側は `nw_checker/lib/` に配置
- ファイル・関数名は英語、処理説明は日本語コメント可

## 開発フロー
1. 機能追加や修正は必ず新しいブランチを切る
2. 実装後は単体テストを作成し、PRに含める
3. テストが全て通ることを確認してからマージ

## テスト
- Run: bash codex_run_tests.sh
- Do NOT run `pytest` directly.
- Do NOT run `flutter test` directly.
- 確認: "== codex_run_tests.sh START (FORCE_RUN_PYTEST=1) ==" がログ先頭に出ること

## セットアップ
- `setup.sh` と `flutter_env.sh` を必ず実行してから作業
