import json

from redis.asyncio import Redis

from app.bot.utils.models import UserData


class RedisStorage:
    NAME = "users"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def _get(self, name: str, key: str | int) -> bytes | None:
        async with self.redis.client() as client:
            return await client.hget(name, key)

    async def _set(self, name: str, key: str | int, value: any) -> None:
        async with self.redis.client() as client:
            await client.hset(name, key, value)

    async def get_user(self, id_: int) -> UserData | None:
        data = await self._get(self.NAME, id_)
        if data is not None:
            decoded_data = json.loads(data)
            return UserData(**decoded_data)
        return None

    async def update_user(self, id_: int, data: UserData) -> None:
        json_data = json.dumps(data.model_dump())
        await self._set(self.NAME, id_, json_data)

    async def get_all_users_ids(self) -> list[int]:
        async with self.redis.client() as client:
            user_ids = await client.hkeys(self.NAME)
            return [int(user_id) for user_id in user_ids]
