#!/usr/bin/env bash
# テストを 2 段階で動かす（backend/ で実行する。poe test から呼ぶ）。
#
# 1. 並列（pytest-xdist）で全テスト。捕捉するログは CRITICAL だけにし、SQL の echo も切って
#    メモリと出力を抑える。並列数は PYTEST_WORKERS（既定 auto = CPU コア数、0 なら直列）
# 2. 失敗があったら、失敗したテストだけを直列で再実行する。ログは DEBUG まで出して原因を追う
#
# 終了コードは 1 の結果をそのまま返す。2 で通っても、並列のときだけ落ちるテスト
# （テスト同士の干渉）がある合図なので成功扱いにしない。
set -u

workers="${PYTEST_WORKERS:-auto}"

SQL_ECHO=false uv run pytest -n "$workers" -q --log-level=CRITICAL "$@"
status=$?

# 1 = テストの失敗。それ以外（収集エラーや中断など）は再実行しても意味がない
if [ "$status" -eq 1 ]; then
    echo
    echo "=== 失敗したテストを直列・DEBUG ログで再実行します ==="
    uv run pytest --last-failed --last-failed-no-failures none -p no:xdist \
        -s -o log_cli=true --log-cli-level=DEBUG "$@" || true
fi

exit "$status"
