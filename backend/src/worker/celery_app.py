"""Celery の設定。ブローカー / 結果の保存先は Valkey（Redis 互換。infra/compose.yml の kvs）。
Valkey は Redis のプロトコルそのままなので、URL は redis:// で書く。

起動（infra/compose.yml の worker サービスと同じ）:
    uv run celery -A src.worker.celery_app worker --loglevel=INFO -O fair

速さのための考え方:
- 並列数は既定で CPU コア数（prefork = プロセス並列なので CPU を使う処理でも GIL に縛られない）。
  `--concurrency` で変えられる。I/O 待ちが中心なら CPU 数より多めにしてよい
- `-O fair`: 空いているプロセスにだけタスクを渡す。処理時間がばらつくときに詰まりにくい
- prefetch（1 プロセスが先読みするタスク数）は既定 4。短いタスクが大量なら増やすと速く、
  長いタスクが混じるなら 1 にすると偏りが減る（CELERY_WORKER_PREFETCH_MULTIPLIER で変更）
"""

import os

from celery import Celery

from src.helper.config import settings

celery_app = Celery(
    "fastapi-practice",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # 処理が終わってから ack する。worker が落ちたら別の worker にタスクが再配送される
    # （その代わりタスクは「2 回実行されても壊れない」ように書く）
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=int(
        os.environ.get("CELERY_WORKER_PREFETCH_MULTIPLIER", "4")
    ),
    # メモリリーク対策に、一定数こなしたプロセスは作り直す
    worker_max_tasks_per_child=1000,
    result_expires=60 * 60,
    broker_connection_retry_on_startup=True,
)
