# Layered Architecture Sample (FastAPI + Jinja2 + S3)

Simple Layered Architecture (3層: UI / Application / Infrastructure) のサンプルです。
セッションとフィードバックはS3に保存します。

## 依存関係
- Python 3.11+
- uv

## セットアップ
```bash
uv sync
```

## 実行
```bash
export AWS_REGION=ap-northeast-1
export AWS_S3_BUCKET=your-bucket-name
# 必要なら AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY を設定

uv run uvicorn app.ui.main:app --reload
```

## 仕様メモ
- セッション: `sessions/{session_id}.json`
- フィードバック: `feedback/{session_id}/{timestamp}.json`

