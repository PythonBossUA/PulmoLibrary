import jwt, orjson

from functools import wraps
from os import environ, urandom
from datetime import datetime, timedelta, timezone

from typing import Annotated
from datetime import date

from fastapi import FastAPI, Depends, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, or_, exists, update
from sqlalchemy.dialects.postgresql import insert as psql_insert

from argon2 import PasswordHasher, Type
from database import get_psql_session, get_sqlite_session, sqlite_sync_session
from models import User, VERIFIED_FLAG, UNVERIFIED_FLAG
from run_sqlite import Region, Settlement

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

psql_database = Annotated[AsyncSession, Depends(get_psql_session)]
sqlite_database = Annotated[AsyncSession, Depends(get_sqlite_session)]
password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=16384,
    parallelism=1,
    hash_len=48,
    salt_len=16,
    type=Type.ID,
)
jwt_secret_key = environ["JWT_SECRET_KEY"]
jwt_algorithm = "HS256"
jwt_exp = timedelta(days=7)

with sqlite_sync_session() as session:
    regions = session.scalars(select(Region)).all()
    cached_regions_to_response = {
        region.name: region.id for region in regions
    }
    cached_regions = {
        region.id: region.name for region in regions
    }

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
    12: "Грудня",
}


@app.get("/")
async def index(request: Request):
    current_date = date.today()

    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "schedule": f"{current_date.day} {months_dict[current_date.month]} · " f"{
            "Сьогодні ми працюємо😄 · з 10:00 до 19:00"
            if current_date.weekday() not in (0, 5)  # 0 - понеділок; 5 - субота
            else "Сьогодні ми відпочиваємо🥺 · вихідні понеділок та субота"
            }"
        },
    )


def normalize_name(name: str) -> str | None:
    return name.strip().capitalize() if len(name) >= 2 and name.isalpha() else None


def format_phone_number(phone_number: str) -> str | None:
    clear_number = phone_number.removeprefix("+38")
    return (
        clear_number
        if len(clear_number) == 10
        and clear_number.isdigit()
        and clear_number.startswith("0")
        else None
    )


def bad_request(message: str | None = None) -> dict:
    return {"type": "bad_request", **({"message": message} if message else {})}


async def get_settlement_by_id(
    settlement_id: int, sqlite_session: AsyncSession
) -> str:
    return await sqlite_session.scalar(
        select(
            case(
                (Settlement.name_ua.isnot(None), Settlement.name_ua),
                (Settlement.name_org.isnot(None), Settlement.name_org),
                (Settlement.old_name_ua.isnot(None), Settlement.old_name_ua),
                (Settlement.old_name_org.isnot(None), Settlement.old_name_org)
            )
        ).where(Settlement.id == settlement_id)
    )


def jwt_builder(
    user_id: int,
    first_name: str,
    last_name: str,
    surname: str,
    phone: str,
    region: str,
    settlement: str,
    events_ok: str,
) -> str:
    return jwt.encode(
        payload={
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "surname": surname,
            "phone": phone,
            "region": region,
            "settlement": settlement,
            "events_ok": events_ok,
            "exp": datetime.now(timezone.utc) + jwt_exp,
        },
        key=jwt_secret_key,
        algorithm=jwt_algorithm,
    )


def orjson_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return Response(
            content=orjson.dumps(
                await func(*args, **kwargs),
            ),
            media_type="application/json",
        )

    return wrapper


@app.post("/events")
@orjson_decorator
async def events(request: Request, psql: psql_database, sqlite: sqlite_database):
    try:
        json = orjson.loads(await request.body())

        match json["type"]:
            case "registration":
                """
                require {
                    "type": "registration",
                    "first_name": <str>,
                    "last_name": <str>,
                    "surname": <str>,
                    "phone_number": <str>,
                    "password": <str>,
                    "events_ok": <bool>,
                    "region_id": <int>,
                    "settlement_id": <int>,
                }
                """
                first_name, last_name, surname = (
                    normalize_name(json["first_name"]),
                    normalize_name(json["last_name"]),
                    normalize_name(json["surname"]),
                )
                if not all((first_name, last_name, surname)):
                    return bad_request()

                phone_number = format_phone_number(json["phone_number"])
                if not phone_number:
                    return bad_request()

                hashed_password = password_hasher.hash(json["password"])

                telegram_code = urandom(4).hex()
                psql_response = await psql.execute(
                    psql_insert(User)
                    .values(
                        first_name=first_name,
                        last_name=last_name,
                        surname=surname,
                        telegram_id=telegram_code,
                        phone_number=phone_number,
                        hashed_password=hashed_password,
                        events_ok=json["events_ok"],
                        sqlite_region_id=(
                            json["region_id"]
                            if json["region_id"] in cached_regions
                            else None  # None raises IntegrityError
                        ),
                        sqlite_settlement_id=(
                            json["settlement_id"]
                            if await sqlite.scalar(
                                select(
                                    exists().where(
                                        Settlement.id == json["settlement_id"],
                                        Settlement.region_id == json["region_id"],
                                    )
                                )
                            )
                            else None  # None raises IntegrityError
                        ),
                    )
                    .on_conflict_do_nothing(constraint="unique_user")
                )
                if psql_response.rowcount == 0:
                    return bad_request(message="Такий користувач існує в базі")

                await psql.commit()

                return {
                    "type": "success_create",
                    "telegram_code": telegram_code,
                }

            case "auth":
                """
                require {
                    "type": "auth",
                    "first_name": <str>,
                    "last_name": <str>,
                    "surname": <str>,
                    "phone_number": <str>,
                    "region_id": <int>,
                    "settlement_id": <int>,
                    "password": <str>
                }
                """
                user: User = await psql.scalar(
                    select(User).where(
                        User.first_name == normalize_name(json["first_name"]),
                        User.last_name == normalize_name(json["last_name"]),
                        User.surname == normalize_name(json["surname"]),
                        User.phone_number == format_phone_number(json["phone_number"]),
                        User.sqlite_region_id == json["region_id"],
                        User.sqlite_settlement_id == json["settlement_id"],
                    )
                )

                if user and (
                    (user.telegram_id.isdigit() and len(user.telegram_id) != 8)
                    or user.telegram_id == VERIFIED_FLAG
                ):
                    password_hasher.verify(user.hashed_password, json["password"])

                    settlement_name = await get_settlement_by_id(
                            settlement_id=user.sqlite_settlement_id,
                            sqlite_session=sqlite
                    )
                    region_name = cached_regions[user.sqlite_region_id]

                    return {
                        "type": "success_auth",
                        "jwt": jwt_builder(
                            user_id=user.id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            surname=user.surname,
                            phone=user.phone_number,
                            region=region_name,
                            settlement=settlement_name,
                            events_ok=user.events_ok,
                        ),
                    }
                return bad_request(message="Неправильні дані")

            case "do_not_verify_telegram":
                """
                require {
                    "type": "do_not_verify_telegram",
                    "first_name": <str>,
                    "last_name": <str>,
                    "surname": <str>,
                    "region_id": <int>,
                    "settlement_id": <int>
                }
                """
                psql_response = await psql.execute(
                    update(User)
                    .values(telegram_id=UNVERIFIED_FLAG)
                    .where(
                        User.first_name == normalize_name(json["first_name"]),
                        User.last_name == normalize_name(json["last_name"]),
                        User.surname == normalize_name(json["surname"]),
                        User.phone_number == format_phone_number(json["phone_number"]),
                        User.sqlite_region_id == json["region_id"],
                        User.sqlite_settlement_id == json["settlement_id"],
                        or_(
                            User.telegram_id.op("!~")("^[[:digit:]]+$"),
                            User.telegram_id != VERIFIED_FLAG,
                        )
                    )
                )
                if psql_response.rowcount == 0:
                    return bad_request("Користувача не знайдено або його уже підтверджено")

                await psql.commit()
                return {"type": "not_verify_ok"}

            case "user_is_verified":
                """
                require {
                    "type": "user_is_verified",
                    "first_name": <str>,
                    "last_name": <str>,
                    "phone_number": <str>,
                    "surname": <str>,
                    "region_id": <int>,
                    "password": <str>,
                    "settlement_id": <int>,
                }
                """
                user = await psql.scalar(
                    select(User).where(
                        User.first_name == normalize_name(json["first_name"]),
                        User.last_name == normalize_name(json["last_name"]),
                        User.surname == normalize_name(json["surname"]),
                        User.phone_number == format_phone_number(json["phone_number"]),
                        User.sqlite_region_id == json["region_id"],
                        User.sqlite_settlement_id == json["settlement_id"],
                        or_(
                            User.telegram_id.op("~")("^[[:digit:]]+$"),
                            User.telegram_id == VERIFIED_FLAG,
                        ),
                    )
                )

                if user:
                    password_hasher.verify(user.hashed_password, json["password"])

                    settlement_name = await get_settlement_by_id(
                        settlement_id=user.sqlite_settlement_id,
                        sqlite_session=sqlite
                    )
                    region_name = cached_regions[user.sqlite_region_id]

                    return {
                        "type": "user_is_verified",
                        "jwt": jwt_builder(
                            user_id=user.id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            surname=user.surname,
                            phone=user.phone_number,
                            region=region_name,
                            settlement=settlement_name,
                            events_ok=user.events_ok,
                        ),
                    }
                return {"type": "user_is_unverified"}

            case "need_regions":
                """
                require {
                    "type": "need_regions"
                }
                """

                return {
                    "type": "regions_answer",
                    "regions": cached_regions_to_response,
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
                        {settlement: id_}
                        for settlement, id_ in (
                            await sqlite.execute(
                                select(
                                    case(
                                        (
                                            Settlement.name_ua.isnot(None),
                                            Settlement.name_ua,
                                        ),
                                        (
                                            Settlement.name_org.isnot(None),
                                            Settlement.name_org,
                                        ),
                                        (
                                            Settlement.old_name_ua.isnot(None),
                                            Settlement.old_name_ua,
                                        ),
                                        (
                                            Settlement.old_name_org.isnot(None),
                                            Settlement.old_name_org,
                                        ),
                                    ),
                                    Settlement.id,
                                ).where(
                                    Settlement.region_id == json["region_id"],
                                    or_(
                                        Settlement.name_org.startswith(prefix),
                                        Settlement.name_ua.startswith(prefix),
                                        Settlement.old_name_org.startswith(prefix),
                                        Settlement.old_name_ua.startswith(prefix),
                                    ),
                                )
                            )
                        ).all()
                    ],
                }
            case _:
                return bad_request()
    except Exception as e:
        return bad_request()
