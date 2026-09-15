import asyncio
import csv

# !!! No import from FastAPI project !!!
from sqlalchemy import String, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = "sqlite+aiosqlite:///settlements.db"


class Base(DeclarativeBase):
    pass


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(31), nullable=False, unique=True)


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_org: Mapped[str] = mapped_column(
        "name:org", String(31), nullable=False
    )
    name_ua: Mapped[str] = mapped_column(
        "name:ua", String(31), nullable=True
    )
    old_name_org: Mapped[str] = mapped_column(
        "old_name:org", String(31), nullable=True
    )
    old_name_ua: Mapped[str] = mapped_column(
        "old_name:ua", String(31), nullable=True
    )
    region_id: Mapped[int] = mapped_column(
        "region:id",
        ForeignKey("regions.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("name:org", "name:ua", "old_name:org", "old_name:ua", "region:id"),
    )


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

            regions = set()
            settlements = list()
            for row in reader:
                region = row[10].strip()

                regions.add(region)
                settlements.append(
                    {
                        "name_org": row[3],
                        "name_ua": row[4],
                        "old_name_org": row[8],
                        "old_name_ua": row[9],
                        "region_id": region,
                    }
                )

            region_name_and_id = dict(
                (
                    await session.execute(
                        insert(Region).returning(Region.name, Region.id),
                        ({"name": name} for name in regions),
                    )
                ).all()
            )

            for settlement in settlements:
                settlement["region_id"] = region_name_and_id[settlement["region_id"]]

            await session.execute(
                insert(Settlement).on_conflict_do_nothing(
                    index_elements=[
                        "name:org",
                        "name:ua",
                        "old_name:org",
                        "old_name:ua",
                        "region:id",
                    ]
                ),
                settlements,
            )
            await session.commit()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
