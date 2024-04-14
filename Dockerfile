ARG PYTHON_BASE_IMAGE='python'

FROM ${PYTHON_BASE_IMAGE}:3.12.2 AS builder
#FROM python:3.11
# NOTE: 3.10.4 にアップグレードすると色々と動かない
#FROM python:3.10.4

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/src:$PYTHONPATH"
ENV RYE_HOME="/opt/rye"
ENV PATH="$RYE_HOME/shims:$PATH"


COPY src /src
#COPY pyproject.toml pyproject.toml
#poetryのデフォルトパスになる
#ENV PYTHONPATH=/src

WORKDIR /src

RUN curl -sSf https://rye-up.com/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash

RUN rye config --set-bool behavior.global-python=true && \
   rye config --set-bool behavior.use-uv=true

# README.MDもマウントさせる必要あり
RUN --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
   --mount=type=bind,source=requirements.lock,target=requirements.lock \
   --mount=type=bind,source=requirements-dev.lock,target=requirements-dev.lock \
   --mount=type=bind,source=.python-version,target=.python-version \
   rye sync --no-lock # lockファイルを作成しようとすると権限エラー
#    --mount=type=bind,source=.python-version,target=.python-version \
#    --mount=type=bind,source=README.md,target=README.md \
#    rye sync --no-lock # lockファイルを作成しようとすると権限エラー
#    rye sync --no-dev --no-lock
#RUN rye sync

# venvのactivate?
RUN . .venv/bin/activate

#COPY pyproject.toml* ./

# こうしないとダメ？
#RUN rye install pytest ruff uvicorn
# RUN rye install fastapi
# RUN #rye install uvicorn
# RUN rye sync
# RUN rye sync --no-lock
# RUN rye sync --no-dev --no-lock




#RUN pip install poetry

# poetryの定義ファイルをコピー (存在する場合)
#COPY pyproject.toml* poetry.lock* ./

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
#RUN poetry config virtualenvs.in-project true
#RUN if [ -f pyproject.toml ]; then poetry install ; fi

# uvicornのサーバーを立ち上げる
#ENTRYPOINT ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
#CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
# CMD ["/src/.venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
# rye run uvicorn src.main:app --host 0.0.0.0 --reload
CMD ["rye", "run", "uvicorn", "src.main:app", "--reload"]

# TODO: マルチビルドステージがあるらしい
#FROM ${PYTHON_BASE_IMAGE}:3.12.2 AS production
#COPY --from=builder /opt/rye /opt/rye
#
#ENV RYE_HOME="/opt/rye"
#ENV PATH="$RYE_HOME/shims:$PATH"
#ENV PYTHONUNBUFFERED True
#
#RUN rye config --set-bool behavior.global-python=true && \
# rye config --set-bool behavior.use-uv=true
#
#CMD ["rye", "run", "uvicorn", "src.main:app", "--reload"]
