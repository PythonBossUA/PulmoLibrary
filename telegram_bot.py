"""
In process to development :)
"""

import asyncio

from os import environ
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from models import User

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Надішли код перевірки.")


@router.message()
async def handle_code(message: Message):
    engine = create_async_engine(environ["DATABASE_URL"], echo=False)

    async with AsyncSession(engine) as session:
        user = await session.scalar(
            update(User)
            .values(telegram_id=message.from_user.id)
            .where(
                User.telegram_id == message.text
            )
            .returning(User)
        )

        if user:
            await message.answer(
                "Код отримано🥰\n"
                "Ваш користувач:\n"
                f"Ім'я: {' '.join((User.first_name, User.last_name, User.sur))}"
            )

    # Тут твоя логіка:
    # - отримати message.from_user.id
    # - отримати message.text
    # - записати в aiosqlite

    await message.answer("Код отримано.")


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