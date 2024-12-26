from aiogram.fsm.state import StatesGroup, State


class BlackjackStates(StatesGroup):
    bet_chose = State()
    start_play = State()
    itog = State()
    one_more = State()
    end_game = State()


class GlobalStates(StatesGroup):
    menu = State()