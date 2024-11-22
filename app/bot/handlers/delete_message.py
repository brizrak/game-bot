from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest


async def delete_message(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest:
        pass


async def delete_previous_message(state: FSMContext, message: Message) -> None:
    data = await state.get_data()
    if "old_message" in data and data["old_message"]:
        await delete_message(message.bot, message.chat.id, data["old_message"])
        await state.update_data(old_message={})
