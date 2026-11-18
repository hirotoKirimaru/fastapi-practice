# frontend (sample)

Vite + React + TypeScript のサンプル。FastAPI バックエンドの `GET /health/` を表示し、
新規登録・ログイン（JWT）のあと、ログイン中のユーザを REST（`GET /users/me`）と
GraphQL（`{ me { ... } }`）の両方で取って表示する。

バックエンドを叩くコードは `src/api/` にまとめてあり（`client.ts` が REST / GraphQL のクライアント、
`graphql.ts` がクエリと結果の型）、アプリと e2e テストの両方がこれを使う。

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

## テスト（Vitest）

`vitest.config.ts` で 2 つのプロジェクトに分けている。

| コマンド | プロジェクト | 中身 |
|---|---|---|
| `npm test` | unit | jsdom 上でコンポーネントと API クライアントを動かす。`fetch` を差し替えるのでバックエンドは要らない |
| `npm run test:coverage` | unit | 上と同じものをカバレッジ付きで（`coverage/` に出る） |
| `npm run test:e2e` | e2e | Node から本物のバックエンドの REST / GraphQL を叩く。認証（登録・ログイン・`/users/me`・GraphQL の `me` / `createPost`、不正なトークンの拒否）も見る |

e2e は先にバックエンドを起動しておく（起動を最大 30 秒待ち、つながらなければ理由を出して落ちる）。

```bash
# backend/ で（DB は docker compose -f infra/compose.yml up -d --wait db）
uv run alembic upgrade head
uv run poe start

# frontend/ で
npm run test:e2e
# 接続先を変えるとき
E2E_API_BASE_URL=http://localhost:8001 npm run test:e2e
```

e2e はテスト用の DB を作り直さず、ユニークなメールアドレスでユーザを足していく（何度流しても衝突しない）。
CI では `e2e` ジョブが PostgreSQL を立て、マイグレーション後に uvicorn を起動してから流す。

## Docker Compose

`infra/compose.yml` に `frontend` サービスがあり、リポジトリ直下で
`docker compose -f infra/compose.yml up` するとバックエンド + DB + frontend (5173 番) がまとめて立ち上がる
（frontend は profile に入っているので `infra/.env` に `COMPOSE_PROFILES=frontend` が必要）。
