# UI Style Guide

業務用ダッシュボード向けの配色・フォント・アイコン指針を示す。

## Colors

| Role | Hex | Usage |
| ---- | ---- | ----- |
| Primary | `#1E3A8A` | 濃紺。ヘッダーや主要アクションに使用し信頼感を演出 |
| Secondary | `#1D4ED8` | 青。ボタンなどの操作要素に使用 |
| Accent | `#EAB308` | 黄。注意喚起や強調に使用 |
| Background | `#F3F4F6` | 淡灰。画面全体の背景色 |
| Danger | `#DC2626` | 赤。エラーや重大な警告に使用 |

## Fonts

- **Base:** "Noto Sans JP" を標準とし、可読性を重視
- **Monospace:** "Roboto Mono" をコードやログ表示に使用
- **Headings:** 太さ 600 以上を使用しセクションを明確化
- **Fallback:** システムフォントを順次使用し文字化けを防止

## Icons

- Material Icons を基本とし、意味の分かりやすいものを選定
- 重大度アイコン: `info`, `warning`, `error` などを用途に応じて使用
- アクションアイコンはラベル併記で誤操作を防止
- アイコンカラーはテキストと十分なコントラストを確保
