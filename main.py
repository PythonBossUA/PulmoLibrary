import jwt, orjson

from functools import wraps
from contextlib import AsyncExitStack
from os import environ, urandom
from datetime import datetime, timedelta, timezone, date
from typing import Annotated

from fastapi import FastAPI, Depends, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, or_, exists, update
from sqlalchemy.dialects.postgresql import insert as psql_insert

from argon2 import PasswordHasher, Type
from database import get_psql_session, get_sqlite_session, sqlite_sync_session
from models import User, VERIFIED_FLAG, UNVERIFIED_FLAG
from run_sqlite import Region, Settlement

_BAD_BODY = orjson.dumps({"type": "bad_request"})
_BAD_HEADERS = [
    (b"content-type", b"application/json"),
    (b"content-length", str(len(_BAD_BODY)).encode(encoding="ascii")),
]


def total_error_catcher(asgi_app: ASGIApp) -> ASGIApp:
    async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # lifespan/websocket
            await asgi_app(scope, receive, send)
            return

        started = False

        async def send_wrapper(message: dict) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        try:
            async with AsyncExitStack() as astack:
                scope["fastapi_middleware_astack"] = astack
                await asgi_app(scope, receive, send_wrapper)
        except Exception:
            if started:
                raise
            try:
                await send(
                    {
                        "type": "http.response.start",
                        "status": 400,
                        "headers": _BAD_HEADERS,
                    }
                )
                await send(
                    {
                        "type": "http.response.body",
                        "body": _BAD_BODY,
                        "more_body": False,
                    }
                )
            except Exception:
                pass

    return middleware


class BareFastAPI(FastAPI):
    def build_middleware_stack(self) -> ASGIApp:
        return total_error_catcher(self.router)


app = BareFastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    cached_regions_to_response = {region.name: region.id for region in regions}
    cached_regions = {region.id: region.name for region in regions}


async def json_body(request: Request) -> dict:
    return orjson.loads(await request.body())


Psql_Database = Annotated[AsyncSession, Depends(get_psql_session)]
Sqlite_Database = Annotated[AsyncSession, Depends(get_sqlite_session)]
OrJson_Body = Annotated[dict, Depends(json_body)]

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


def bad_request(message: str | None = None) -> dict:
    return {"type": "bad_request", **({"message": message} if message else {})}


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


async def get_settlement_by_id(settlement_id: int, sqlite_session: AsyncSession) -> str:
    return await sqlite_session.scalar(
        select(
            case(
                (Settlement.name_ua.isnot(None), Settlement.name_ua),
                (Settlement.name_org.isnot(None), Settlement.name_org),
                (Settlement.old_name_ua.isnot(None), Settlement.old_name_ua),
                (Settlement.old_name_org.isnot(None), Settlement.old_name_org),
            )
        ).where(Settlement.id == settlement_id)
    )


async def jwt_builder(user: User, sqlite: AsyncSession) -> str:
    settlement_name = await get_settlement_by_id(
        settlement_id=user.sqlite_settlement_id, sqlite_session=sqlite
    )
    region_name = cached_regions[user.sqlite_region_id]

    return jwt.encode(
        payload={
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "surname": user.surname,
            "phone": user.phone_number,
            "events_ok": user.events_ok,
            "region": region_name,
            "settlement": settlement_name,
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


@app.post("/registration")
@orjson_decorator
async def registration(json: OrJson_Body, psql: Psql_Database, sqlite: Sqlite_Database):
    """
    json:input {
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


@app.post("/auth")
@orjson_decorator
async def auth(json: OrJson_Body, psql: Psql_Database, sqlite: Sqlite_Database):
    """
    json:input {
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

        return {
            "type": "success_auth",
            "jwt": await jwt_builder(user, sqlite),
        }

    return bad_request(message="Неправильні дані")


@app.post("/do_not_verify_telegram")
@orjson_decorator
async def do_not_verify_telegram(json: OrJson_Body, psql: Psql_Database):
    """
    json:input {
        "type": "do_not_verify_telegram",
        "first_name": <str>,
        "last_name": <str>,
        "surname": <str>,
        "phone_number": <str>,
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
            ),
        )
    )
    if psql_response.rowcount == 0:
        return bad_request(message="Користувача не знайдено або його уже підтверджено")

    await psql.commit()
    return {"type": "do_not_verify_ok"}


@app.post("/user_is_verified")
@orjson_decorator
async def user_is_verified(
    json: OrJson_Body, psql: Psql_Database, sqlite: Sqlite_Database
):
    """
    json:input {
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

        return {
            "type": "user_is_verified",
            "jwt": jwt_builder(user, sqlite),
        }
    return {"type": "user_is_unverified"}


@app.post("/need_regions")
@orjson_decorator
async def need_regions():
    """
    json:input {
        "type": "need_regions"
    }
    """
    return {
        "type": "regions_answer",
        "regions": cached_regions_to_response,
    }


@app.post("/need_settlements")
@orjson_decorator
async def need_settlements(json: OrJson_Body, sqlite: Sqlite_Database):
    """
    json:input {
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
