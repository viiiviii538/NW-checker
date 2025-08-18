# 開発メモ

## 2025-08-18 API検証
- `uvicorn src.server:app --reload` で起動。ログに `Uvicorn running on http://127.0.0.1:8000` を確認。
- `curl -v http://localhost:8000/static_scan` により 200 OK と JSON レスポンスを取得。
- `curl -v http://localhost:8000/dynamic_scan` は 404 Not Found を返却。動的スキャン API は `src.server` では提供されていないため、`src.api:app` や `/scan/dynamic/*` のエンドポイントを利用する必要がある。

