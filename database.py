from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

with open(".env", "r") as file:
    for line in file.readlines():
        if line.startswith("DATABASE_URL"):
            DATABASE_URL = line.split("=", 1)[-1].rstrip("\n")
            break
    else:
        raise ValueError("DATABASE_URL not found in .env")

async_engine = create_async_engine(DATABASE_URL, echo=True) # TODO set echo to False
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
