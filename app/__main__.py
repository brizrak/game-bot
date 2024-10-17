import logging
import asyncio

from aiogram import Bot, Dispatcher

from app.config import load_config
from app.bot import include_routers


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(load_config().BOT_TOKEN)
    dp = Dispatcher(bot=bot)
    await include_routers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
