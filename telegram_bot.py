import asyncio

from datetime import datetime, timedelta
from os import environ
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import update, select, case

from models import User
from run_sqlite import Region, Settlement
from database import psql_async_session, sqlite_sync_session, sqlite_async_session

request_counter: int = 0
user_attempts: dict[str, tuple[datetime, int]] = {}
retry_after = timedelta(days=1)
with sqlite_sync_session() as session:
    cached_regions = {
        region.id: region.name for region in (session.scalars(select(Region))).all()
    }


def declension(one: str, few: str, many: str, number: int) -> str:
    n = abs(number) % 100
    return (
        many
        if 11 <= n <= 19
        else (many, one, few, few, few, many, many, many, many, many)[n % 10]
    )


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Скажи код перевірки🤗")


@router.message()
async def handle_code(message: Message):
    global request_counter
    request_counter += 1

    now = datetime.now()
    if request_counter == 100:
        request_counter = 0
        expired_keys = [
            user_id for user_id, (check_time, _) in user_attempts.items()
            if check_time + retry_after < now
        ]
        for key in expired_keys:
            del user_attempts[key]

    if not message.text or len(message.text) != 6 or not message.text.isalnum():
        if message.text:
            await message.answer("Код точно має бути 6 символів🤔*(та лише a-z | 0-9)*", parse_mode="Markdown")
        return

    telegram_user_id = str(message.from_user.id)
    tuple_attempts = user_attempts.get(telegram_user_id)

    if tuple_attempts:
        check_time, attempts = tuple_attempts
        future_time = check_time + retry_after

        if attempts != 10:
            user_attempts[telegram_user_id] = (now, attempts + 1)
        elif future_time < now:
            user_attempts[telegram_user_id] = (now, 1)
        else:
            delta = (future_time - now).seconds
            hours, minutes, seconds = (
                delta // 3600,
                (delta % 3600) // 60,
                delta % 60,
            )
            await message.answer(
                "Занадто багато неправильних кодів😴\n"
                "Можеш подати заявку перевірки *керівником сайту*\n"
                f"Або зачекай *"
                + (
                    f"{hours} {declension('годину', 'години', 'годин', number=hours)} "
                    if hours
                    else ""
                )
                + (
                    f"{minutes} {declension('хвилину','хвилини', 'хвилин', number=minutes)} "
                    if minutes
                    else ""
                )
                + (
                    f"{seconds} {declension('секунду', 'секунди', 'секунд', number=seconds)}"
                    if seconds
                    else ""
                )
                + "*",
                parse_mode="Markdown",
            )
            return
    else:
        user_attempts[telegram_user_id] = (now, 1)

    async with psql_async_session() as psql:
        async with sqlite_async_session() as sqlite:
            user = await psql.scalar(
                update(User)
                .values(telegram_id=telegram_user_id)
                .where(User.telegram_id == message.text.lower())
                .returning(User)
            )

            if user:
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
                return
            await message.answer("Чекай... це точно правильний код?🥺")


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
