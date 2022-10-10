FROM python:3.9
# NOTE: 3.10.4 にアップグレードすると色々と動かない
#FROM python:3.10.4
ENV PYTHONUNBUFFERED=1

COPY ./src /src
WORKDIR /src

RUN pip install poetry

# poetryの定義ファイルをコピー (存在する場合)
COPY pyproject.toml* poetry.lock* ./

# poetryでライブラリをインストール (pyproject.tomlが既にある場合)
RUN poetry config virtualenvs.in-project true
# インストール
# RUN if [ -f pyproject.toml ]; then poetry install ; fi
RUN poetry install

# uvicornのサーバーを立ち上げる
#ENTRYPOINT ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
