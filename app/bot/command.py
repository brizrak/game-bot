from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def handler(message: Message) -> None:
    await message.answer(text="hello")
    await message.delete()
