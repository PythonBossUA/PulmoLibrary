from os import environ
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from run_sqlite import DATABASE_URL as SQLITE_DATABASE_URL


class Base(DeclarativeBase):
    pass


PSQL_DATABASE_URL = environ["DATABASE_URL"]
psql_async_engine = create_async_engine(
    PSQL_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0, "ssl": "require"}
)
psql_async_session = async_sessionmaker(psql_async_engine, class_=AsyncSession, expire_on_commit=False)

sqlite_async_engine = create_async_engine(
    SQLITE_DATABASE_URL,
    echo=False,
)
sqlite_async_session = async_sessionmaker(sqlite_async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_psql_session() -> AsyncGenerator[AsyncSession, None]:
    async with psql_async_session() as session:
        yield session


async def get_sqlite_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlite_async_session() as session:
        yield session
