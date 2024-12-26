from aiogram.fsm.state import StatesGroup, State

class FoolStates(StatesGroup):
    bet_chose = State()
    start_play = State()
    game_is_on = State()
    choosing_card = State()
    itog = State()
