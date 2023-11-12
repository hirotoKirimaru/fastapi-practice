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
docker-compose exec api poetry add -D pytest-asyncio aiosqlite httpx
# やりたいけど動かない
docker-compose exec api poetry add pandas
```

```bash
# ログイン
docker-compose run api bash
```

# ライブラリを追加する

```bash
# 次のコマンドが動かないので。
poerty add pandas

# Response
# failed to create /root/.cache/pypoetry/cache/repositories/PyPI/_http/9/7/d/d/9/ec3f3c34427c-68eba740.67-179095377644821737
```

1. poetry.lockファイルを削除する
1. pyproject.tomlファイルに自分で追記する
1. Dockerのビルド時、または起動時にpoetryのインストールを行う
1. 動く！

```bash
# 起動時じゃないとつかえない？
docker-compose run --entrypoint "poetry install" api
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



```bash
# LinterのBlackをつかう？？？？
# black
pip install black
```


```bash
# 単体ファイル
docker-compose run --entrypoint "poetry run pytest -s tests/unit/models/test_search.py --asyncio-mode=strict" api
```