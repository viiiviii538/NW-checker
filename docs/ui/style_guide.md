# UI Style Guide

業務用ダッシュボード向けの配色・フォント・アイコン指針を示す。

## Colors
- **Primary:** `#1E3A8A` （濃紺、信頼感を与える）
- **Secondary:** `#1D4ED8` （青、操作要素に使用）
- **Accent:** `#EAB308` （黄、注意喚起や強調に使用）
- **Background:** `#F3F4F6` （淡灰、背景色）
- **Danger:** `#DC2626` （赤、エラーや重大な警告）

### Usage
- ステータスバー: Primary 背景に白文字
- メトリクスカード: Secondary をタイトルやボーダーに使用
- リアルタイムログテーブル: Background を行背景に、重大度バッジに Danger/Accent を適用

## Fonts
- **Base:** "Noto Sans JP" を標準とし、可読性を重視
- **Monospace:** "Roboto Mono" をコードやログ表示に使用
- **Headings:** 太さ 600 以上を使用しセクションを明確化

本文は 14px、見出しは 16px 以上を推奨

## Icons
- Material Icons を基本とし、意味の分かりやすいものを選定
- 重大度アイコン: `info`, `warning`, `error` などを用途に応じて使用
- アクションアイコンはラベル併記で誤操作を防止
- アイコンサイズは 24px を基本とし、タップ領域に余白を確保
