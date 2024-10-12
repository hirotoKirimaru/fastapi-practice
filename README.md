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
uv lock
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

# 参考にする
- [https://github.com/tiangolo/full-stack-fastapi-template/tree/master]