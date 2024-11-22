from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from redis.asyncio import Redis
from pydantic import ValidationError

from app.bot.utils.redis import RedisStorage
from app.bot.utils.models import UserData, Stats


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
        try:
            user_redis = await redis.get_user(user.id)
        except ValidationError as exc:
            user_redis = None

        user_data = user_redis or UserData(
            id=user.id,
            full_name=user.full_name,
            score=0,
            balance=1000,
            blackjack_stats=Stats(
                total_games=0,
                wins=0,
                loses=0,
                draws=0,
            ),
            seabattle_stats=Stats(
                total_games=0,
                wins=0,
                loses=0,
                draws=0,
            ),
            fool_stats=Stats(
                total_games=0,
                wins=0,
                loses=0,
                draws=0,
            ),
        )
        if user_redis:
            user_data.full_name = user.full_name

        await redis.update_user(user.id, user_data)

        data["redis"] = redis
        data["user_data"] = user_data

        return await handler(event, data)
