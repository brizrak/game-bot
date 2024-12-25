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
    if "old_messages" in data and data["old_messages"]:
        for msg in data["old_messages"]:
            await delete_message(message.bot, message.chat.id, msg)
        await state.update_data(old_messages=[])


async def add_message(state: FSMContext, message: Message) -> None:
    data = await state.get_data()
    if "old_messages" in data and data["old_messages"]:
        messages = data["old_messages"]
    else:
        messages = []
    messages.append(message.message_id)
    await state.update_data(old_messages=messages)
