from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata = SQLModel.metadata

# autogenerate / alembic check がモデルと DB を比べられるよう、全モデルを読み込んで
# SQLModel.metadata に登録する（読み込まないと「全テーブルを消す」差分に見えてしまう）
import src.models.access_token
import src.models.minors
import src.models.organization
import src.models.post
import src.models.task
import src.models.user  # noqa: F401
from src.helper.config import settings

# 接続先は既定でアプリと同じ設定（DATABASE_URL）から取る。alembic.ini には書かない。
# テスト（tests/conftest.py）はテスト用 DB の URL を先に入れてから呼ぶので、その場合は上書きしない
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# マイグレーションにだけ存在し、モデルを持たないテーブル。
# relation_timelines は部分ユニークインデックスの題材として DB 側だけで定義している
MIGRATION_ONLY_TABLES = {"relation_timelines"}


def include_object(obj, name, type_, reflected, compare_to):  # type: ignore[no-untyped-def]
    # テーブルを比較対象から外せば、その列・インデックス・制約も比べられない
    return not (type_ == "table" and name in MIGRATION_ONLY_TABLES)


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """オンラインモードでのマイグレーション実行"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.
#
#     In this scenario we need to create an Engine
#     and associate a connection with the context.
#
#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )
#
#     with connectable.connect() as connection:
#         context.configure(connection=connection, target_metadata=target_metadata)
#
#         with context.begin_transaction():
#             context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
