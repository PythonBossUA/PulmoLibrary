import orjson

from typing import Annotated
from datetime import date

from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from argon2 import PasswordHasher, Type
from database import get_psql_session, get_sqlite_session
from run_sqlite import Region, Settlement

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

psql_database = Annotated[AsyncSession, Depends(get_psql_session)]
sqlite_database = Annotated[AsyncSession, Depends(get_sqlite_session)]
password_hasher = PasswordHasher(
    time_cost=3, memory_cost=16384, parallelism=1,
    hash_len=48, salt_len=16, type=Type.ID,
)

months_dict = {
    1: "Січня",
    2: "Лютого",
    3: "Березня",
    4: "Квітня",
    5: "Травня",
    6: "Червня",
    7: "Липня",
    8: "Серпня",
    9: "Вересня",
    10: "Жовтня",
    11: "Листопада",
    12: "Грудня"
}


@app.get("/")
async def index(request: Request):
    current_date = date.today()

    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "schedule": f"{current_date.day} {months_dict[current_date.month]} · "
                        f"{
                        "Сьогодні ми працюємо😄 · з 10:00 до 19:00"
                        if current_date.weekday() not in (0, 5)  # 0 - понеділок; 5 - субота
                        else "Сьогодні ми відпочиваємо🥺 · вихідні понеділок та субота"
                        }"
        }
    )


def split_full_name(full_name: str) -> tuple[str, str]:
    first_name, last_name = full_name.strip().split()
    return first_name.capitalize(), last_name.capitalize()


def format_phone_number(phone_number: str) -> str:
    clear_number = phone_number.removeprefix("+38")
    if len(clear_number) == 10 and clear_number.isdigit() and clear_number.startswith("0"):
        return clear_number
    raise ValueError("Invalid phone number")


@app.post("/events")
async def events(request: Request, psql: psql_database, sqlite: sqlite_database):
    try:
        json = orjson.loads(await request.body())
        match json["type"]:
            case "registration":
                """
                require {
                    "type": "registration",
                    "full_name": <str>,
                    "phone_number": <str>,
                    "password": <str>,
                    "events_ok": <bool>,
                    "region_id": <int>,
                    "settlement_id": <int>,
                }
                """
                first_name, last_name = split_full_name(json["full_name"])
                phone_number = format_phone_number(json["phone_number"])
                hashed_password = password_hasher.hash(json["password"])

                await psql.execute(
                    insert(Settlement)
                    .values(
                        first_name=first_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        hashed_password=hashed_password,
                        events_ok=json["events_ok"],
                        sqlite_region_id=await sqlite.scalar(
                            select(Region.id)
                            .where(Region.id == json["region_id"])
                        ),
                        sqlite_settlement_id=await sqlite.scalar(
                            select(Settlement.id)
                            .where(Settlement.id == json["settlement_id"])
                        ),
                    )
                )

                return {
                    "type": "success_create"
                }

            case "login":
                ...
            case "need_regions":
                return {
                    "type": "regions_answer",
                    "regions": [
                        {
                            region.name : region.id
                        }
                        for region in (await sqlite.scalars(select(Region))).all()
                    ]
                }
            case "need_settlements":
                ...
    except Exception as e:
        return {
            "type": "bad_request"
        }
