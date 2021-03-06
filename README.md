# fastapi-practice
FastAPIを素振りする

# ログイン
```bash
docker-compose run api bash
```

# 起動
```bash
docker-compose up -d
```

# 起動しない？
```bash
uvicorn main:app --reload
```

# Swagger

```bash
http://127.0.0.1/docs
```

# 参考元

https://zenn.dev/sh0nk/books/537bb028709ab9


```bash
docker-compose run \
  --entrypoint "poetry init \
    --name demo-app \
    --dependency fastapi \
    --dependency uvicorn[standard]" \
  demo-app
```
```bash
docker-compose run --entrypoint "poetry install" api
```

```bash
docker-compose build --no-cache
```


```bash
# poetryで開発者モードでインストール
docker-compose exec demo-app poetry add -D pytest-asyncio aiosqlite httpx
```

```bash
# ログイン
docker-compose run api bash
```

# DBマイグレーション
```bash

docker-compose exec demo-app poetry run python -m api.migrate_db
```

# テスト
```bash
docker-compose run --entrypoint "poetry run pytest --asyncio-mode=strict" api
```

```bash
docker-compose run --rm api poetry run pytest --asyncio-mode=strict
```

ログインした場合のコマンド。
```bash
poetry run pytest --asyncio-mode=strict
poetry run pytest --asyncio-mode=strict --pdb
```