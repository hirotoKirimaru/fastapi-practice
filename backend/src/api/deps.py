from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.helper.config import settings

async_engine = create_async_engine(settings.DATABASE_URL, echo=True)
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

# Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession]:
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


async def get_writer_db() -> AsyncGenerator[AsyncSession]:
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


async def get_reader_db() -> AsyncGenerator[AsyncSession]:
    # async with async_session(autocommit=False, autoflush=False) as session:
    #     session.bind = async_engine
    # async with async_session(
    #     bind=async_engine, autocommit=False, autoflush=False
    # ) as session:
    async with async_session() as session:
        yield session


SessionWriterDep = Annotated[AsyncSession, Depends(get_writer_db)]
SessionReaderDep = Annotated[AsyncSession, Depends(get_reader_db)]
