# README

```bash
rye sync
# activateを実行する
. .venv/bin/activate
```

```bash
# Docker内部でrequirements.lockが作成できない？
# Windows 等々で行う必要あり
```

# 自動Linter

違う意図があるので別々に入れておく


```bash
ruff . --fix
black .
```

# OpenAPIの定義ファイル
```bash
http://localhost:8000/docs
```

# fastapi-practice

Describe your project here.

```bash
# 開発環境でビルド
#普通にビルドでoK
#docker compose build --target development
# 本番環境でビルド
#docker compose build --target production
BUILD_TARGET=development docker compose build
```

# Rye か uvの使い方

```bash
uv sync
```
```bash
uv add pytest
uv add --dev pytest

uv run pytest .
```
```bash
# update
uv lock --upgrade

# pyprojectの更新
uv remove fastapi
uv add fastapi

#uv lock
#rye lock --update-all
```

```bash
uv python pin 3.13
#rye pin 3.12.4
```

# Dev
```bash
# 
uv run alembic upgrade head

# 
uv run alembic revision -m "description of changes"
```

```bash
uv self update
```

```bash
# TODO pytypeをいい感じに使えるようにしたい

```

```bash
# rye.tools.scripts
rye lint
rye start
rye production


```

# Allureのページ
- [https://hirotokirimaru.github.io/fastapi-practice]

# 参考にする
- [https://github.com/tiangolo/full-stack-fastapi-template/tree/master]

# Docker buildxを素振り

```bash
docker buildx bake
#docker buildx bake --set BUILD_TARGET=production

# 環境変数を指定する場合
## .env でよければ指定不要。基本的にアプリと混ざらせたくなかったので、これを分ける
export $(cat docker.env | xargs) && docker buildx bake

export $(cat docker.env | xargs) && docker buildx bake --set common.target=production

#export $(cat docker.env | xargs) && docker buildx bake api --set common.target=prod_runtime --push --set *.tags="kirimaru/fastapi-practice_prod-runtime:latest,kirimaru/fastapi-practice_prod-runtime:0.0.1"
# 事前にランタイムだけビルド
export $(cat docker.env | xargs) && docker buildx bake api --set common.target=prod_runtime --push --set *.tags="kirimaru/fastapi-practice_prod-runtime:0.0.1"
# 本番ビルド
export $(cat docker.env | xargs) && docker buildx bake api --set common.target=prod --push --set *.tags="kirimaru/fastapi-practice_prod:0.0.1"
# 本番起動
docker run --rm kirimaru/fastapi-practice_prod:0.0.1

# これで一緒にタグ付けできそう
docker buildx bake --set *.tags="myapp/api:latest,myapp/api:v1.0"

# 動的にやるならこっち
TAG=v1.0 docker buildx bake
docker buildx bake --push --set TAG=v1.0

# 指定してビルドしたいとき
docker buildx bake api worker
```


### CI運用
```bash
## 既存のRuntimeイメージからuv.lockを吐き出させる
docker create --name temp_container kirimaru/fastapi-practice_prod-runtime:0.0.1
docker cp temp_container:/app/uv.lock ./uv.lock.docker
docker rm temp_container

## 差分チェック[docker-bake.hcl](docker-bake.hcl)
diff uv.lock uv.lock.docker

### 差分チェック？
if [ $? -eq 0 ]; then
    echo "ファイルに差分はありません"
elif [ $? -eq 1 ]; then
    echo "ファイルに差分があります"
else
    echo "diffコマンドでエラーが発生しました"
fi
```