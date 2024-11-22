from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from app.bot.utils.models import UserData
from app.bot.handlers.delete_message import delete_previous_message


def game_choice() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder().row(
        *[
            InlineKeyboardButton(text="Двадцать одно", callback_data="21"),
            InlineKeyboardButton(text="Морской бой", callback_data="sea"),
            InlineKeyboardButton(text="Дурак", callback_data="fool"),
        ], width=1
    )
    return builder.as_markup()


class Window:
    @staticmethod
    async def main_menu(message: Message, user_data: UserData, state: FSMContext) -> None:
        await delete_previous_message(state, message)
        text = f"Привет🖐\n\nВаш баланс: {user_data.balance}\nВаш счет: {user_data.score}\n\nВыберите игру:"
        reply_markup = game_choice()
        msg = await message.answer(text=text, reply_markup=reply_markup)
        await state.update_data(old_message=msg.message_id)
        await message.delete()

    @staticmethod
    async def stats(message: Message, user_data: UserData, state: FSMContext) -> None:
        await delete_previous_message(state, message)
        text = (f"Статистика:"
                f"\n\nДвадцать одно:"
                f"\n\tВсего игр: {user_data.blackjack_stats.total_games}"
                f"\n\tПобед: {user_data.blackjack_stats.wins}"
                f"\n\tПоражений: {user_data.blackjack_stats.loses}"
                f"\n\tНичьих: {user_data.blackjack_stats.draws}"
                f"\n\nМорской бой:"
                f"\n\tВсего игр: {user_data.seabattle_stats.total_games}"
                f"\n\tПобед: {user_data.seabattle_stats.wins}"
                f"\n\tПоражений: {user_data.seabattle_stats.loses}"
                f"\n\tНичьих: {user_data.seabattle_stats.draws}"
                f"\n\nДурак:"
                f"\n\tВсего игр: {user_data.fool_stats.total_games}"
                f"\n\tПобед: {user_data.fool_stats.wins}"
                f"\n\tПоражений: {user_data.fool_stats.loses}"
                f"\n\tНичьих: {user_data.fool_stats.draws}")
        msg = await message.answer(text=text)
        await state.update_data(old_message=msg.message_id)
        await message.delete()
