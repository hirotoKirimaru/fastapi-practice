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

## レポート

- Allure: <https://hirotokirimaru.github.io/fastapi-practice>

## 参考

- <https://github.com/tiangolo/full-stack-fastapi-template>
