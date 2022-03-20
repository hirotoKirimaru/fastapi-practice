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
docker-compose run --entrypoint "poetry install" demo-app
```

```bash
docker-compose build --no-cache
```