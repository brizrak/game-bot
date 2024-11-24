from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.handlers.delete_message import delete_previous_message
from app.bot.handlers.blackjack import play_start

router = Router()
router.callback_query.filter(F.message.chat.type == "private", StateFilter(None))


@router.callback_query()
async def handler(call: CallbackQuery, state: FSMContext) -> None:
    if call.data == "21":
        await play_start(call.message, state)
    if call.data == "sea":
        await call.message.answer("Здесь будет морской бой")
    if call.data == "fool":
        await call.message.answer("Здесь наверное ниче не будет")
    await delete_previous_message(state, call.message)

    await call.answer()
