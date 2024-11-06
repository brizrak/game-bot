import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.config import config
from app.bot import include_routers
from app.bot.middlewares import register_middlewares
from app.bot import commands


async def on_shutdown(dp: Dispatcher, bot: Bot) -> None:
    await commands.delete(bot)
    await bot.delete_webhook()
    await bot.session.close()


async def on_startup(bot: Bot) -> None:
    await commands.setup(bot)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.BOT_TOKEN)
    storage = RedisStorage.from_url(
        url=config.dsn(),
    )
    dp = Dispatcher(bot=bot, storage=storage)
    register_middlewares(dp=dp, redis=storage.redis)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await include_routers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
