from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from redis.asyncio import Redis

from app.bot.utils.redis import RedisStorage
from app.bot.utils.models import UserData


class RedisMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        redis = RedisStorage(self.redis)

        user: User = data.get("event_from_user")
        user_redis = await redis.get_user(user.id)
        print(user_redis)

        user_data = user_redis or UserData(
            id=user.id,
            full_name=user.full_name,
            score=0,
            balance=1000,
        )
        if user_redis:
            user_data.full_name = user.full_name

        await redis.update_user(user.id, user_data)

        data["redis"] = redis
        data["user_data"] = user_data

        return await handler(event, data)
