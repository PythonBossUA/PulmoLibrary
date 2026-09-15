import asyncio
import csv
# !!! No import from FastAPI project !!!
from sqlalchemy import String
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


DATABASE_URL = "sqlite+aiosqlite:///settlements.db"


class Base(DeclarativeBase):
    pass


class Settlement(Base):
    __tablename__ = "settlements"

    name_org: Mapped[str] = mapped_column("name:org", String(63), nullable=False, primary_key=True)
    name_ua: Mapped[str] = mapped_column("name:ua", String(63), nullable=True, primary_key=True)
    old_name_org: Mapped[str] = mapped_column("old_name:org", String(63), nullable=True, primary_key=True)
    old_name_ua: Mapped[str] = mapped_column("old_name:ua", String(63), nullable=True, primary_key=True)


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        # prefix = "октя".capitalize()
        #
        # from sqlalchemy import select, case, or_
        #
        # print(
        #     (await session.scalars(
        #         select(
        #             case(
        #                 (Settlement.name_ua.startswith(prefix), Settlement.name_ua),
        #                 (Settlement.old_name_ua.startswith(prefix), Settlement.old_name_ua),
        #                 (Settlement.name_org.startswith(prefix), Settlement.name_org),
        #                 (Settlement.old_name_org.startswith(prefix), Settlement.old_name_org),
        #                 else_=None,
        #             ).distinct(),
        #         )
        #         .where(
        #             or_(
        #                 Settlement.name_org.startswith(prefix),
        #                 Settlement.name_ua.startswith(prefix),
        #                 Settlement.old_name_org.startswith(prefix),
        #                 Settlement.old_name_ua.startswith(prefix),
        #             )
        #         )
        #     )).all()
        # )

        with open("ua-name-places.csv", mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")

            _ = next(reader)

            await session.execute(
                insert(Settlement)
                .on_conflict_do_nothing(index_elements=["name:org", "name:ua", "old_name:org", "old_name:ua"]),
                [
                    {
                        "name_org": line[3],
                        "name_ua": line[4],
                        "old_name_org": line[8],
                        "old_name_ua": line[9],
                    }
                    for line in reader
                ]
            )
            await session.commit()
    await engine.dispose()


asyncio.run(main())
