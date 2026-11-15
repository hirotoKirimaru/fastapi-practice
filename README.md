# fastapi-practice

FastAPI / SQLModel / Strawberry GraphQL を題材にした学習用リポジトリ。

## ディレクトリ構成

| ディレクトリ | 中身 |
|---|---|
| `backend/` | FastAPI アプリ（`src/`）、テスト、alembic、`pyproject.toml` / `uv.lock`、Dockerfile |
| `frontend/` | Vite + React + TypeScript のサンプルと、その Dockerfile |
| `infra/` | compose（ローカル開発用 `compose.yml` / CI 専用 `compose.ci.yml`）と `docker-bake.hcl` |

Python のコマンド（uv / poe / pytest / alembic）は `backend/` で、compose と bake はリポジトリ直下から実行する。

## セットアップ

```bash
cd backend

# 全依存関係をインストール
uv sync

# 環境変数ファイルを用意（backend で直接動かすとき用）
cp .env.example .env
# 必要に応じて編集 (GOOGLE_API_KEY 等)
```

compose で動かすときは `cp infra/.env.example infra/.env` を使う（compose は `infra/.env` を読む）。

## 開発

```bash
cd backend

# 開発サーバ
uv run poe start

# Lint / Format / TypeCheck
uv run poe check
uv run poe lint
```

## テスト

```bash
cd backend
uv run pytest
```

## Docker

```bash
# 開発用 (compose で起動。リポジトリ直下から)
docker compose -f infra/compose.yml up -d --wait

# Bake で個別ビルド
docker buildx bake -f infra/docker-bake.hcl
```

毎回 `-f` を付けたくなければ `export COMPOSE_FILE=infra/compose.yml` しておく。
compose のプロジェクト名は `name: fastapi-practice` で固定してあるので、
コンテナ名やボリューム名は以前（直下に compose.yml があったとき）と変わらない。

CI は `backend/uv.lock` のハッシュをタグにして dev_runtime イメージを DockerHub に push し、test ジョブはそのイメージを再利用する。
CI では `infra/compose.yml` を使わず、CI 専用の `infra/compose.ci.yml` を単体で使う（`COMPOSE_FILE=infra/compose.ci.yml`）。
テストに要る api / db / storage / relay だけを起動し、永続化はしない（名前付きボリューム無し・DB は tmpfs・
binlog 無効・healthcheck あり）。ポート公開とソースのバインドマウントもしない。
ローカルの `docker compose up` の挙動は変えていない。

## DB (PostgreSQL)

`infra/compose.yml` の `db` は `postgres:18-alpine`。ドライバは psycopg 3 で、アプリ（非同期）と
alembic / `migrate_db.py`（同期）の両方が同じ設定 `DATABASE_URL` を使う。

- コンテナ内の既定: `postgresql+psycopg://postgres:postgres@db:5432/demo`（`src/helper/config.py`）
- ホストから: `postgresql+psycopg://postgres:postgres@localhost:35432/demo`（`backend/.env.example`）
- テスト本体は従来どおりオンメモリの SQLite。PostgreSQL は CI のマイグレーション確認に使う

## ストレージ (S3)

MinIO の公開イメージが Docker Hub と quay.io の両方から無くなったため、`storage` は
S3 互換モックの [adobe/s3mock](https://github.com/adobe/S3Mock) を使う。

- ホストからのエンドポイントは `http://localhost:9090`（MinIO 時代の 9000 から変更）
- コンテナ内のアプリからは従来どおり `localhost:9000`。`relay` (socat) が 9000 で受けて 9090 へ渡す
- バケットは起動時に `COM_ADOBE_TESTING_S3MOCK_STORE_INITIAL_BUCKETS` で作られる
- **MinIO のコンソール UI (`:9001`) は無くなった**

## 依存関係の更新

```bash
cd backend

# 全部最新化
uv lock --upgrade
uv sync

# 個別追加 / 削除
uv add fastapi
uv remove fastapi
uv add --group analyze jupyter matplotlib
```

## Python バージョン

`backend/.python-version` で 3.15 を固定。`backend/Dockerfile` では `python:3.15-slim` を使用する。

## マイグレーション

```bash
cd backend
uv run alembic upgrade head
uv run alembic revision -m "description of changes"
```

## DB が立ち上がるのを待つ (pre-start)

`full-stack-fastapi-template` の `backend_pre_start.py` 相当のスクリプトを
`backend/src/backend_pre_start.py` に用意（`backend/` で実行する）。tenacity で `SELECT 1` をリトライする。

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

`frontend` は compose の profile に入れてある。`infra/.env.example` に
`COMPOSE_PROFILES=frontend` があるので、`cp infra/.env.example infra/.env` してあれば
`docker compose -f infra/compose.yml up` で一緒に立ち上がる（`docker compose -f infra/compose.yml up frontend` と
名指しすれば `.env` が無くても起動する）。
バックエンドの CORS は `BACKEND_CORS_ORIGINS` / `FRONTEND_HOST` で制御する
（デフォルトで `http://localhost:5173` を許可済）。

## レポート

- Allure: <https://hirotokirimaru.github.io/fastapi-practice>

## 参考

- <https://github.com/tiangolo/full-stack-fastapi-template>
