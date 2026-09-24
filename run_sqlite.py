import asyncio
import csv

# !!! No import from FastAPI project !!!
from sqlalchemy import String, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, mapped_column
from database import sqlite_async_engine, sqlite_async_session, Base


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(31), nullable=False, unique=True)


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_org: Mapped[str] = mapped_column("name:org", String(31), nullable=False)
    name_ua: Mapped[str | None] = mapped_column("name:ua", String(31), nullable=True)
    old_name_org: Mapped[str | None] = mapped_column(
        "old_name:org", String(31), nullable=True
    )
    old_name_ua: Mapped[str | None] = mapped_column(
        "old_name:ua", String(31), nullable=True
    )
    region_id: Mapped[int] = mapped_column(
        "region:id", ForeignKey("regions.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "region:id", "name:org", "name:ua", "old_name:org", "old_name:ua"
        ),
    )


async def main():
    async with sqlite_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sqlite_async_session() as session:
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
                        insert(Region)
                        .on_conflict_do_update(
                            index_elements=("name",),
                            set_={Region.name: Region.name},  # fake update
                        )
                        .returning(Region.name, Region.id),
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
    await sqlite_async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
