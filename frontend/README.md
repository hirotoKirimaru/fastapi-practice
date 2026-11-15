# frontend (sample)

最小構成の Vite + React + TypeScript サンプル。FastAPI バックエンドの
`GET /health/` を呼び出して結果を表示するだけ。

## 依存関係

```bash
cd frontend
npm install
cp .env.example .env
```

## 開発

```bash
npm run dev   # http://localhost:5173
```

バックエンドは別途 `uv run poe start`、または `docker compose up` で起動する。
バックエンドの URL を変えたい場合は `frontend/.env` の `VITE_API_BASE_URL` を編集する。

## Docker Compose

`infra/compose.yml` に `frontend` サービスがあり、リポジトリ直下で
`docker compose -f infra/compose.yml up` するとバックエンド + DB + frontend (5173 番) がまとめて立ち上がる
（frontend は profile に入っているので `infra/.env` に `COMPOSE_PROFILES=frontend` が必要）。
