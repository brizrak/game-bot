from aiogram import Dispatcher

from app.bot.middlewares.redis import RedisMiddleware


def register_middlewares(dp: Dispatcher, **kwargs) -> None:
    dp.update.outer_middleware.register(RedisMiddleware(kwargs["redis"]))


__all__ = [
    "register_middlewares",
]
