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

```
rye sync

rye add pytest
rye add --dev pytest

```