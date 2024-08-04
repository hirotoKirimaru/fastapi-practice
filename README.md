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

# Ryeの使い方

```bash
rye sync
```
```bash
rye add pytest
rye add --dev pytest

rye run pytest .
```
```bash
rye lock --update-all
```

```bash
rye pin 3.12.4
```

# Dev
```bash
# 
rye run alembic upgrade head

# 
rye run alembic revision -m "description of changes"
```

# 参考にする
- [https://github.com/tiangolo/full-stack-fastapi-template/tree/master]