from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault
)


async def setup(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Start bot"),
    ]

    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeDefault(),
    )


async def delete(bot: Bot) -> None:
    await bot.delete_my_commands(
        scope=BotCommandScopeDefault(),
    )
