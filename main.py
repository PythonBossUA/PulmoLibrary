import jwt, orjson

from os import environ
from datetime import datetime, timedelta, timezone

from typing import Annotated
from datetime import date

from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, or_
from sqlalchemy.dialects.postgresql import insert as psql_insert

from argon2 import PasswordHasher, Type
from database import get_psql_session, get_sqlite_session
from models import User
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
jwt_secret_key = environ["JWT_SECRET_KEY"]
jwt_algorithm = "HS256"
jwt_exp = timedelta(days=7)

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
    return (
        clear_number
        if len(clear_number) == 10
           and clear_number.isdigit()
           and clear_number.startswith("0")
        else None
    )


def bad_request() -> dict:
    return {"type": "bad_request"}


def jwt_builder(**kwargs) -> str:
    kwargs.update(exp=datetime.now(timezone.utc) + jwt_exp)

    return jwt.encode(
        payload=kwargs,
        key=jwt_secret_key,
        algorithm=jwt_algorithm
    )


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
                if not phone_number:
                    return bad_request()

                hashed_password = password_hasher.hash(json["password"])

                region_name, region_id = (await sqlite.execute(
                    select(Region.name, Region.id)
                    .where(Region.id == json["region_id"])
                )).first()

                settlement_name, settlement_id = (await sqlite.execute(
                    select(
                        case(
                            (Settlement.name_ua.isnot(None), Settlement.name_ua),
                            (Settlement.name_org.isnot(None), Settlement.name_org),
                            (Settlement.old_name_ua.isnot(None), Settlement.old_name_ua),
                            (Settlement.old_name_org.isnot(None), Settlement.old_name_org),
                            else_=None,
                        ),
                        Settlement.id
                    )
                    .where(Settlement.id == json["settlement_id"])
                )).first()

                user_id = await psql.scalar(
                    psql_insert(User)
                    .values(
                        first_name=first_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        hashed_password=hashed_password,
                        events_ok=json["events_ok"],
                        sqlite_region_id=region_id,
                        sqlite_settlement_id=settlement_id,
                    )
                    .on_conflict_do_nothing(
                        constraint="unique_user"
                    )
                    .returning(User.id)
                )
                if not user_id:
                    return bad_request()
                
                await psql.commit()

                return {
                    "type": "success_create",
                    "jwt": jwt_builder(
                        id=user_id,
                        first_name=first_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        region=region_name,
                        settlement=settlement_name,
                        events_ok=json["events_ok"]
                    )
                }

            case "auth":
                """
                require {
                    "type": "auth",
                    "full_name": <str>,
                    "region_id": <int>,
                    "settlement_id": <int>,
                    "password": <str>
                }
                """
                first_name, last_name = split_full_name(json["full_name"])
                user = await psql.scalar(
                    select(User)
                    .where(
                        User.first_name == first_name,
                        User.last_name == last_name,
                        User.sqlite_region_id == json["region_id"],
                        User.sqlite_settlement_id == json["settlement_id"],
                    )
                )

                if user:
                    password_hasher.verify(user.hashed_password, json["password"])

                    region_name = await sqlite.scalar(
                        select(Region.name)
                        .where(Region.id == user.sqlite_region_id)
                    )
                    settlement_name = await sqlite.scalar(
                        select(
                            case(
                                (Settlement.name_ua.isnot(None), Settlement.name_ua),
                                (Settlement.name_org.isnot(None), Settlement.name_org),
                                (Settlement.old_name_ua.isnot(None), Settlement.old_name_ua),
                                (Settlement.old_name_org.isnot(None), Settlement.old_name_org),
                                else_=None,
                            )
                        )
                        .where(Settlement.id == json["settlement_id"])
                    )

                    return {
                        "type": "success_auth",
                        "jwt": jwt_builder(
                            id=user.id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            phone_number=user.phone_number,
                            region=region_name,
                            settlement=settlement_name,
                            events_ok=user.events_ok
                        )
                    }
                return bad_request()

            case "need_regions":
                """
                require {
                    "type": "need_regions"
                }
                """

                return {
                    "type": "regions_answer",
                    "regions": [
                        {
                            region.name: region.id
                        }
                        for region in (await sqlite.scalars(select(Region))).all()
                    ]
                }

            case "need_settlements":
                """
                require {
                    "type": "need_settlements",
                    "settlement_startname": <str>,
                    "region_id": <int>
                }
                """

                prefix = json["settlement_startname"].capitalize()

                return {
                    "type": "settlements_answer",
                    "settlements": [
                        {
                            settlement: id_
                        }
                        for settlement, id_ in (await sqlite.execute(
                            select(
                                case(
                                    (Settlement.name_ua.startswith(prefix), Settlement.name_ua),
                                    (Settlement.name_org.startswith(prefix), Settlement.name_org),
                                    (Settlement.old_name_ua.startswith(prefix), Settlement.old_name_ua),
                                    (Settlement.old_name_org.startswith(prefix), Settlement.old_name_org),
                                    else_=None,
                                ).distinct(),
                                Settlement.id
                            )
                            .where(
                                Settlement.region_id == json["region_id"],
                                or_(
                                    Settlement.name_org.startswith(prefix),
                                    Settlement.name_ua.startswith(prefix),
                                    Settlement.old_name_org.startswith(prefix),
                                    Settlement.old_name_ua.startswith(prefix),
                                )
                            )
                        )).all()
                    ]
                }
            case _:
                return bad_request()
    except Exception as e:
        return bad_request()
