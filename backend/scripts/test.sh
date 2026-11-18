#!/usr/bin/env bash
# テストを 2 段階で動かす（backend/ で実行する。poe test から呼ぶ）。
#
# 1. 全テスト。捕捉するログは CRITICAL だけにし、SQL の echo も切ってメモリと出力を抑える。
#    並列数は PYTEST_WORKERS（既定 0 = 直列、auto = CPU コア数、数字ならその数）。
#    既定を直列にしているのは、Celery の worker の停止待ち（約 4 秒）を無くしたあとは、
#    ワーカーごとのアプリの import とマイグレーションの方が高くつき、直列の方が速いため
#    （手元の 4 コアで 直列 約 8.6 秒・316MB / auto 約 9.5 秒・1.1GB）。テストが増えたら auto にする
# 2. 失敗があったら、失敗したテストだけを直列で再実行する。ログは DEBUG まで出して原因を追う
#
# 終了コードは 1 の結果をそのまま返す。2 で通っても、並列のときだけ落ちるテスト
# （テスト同士の干渉）がある合図なので成功扱いにしない。
set -u

workers="${PYTEST_WORKERS:-0}"

# --durations: 遅いテスト上位 10 件を毎回出す（どこに時間がかかっているかを見えるようにする）
# --dist loadfile（並列のときだけ効く）: 同じファイルのテストを同じワーカーに寄せる。Celery の worker を
# 使うテスト（tests/unit/worker/test_tasks.py）が散らばると、worker の起動・停止をワーカーごとに払うため。
# （--dist loadgroup + xdist_group の方が細かく選べるが、pytest 9.2 + pytest-xdist 3.8 では効かなかった）
SQL_ECHO=false uv run pytest -n "$workers" --dist loadfile -q --log-level=CRITICAL --durations=10 "$@"
status=$?

# 1 = テストの失敗。それ以外（収集エラーや中断など）は再実行しても意味がない
if [ "$status" -eq 1 ]; then
    echo
    echo "=== 失敗したテストを直列・DEBUG ログで再実行します ==="
    uv run pytest --last-failed --last-failed-no-failures none -p no:xdist \
        -s -o log_cli=true --log-cli-level=DEBUG "$@" || true
fi

exit "$status"
