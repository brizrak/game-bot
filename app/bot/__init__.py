from aiogram import Dispatcher

from app.bot import command


async def include_routers(dp: Dispatcher) -> None:
    dp.include_routers(
        command.router,
    )
