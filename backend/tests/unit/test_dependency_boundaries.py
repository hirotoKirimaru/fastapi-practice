"""API と worker の依存の境界が崩れていないことを確かめる。

- worker のイメージには API 用の依存（pyproject の api グループ）が入っていない。
  worker のコードがそれらを import すると、本番の worker だけが起動時に落ちる
- API はタスクを名前で投入する（send_task）。タスクの実装を import すると、
  worker の都合で入れた依存が API にも必要になる

import の有無はモジュールのキャッシュに左右されるので、まっさらな別プロセスで調べる。
"""

import json
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]

# pyproject.toml の api グループにしか無いパッケージ（import 名）。
# greenlet も api グループだが、SQLAlchemy が「入っていれば読み込む」任意の依存なので外す
# （全部入りの開発環境では読み込まれ、worker のイメージでは入っていないので読み込まれない）
API_ONLY_MODULES = (
    "fastapi",
    "starlette",
    "strawberry",
    "polars",
    "boto3",
    "pwdlib",
    "tenacity",
    "google.genai",
    "sentry_sdk",
)


def _loaded_modules(code: str) -> set[str]:
    script = f"{code}\nimport json, sys\nprint(json.dumps(sorted(sys.modules)))"
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    return set(json.loads(result.stdout.splitlines()[-1]))


def test_worker_does_not_import_api_only_dependencies() -> None:
    loaded = _loaded_modules("import src.worker.tasks")
    leaked = [m for m in API_ONLY_MODULES if m in loaded]
    assert leaked == [], f"worker のコードが API 専用の依存を読み込んでいる: {leaked}"


# src.main はタスクを投入する src.api.routers.job も含めて全ルーターを読み込むので、
# これ 1 つで足りる（以前は job 単体でも別プロセスを起こしていたが、src.main の部分集合で冗長だった）
def test_api_does_not_import_task_implementations() -> None:
    loaded = _loaded_modules("import src.main")
    assert "src.worker.tasks" not in loaded, (
        "API がタスクの実装を import している。send_task で名前を使って投入すること"
    )
