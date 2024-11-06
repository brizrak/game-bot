import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.config import config
from app.bot import include_routers
from app.bot.middlewares import register_middlewares


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.BOT_TOKEN)
    storage = RedisStorage.from_url(
        url=config.dsn(),
    )
    dp = Dispatcher(bot=bot, storage=storage)
    register_middlewares(dp=dp, redis=storage.redis)

    await include_routers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
