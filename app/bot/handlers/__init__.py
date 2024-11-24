from aiogram import Dispatcher

from app.bot.handlers import command, callback_query, blackjack


async def include_routers(dp: Dispatcher) -> None:
    dp.include_routers(
        command.router,
        callback_query.router,
        blackjack.router,
    )
