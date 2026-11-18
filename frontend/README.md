# frontend (sample)

Vite + React + TypeScript のサンプル。パッケージ管理とスクリプトの起動は [bun](https://bun.sh)
（版は `package.json` の `packageManager`）。Vite / Vitest 自体は Node で動く。

FastAPI バックエンドの `GET /health/` を表示し、新規登録・ログイン・パスワード再設定メールの依頼ができる。
ログイン後は REST（`GET /users/me`）と GraphQL（`{ me { ... } }`）の両方でユーザを取って表示し、
名前・パスワードの変更、ログアウト、退会ができる。管理者にはユーザの一覧と停止・再開を出す。

バックエンドを叩くコードは `src/api/` にまとめてあり（`client.ts` が REST / GraphQL のクライアント、
`graphql.ts` がクエリと結果の型、`messages.ts` がエラーコードの日本語化）、アプリと e2e テストの両方がこれを使う。

## 依存関係

```bash
cd frontend
bun install
cp .env.example .env
```

`bunfig.toml` で公開から 3 日経っていない版は入れない（乗っ取られたパッケージの悪性版を避ける）。
取得元は `.npmrc` の Takumi Guard。

## 開発

```bash
bun run dev   # http://localhost:5173
```

バックエンドは別途 `uv run poe start`、または `docker compose up` で起動する。
バックエンドの URL を変えたい場合は `frontend/.env` の `VITE_API_BASE_URL` を編集する。

## テスト（Vitest）

`vitest.config.ts` で 2 つのプロジェクトに分けている。

| コマンド | プロジェクト | 中身 |
|---|---|---|
| `bun run test` | unit | jsdom 上でコンポーネントと API クライアントを動かす。`fetch` を差し替えるのでバックエンドは要らない |
| `bun run test:coverage` | unit | 上と同じものをカバレッジ付きで（`coverage/` に出る） |
| `bun run test:e2e` | e2e | Node から本物のバックエンドの REST / GraphQL を叩く。認証（登録・ログイン・ログアウト・自分の更新・パスワード変更・退会・再設定の受け付け）、管理者のユーザ管理、投稿の持ち主チェック、GraphQL の `me` / `createPost` を見る |

e2e は先にバックエンドを起動しておく（起動を最大 30 秒待ち、つながらなければ理由を出して落ちる）。

```bash
# backend/ で（DB は docker compose -f infra/compose.yml up -d --wait db）
uv run poe prestart   # マイグレーションと最初の管理者
uv run poe start

# frontend/ で
bun run test:e2e
# 接続先や管理者を変えるとき（管理者は backend の FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD と揃える）
E2E_API_BASE_URL=http://localhost:8001 E2E_SUPERUSER_PASSWORD=... bun run test:e2e
```

e2e はテスト用の DB を作り直さず、ユニークなメールアドレスでユーザを足していく（何度流しても衝突しない）。
CI では `e2e` ジョブが PostgreSQL を立て、マイグレーション後に uvicorn を起動してから流す。

## Docker Compose

`infra/compose.yml` に `frontend` サービスがあり、リポジトリ直下で
`docker compose -f infra/compose.yml up` するとバックエンド + DB + frontend (5173 番) がまとめて立ち上がる
（frontend は profile に入っているので `infra/.env` に `COMPOSE_PROFILES=frontend` が必要）。
