# fastapi-practice

FastAPI / SQLModel / Strawberry GraphQL を題材にした学習用リポジトリ。

## セットアップ

```bash
# 全依存関係をインストール
uv sync

# 環境変数ファイルを用意
cp .env.example .env
# 必要に応じて編集 (GOOGLE_API_KEY 等)
```

## 開発

```bash
# 開発サーバ
uv run poe start

# Lint / Format / TypeCheck
uv run poe check
uv run poe lint
```

## テスト

```bash
uv run pytest
```

## Docker

```bash
# 開発用 (compose で起動)
docker compose up -d --wait

# Bake で個別ビルド
docker buildx bake
```

CI は `uv.lock` のハッシュをタグにして dev_runtime イメージを DockerHub に push し、test ジョブはそのイメージを再利用する。

## 依存関係の更新

```bash
# 全部最新化
uv lock --upgrade
uv sync

# 個別追加 / 削除
uv add fastapi
uv remove fastapi
uv add --group analyze jupyter matplotlib
```

## Python バージョン

`.python-version` で 3.14 を固定。Dockerfile では `python:3.14-slim` を使用する。

## マイグレーション

```bash
uv run alembic upgrade head
uv run alembic revision -m "description of changes"
```

## DB が立ち上がるのを待つ (pre-start)

`full-stack-fastapi-template` の `backend_pre_start.py` 相当のスクリプトを
`src/backend_pre_start.py` に用意。tenacity で `SELECT 1` をリトライする。

```bash
uv run poe pre-start
```

## フロントエンドサンプル

`frontend/` に最小構成の Vite + React + TypeScript サンプルを置いてある。
`/health/` を fetch して結果を表示するだけのデモ。

```bash
cd frontend
npm install
cp .env.example .env
npm run dev   # http://localhost:5173
```

`docker compose up` でも `frontend` サービスが立ち上がる。
バックエンドの CORS は `BACKEND_CORS_ORIGINS` / `FRONTEND_HOST` で制御する
（デフォルトで `http://localhost:5173` を許可済）。

## レポート

- Allure: <https://hirotokirimaru.github.io/fastapi-practice>

## 参考

- <https://github.com/tiangolo/full-stack-fastapi-template>
