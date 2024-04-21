from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from fastapi import Depends

# ASYNC_DB_URL = "mysql+aiomysql://root@db:3306/demo?charset=utf8"

# 非同期のテストのために、aiomysqlを使用する
# ASYNC_DB_URL = "mysql+aiomysql://root@localhost:33306/demo?charset=utf8"
# ASYNC_DB_URL = "mysql+pymysql://root@localhost:33306/demo?charset=utf8"
ASYNC_DB_URL = "mysql+aiomysql://root@db:3306/demo?charset=utf8"

async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
# async_session = sessionmaker(
#     autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
# )
# async_session = sessionmaker(bind=async_engine, class_=AsyncSession)
# async_session = sessionmaker(class_=AsyncSession)
# async_session = async_sessionmaker(
#     autoflush=False, expire_on_commit=False, bind=async_engine, class_=AsyncSession
# )
async_session = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


async def get_writer_db():
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


async def get_reader_db():
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


SessionWriterDep = Annotated[AsyncSession, Depends(get_writer_db)]
SessionReaderDep = Annotated[AsyncSession, Depends(get_reader_db)]
