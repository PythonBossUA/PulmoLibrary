from os import environ
from secrets import token_urlsafe
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

token_bytes = 4
_tl = token_bytes * (4 / 3)
token_length = int(_tl) + (_tl > int(_tl))  # used in models

translation_table = str.maketrans({"-": "A", "_": "B"})
verification_re_index = "^(tg_id|token)"


def generate_valid_token():
    return token_urlsafe(token_bytes).translate(translation_table)


class Base(DeclarativeBase):
    pass


SQLITE_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///sqlite.db"
SQLITE_SYNC_DATABASE_URL = SQLITE_ASYNC_DATABASE_URL.replace("+aiosqlite", "")

PSQL_DATABASE_URL = environ["DATABASE_URL"]
psql_async_engine = create_async_engine(
    PSQL_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0, "ssl": "require"},
)
psql_async_session = async_sessionmaker(
    psql_async_engine, class_=AsyncSession, expire_on_commit=False
)

sqlite_async_engine = create_async_engine(
    SQLITE_ASYNC_DATABASE_URL,
    echo=False,
)
sqlite_sync_engine = create_engine(SQLITE_SYNC_DATABASE_URL, echo=False)

sqlite_async_session = async_sessionmaker(
    sqlite_async_engine, class_=AsyncSession, expire_on_commit=False
)
sqlite_sync_session = sessionmaker(sqlite_sync_engine, class_=Session)


async def get_psql_session() -> AsyncGenerator[AsyncSession, None]:
    async with psql_async_session() as session:
        yield session


async def get_sqlite_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlite_async_session() as session:
        yield session
