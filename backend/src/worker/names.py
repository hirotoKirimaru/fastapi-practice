"""タスク名の定義。API（投入側）と worker（実行側）の両方がここだけを共有する。

API は `celery_app.send_task(名前, args=...)` で投入するので、タスクの実装（src/worker/tasks.py）や
その依存を import しなくて済む。
"""

CREATE_USER_PROFILE = "user_profiles.create"
