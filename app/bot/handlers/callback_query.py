from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.handlers.delete_message import delete_previous_message
from app.bot.handlers.windows import Window

router = Router()


@router.callback_query()
async def handler(call: CallbackQuery, state: FSMContext) -> None:
    action, game = call.data.split("_", 1)
    if action == "game":
        match game:
            case "21":
                await call.message.answer("Здесь будет двадцать одно")
            case "sea":
                await call.message.answer("Здесь будет морской бой")
            case "fool":
                await call.message.answer("Здесь наверное ниче не будет")
        await delete_previous_message(state, call.message)
    else:
        match game:
            case "21":
                await Window.blackjack_rules(call.message, state)
            case "sea":
                await Window.sea_rules(call.message, state)
            case "fool":
                await call.message.answer("Здесь наверное ниче не будет rules")

    await call.answer()
