from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from app.bot.utils.models import UserData
from app.bot.handlers.delete_message import delete_previous_message, add_message
from app.bot.handlers.states import GlobalStates


def game_choice(text: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder().row(
        *[
            InlineKeyboardButton(text="Двадцать одно", callback_data=f"{text}_21"),
            InlineKeyboardButton(text="Морской бой", callback_data=f"{text}_sea"),
            InlineKeyboardButton(text="Дурак", callback_data=f"{text}_fool"),
        ], width=1
    )
    return builder.as_markup()


class Window:
    @staticmethod
    async def main_menu(message: Message, user_data: UserData, state: FSMContext, is_command: bool = False) -> None:
        text = f"Привет🖐\n\nВаш баланс: {user_data.balance}\nВаш счет: {user_data.score}\n\nВыберите игру:"
        reply_markup = game_choice("game")
        msg = await message.answer(text=text, reply_markup=reply_markup)
        await delete_previous_message(state, message)
        await add_message(state, msg)
        if is_command:
            await message.delete()

    @staticmethod
    async def stats(message: Message, user_data: UserData, state: FSMContext) -> None:
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
        await delete_previous_message(state, message)
        await add_message(state, msg)
        await message.delete()

    @staticmethod
    async def rules(message: Message, state: FSMContext) -> None:
        text = f"Выберите игру:"
        reply_markup = game_choice("rule")
        msg = await message.answer(text=text, reply_markup=reply_markup)
        await delete_previous_message(state, message)
        await state.update_data(old_message=msg.message_id)
        await message.delete()

    @staticmethod
    async def sea_rules(message: Message, state: FSMContext) -> None:
        await delete_previous_message(state, message)
        text = ("Добро пожаловать в Морской Бой!"
                "\n\nПравила игры:"
                "\n1.  Игровое поле представляет собой сетку 10x10, где строки обозначены цифрами (1-10), а столбцы - буквами (A-J)."
                "\n2.  На каждом поле размещены корабли разных размеров: 1 корабль длиной 4 клетки, 2 корабля длиной 3 клетки, 3 корабля длиной 2 клетки и 4 корабля длиной 1 клетка."
                "\n3.  Цель игры - первым потопить все корабли противника."
                "\n4.  Игрок выбирает координаты для выстрела (например, A1, B5, J10)."
                "\n5.  Если выстрел попадает в корабль, то корабль помечается как раненый, и вы получаете возможность продолжать стрелять до первого промаха."
                "\n6.  Если вы потопили корабль противника, то все окружающие клетки вокруг потопленного корабля автоматически отмечаются как промах."
                "\n7.  Выигрывает тот, кто первым потопит все корабли противника."
                "\n\nЛегенда:"
                "\n⬜️ — Пустая клетка"
                "\n🟩 — Клетка с кораблем"
                "\n❌ — Клетка, в которую попали"
                "\n🌀 — Клетка, в которую промахнулись")

        msg = await message.answer(text=text)
        await state.update_data(old_message=msg.message_id)

    @staticmethod
    async def blackjack_rules(message: Message, state: FSMContext) -> None:
        await delete_previous_message(state, message)
        text = ("Добро пожаловать в Двадцать Одно!"
                "\n\nПравила игры:"
                "\n\nЕсли первые две карты в сумме дают 21 очко, то такая комбинация называется блэкджек. Если дилер собрал блэкджек, то все игроки проигрывают, кроме тех, у кого тоже блэкджек. Такой случай считается ничьей, и ставка возвращается игроку."
                "\n\nЕсли игрок собрал блэкджек, а дилер нет, то игрок выигрывает и получает выплату 3 к 2 от своей ставки."
                "\n\nЦель игрока - собрать руку, сумма очков в которой превышает сумму очков у дилера. Важно собрать не более 21 очков, в ином случае игрок проиграет (перебор).")

        msg = await message.answer(text=text)
        await state.update_data(old_message=msg.message_id)
