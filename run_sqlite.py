import asyncio
import csv

from sqlalchemy import String
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Settlement(Base):
    __tablename__ = "settlements"

    name1: Mapped[str] = mapped_column(String(63), nullable=False, primary_key=True)
    name2: Mapped[str] = mapped_column(String(63), nullable=False, primary_key=True)
    old_name1: Mapped[str] = mapped_column(String(63), nullable=True, primary_key=True)
    old_name2: Mapped[str] = mapped_column(String(63), nullable=True, primary_key=True)


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///settlements.db", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        # prefix = "кіро".capitalize()
        #
        # from sqlalchemy import select, case, or_
        #
        # print(
        #     (await session.scalars(
        #         select(
        #             case(
        #                 (Settlement.name1.startswith(prefix), Settlement.name1),
        #                 (Settlement.name2.startswith(prefix), Settlement.name2),
        #                 (Settlement.old_name1.startswith(prefix), Settlement.old_name1),
        #                 (Settlement.old_name2.startswith(prefix), Settlement.old_name2),
        #                 else_=None,
        #             ).distinct(),
        #         )
        #         .where(
        #             or_(
        #                 Settlement.name1.startswith(prefix),
        #                 Settlement.name2.startswith(prefix),
        #                 Settlement.old_name1.startswith(prefix),
        #                 Settlement.old_name2.startswith(prefix),
        #             )
        #         )
        #     )).all()
        # )

        with open("ua-name-places.csv", mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")

            _ = next(reader)

            await session.execute(
                insert(Settlement)
                .on_conflict_do_nothing(index_elements=["name1", "name2", "old_name1", "old_name2"]),
                [
                    {
                        "name1": line[3],
                        "name2": line[4],
                        "old_name1": line[8],
                        "old_name2": line[9],
                    }
                    for line in reader
                ]
            )
            await session.commit()
    await engine.dispose()


asyncio.run(main())
