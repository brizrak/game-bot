from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.bot.utils.redis import RedisStorage
from app.bot.utils.models import UserData
from app.bot.handlers.windows import Window

router = Router()


@router.message(CommandStart())
async def handler(message: Message, user_data: UserData, state: FSMContext) -> None:
    await Window.main_menu(message, user_data, state)


@router.message(Command("stats"))
async def handler(message: Message, user_data: UserData, state: FSMContext) -> None:
    await Window.stats(message, user_data, state)


@router.message(Command("rules"))
async def handler(message: Message, state: FSMContext) -> None:
    await Window.rules(message, state)


@router.message(Command("plus"))
async def handler(message: Message, user_data: UserData, redis: RedisStorage) -> None:
    user_data.blackjack_stats.total_games += 4
    user_data.blackjack_stats.wins += 3
    user_data.blackjack_stats.loses += 1
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
