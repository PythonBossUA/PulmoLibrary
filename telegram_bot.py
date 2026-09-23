import asyncio

from datetime import datetime, timedelta
from os import environ
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import update, select, case, exists

from models import User
from run_sqlite import Region, Settlement
from database import (
    psql_async_session,
    sqlite_sync_session,
    sqlite_async_session,
    verification_re_index,
    token_length,
)

request_counter: int = 0
user_attempts: dict[str, tuple[datetime, int]] = {}
retry_after = timedelta(hours=2)

with sqlite_sync_session() as session:
    cached_regions = {
        region.id: region.name for region in (session.scalars(select(Region))).all()
    }


def declension(one: str, few: str, many: str, number: int) -> str:
    n = number % 100
    n1 = n % 10
    if 11 <= n <= 19:
        return many
    if n1 == 1:
        return one
    if 2 <= n1 <= 4:
        return few
    return many


def rate_limiter(tg_id: str) -> str | None:
    global request_counter
    request_counter += 1

    now = datetime.now()
    if request_counter == 256:
        request_counter = 0
        expired_keys = [
            user_id
            for user_id, (check_time, _) in user_attempts.items()
            if check_time + retry_after < now
        ]
        for key in expired_keys:
            del user_attempts[key]

    if tuple_attempts := user_attempts.get(tg_id):
        check_time, attempts = tuple_attempts
        future_time = check_time + retry_after

        if attempts != 10:
            user_attempts[tg_id] = (check_time, attempts + 1)
        elif future_time < now:
            user_attempts[tg_id] = (now, 1)
        else:
            delta = (future_time - now).seconds
            hours, minutes, seconds = (
                delta // 3600,
                (delta % 3600) // 60,
                delta % 60,
            )
            return (
                "Занадто багато безглуздих запитів😴\n"
                "Можеш подати заявку перевірки *керівником сайту*\n"
                f"Або зачекай *"
                + (
                    f"{hours} {declension('годину', 'години', 'годин', number=hours)} "
                    if hours
                    else ""
                )
                + (
                    f"{minutes} {declension('хвилину', 'хвилини', 'хвилин', number=minutes)} "
                    if minutes
                    else ""
                )
                + (
                    f"{seconds} {declension('секунду', 'секунди', 'секунд', number=seconds)}"
                    if seconds
                    else ""
                )
                + "*"
            )
    else:
        user_attempts[tg_id] = (now, 1)


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    tg_id = str(message.from_user.id)

    if isinstance(msg := rate_limiter(tg_id), str):
        await message.answer(msg, parse_mode="Markdown")
        return

    async with psql_async_session() as psql:
        user = await psql.scalar(
            select(User).where(
                User.verification.op("~")(verification_re_index),
                User.verification == f"tg_id:{tg_id}",
            )
        )
        if not user:
            await message.answer("Скажи код перевірки🤗")
            return

        region = cached_regions[user.sqlite_region_id]
        async with sqlite_async_session() as sqlite:
            settlement = await sqlite.scalar(
                select(
                    case(
                        (Settlement.name_ua.isnot(None), Settlement.name_ua),
                        (Settlement.name_org.isnot(None), Settlement.name_org),
                        (
                            Settlement.old_name_ua.isnot(None),
                            Settlement.old_name_ua,
                        ),
                        (
                            Settlement.old_name_org.isnot(None),
                            Settlement.old_name_org,
                        ),
                    )
                ).where(Settlement.id == user.sqlite_settlement_id)
            )

            await message.answer(
                "За вами закріплено користувача:\n"
                f" *Ім'я:* {user.last_name} {user.first_name} {user.surname}\n"
                f" *Телефон:* +38{user.phone_number}\n"
                f" *Участь в заходах:* {'Так' if user.events_ok else 'Ні'}\n"
                f" *Локація:* {region} - {settlement}\n",
                parse_mode="Markdown",
            )


@router.message()
async def handle_code(message: Message):
    tg_id = str(message.from_user.id)

    if isinstance(msg := rate_limiter(tg_id), str):
        await message.answer(msg, parse_mode="Markdown")
        return

    async with psql_async_session() as psql:
        if await psql.scalar(
            select(
                exists().where(
                    User.verification.op("~")(verification_re_index),
                    User.verification == f"tg_id:{tg_id}",
                )
            )
        ):
            await message.answer(
                "Код не потрібно☺️ Вашого користувача уже підтверджено"
            )
            return

        if not message.text:
            await message.answer(
                "Код містить лише *a-z | 0-9* символи", parse_mode="Markdown"
            )
            return

        if len(message.text) != token_length or not message.text.isalnum():
            await message.answer(f"Код точно має бути {token_length} символів🤔")
            return

        async with sqlite_async_session() as sqlite:
            user = await psql.scalar(
                update(User)
                .values(verification=f"tg_id:{tg_id}")
                .where(
                    User.verification.op("~")(verification_re_index),
                    User.verification == f"token:{message.text}",
                )
                .returning(User)
            )

            if not user:
                await message.answer("Чекай... це точно правильний код?🥺")
                return

            region = cached_regions[user.sqlite_region_id]
            settlement = await sqlite.scalar(
                select(
                    case(
                        (Settlement.name_ua.isnot(None), Settlement.name_ua),
                        (Settlement.name_org.isnot(None), Settlement.name_org),
                        (
                            Settlement.old_name_ua.isnot(None),
                            Settlement.old_name_ua,
                        ),
                        (
                            Settlement.old_name_org.isnot(None),
                            Settlement.old_name_org,
                        ),
                    )
                ).where(Settlement.id == user.sqlite_settlement_id)
            )
            await psql.commit()

            await message.answer(
                "*Код отримано🥰*\n\n"
                "--- *Ваш користувач:* ---\n"
                f" · *Ім'я:* {user.last_name} {user.first_name} {user.surname}\n"
                f" · *Телефон:* +38{user.phone_number}\n"
                f" · *Участь в заходах:* {'Так' if user.events_ok else 'Ні'}\n"
                f" · *Локація:* {region} - {settlement}\n",
                parse_mode="Markdown",
            )


async def main():
    token = environ["BOT_TOKEN"]

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(
        bot,
        allowed_updates=["message"],
    )


if __name__ == "__main__":
    asyncio.run(main())
