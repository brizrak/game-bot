from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.bot.utils.models import UserData
from app.bot.utils.redis import RedisStorage

router = Router()


@router.message(CommandStart())
async def handler(message: Message, user_data: UserData) -> None:
    await message.answer(text=f"hello\nyour balance: {user_data.balance}\nyour score: {user_data.score}")
    await message.delete()


@router.message(Command("plus"))
async def handler(message: Message, user_data: UserData, redis: RedisStorage) -> None:
    user_data.balance += 100
    await redis.update_user(user_data.id, user_data)
    await message.answer(text=f"balance increased")
    await message.delete()


@router.message(Command("minus"))
async def handler(message: Message, user_data: UserData, redis: RedisStorage) -> None:
    user_data.balance -= 100
    await redis.update_user(user_data.id, user_data)
    await message.answer(text=f"balance decreased")
    await message.delete()
