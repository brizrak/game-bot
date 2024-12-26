from aiogram.fsm.state import StatesGroup, State


class BlackjackStates(StatesGroup):
    bet_chose = State()
    start_play = State()
    itog = State()
    one_more = State()
    end_game = State()


class GlobalStates(StatesGroup):
    menu = State()


class FoolStates(StatesGroup):
    bet_chose = State()
    start_play = State()
    game_is_on = State()
    choosing_card = State()
    itog = State()


class GameStates(StatesGroup):
    waiting_for_player_move_letter = State()  # Ожидание выбора буквы игроком
    waiting_for_player_move_number = State()  # Ожидание выбора цифры игроком
    waiting_for_player_move_confirm = State()  # Ожидание подтверждения хода игрока
    waiting_for_enemy_move = State()  # Ожидание хода противника
