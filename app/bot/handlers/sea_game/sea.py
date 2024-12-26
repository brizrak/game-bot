import random
from typing import List, Tuple
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command


from app.bot.handlers.states import GameStates

# Состояния FSM (конечный автомат состояний)
router = Router()


# Константы для игры
EMPTY_CELL = '⬜️'  # Пустая клетка
SHIP_CELL = '🟩'  # Клетка с кораблем
HIT_CELL = '❌'  # Клетка, в которую попали
MISS_CELL = '🌀'  # Клетка, в которую промахнулись


# Класс для представления корабля
class Ship:
    def __init__(self, size: int, coordinates: List[Tuple[int, int]]):
        self.size = size  # Размер корабля
        self.coordinates = coordinates  # Координаты корабля
        self.hit_count = 0  # Количество попаданий по кораблю

    def is_sunk(self) -> bool:
        return self.hit_count >= self.size  # Проверка, потоплен ли корабль

    def get_status(self):
        if self.is_sunk():
            return "Уничтожен"  # Если потоплен
        elif self.hit_count > 0:
            return "Ранен"  # Если ранен
        else:
            return "Цел"  # Если цел


# Класс для управления игрой
class SeaBattle:
    def __init__(self):
        self.player_board = self.create_board()  # Игровая доска игрока
        self.enemy_board = self.create_board()  # Игровая доска противника
        self.ships = {'4': 1, '3': 2, '2': 3, '1': 4}  # Словарь с количеством кораблeй разных размеров
        self.player_ships = []  # Список кораблeй игрока
        self.enemy_ships = []  # Список кораблeй противника
        self.place_ships(self.player_board, self.player_ships)  # Размещаем корабли игрока
        self.place_ships(self.enemy_board, self.enemy_ships)  # Размещаем корабли противника
        self.enemy_shots = []  # Список для отслеживания выстрелов врага

    # Создание пустой игровой доски
    @staticmethod
    def create_board():
        return [[EMPTY_CELL for _ in range(10)] for _ in range(10)]  # Создание доски 10x10

    # Проверка возможности размещения корабля
    def can_place_ship(self, board, x, y, ship_size, orientation):
        if orientation == 'H':  # Горизонтальное размещение
            if y + ship_size > len(board[0]):  # Проверка выхода за границы доски
                return False
            for i in range(ship_size):
                # Проверка, что в клетке нет корабля и рядом нет других кораблeй
                if board[x][y + i] != EMPTY_CELL and board[x][y + i] != MISS_CELL or \
                        (x > 0 and board[x - 1][y + i] != EMPTY_CELL and board[x - 1][y + i] != MISS_CELL) or \
                        (x < len(board) - 1 and board[x + 1][y + i] != EMPTY_CELL and board[x + 1][
                            y + i] != MISS_CELL) or \
                        (y + i > 0 and board[x][y + i - 1] != EMPTY_CELL and board[x][y + i - 1] != MISS_CELL) or \
                        (y + i < len(board[0]) - 1 and board[x][y + i + 1] != EMPTY_CELL and board[x][
                            y + i + 1] != MISS_CELL) or \
                        (x > 0 and y + i > 0 and board[x - 1][y + i - 1] != EMPTY_CELL and board[x - 1][
                            y + i - 1] != MISS_CELL) or \
                        (x > 0 and y + i < len(board[0]) - 1 and board[x - 1][y + i + 1] != EMPTY_CELL and board[x - 1][
                            y + i + 1] != MISS_CELL) or \
                        (x < len(board) - 1 and y + i > 0 and board[x + 1][y + i - 1] != EMPTY_CELL and board[x + 1][
                            y + i - 1] != MISS_CELL) or \
                        (x < len(board) - 1 and y + i < len(board[0]) - 1 and board[x + 1][y + i + 1] != EMPTY_CELL and
                         board[x + 1][y + i + 1] != MISS_CELL):
                    return False

        else:  # Вертикальное размещение
            if x + ship_size > len(board):
                return False
            for i in range(ship_size):
                # Проверка, что в клетке нет корабля и рядом нет других кораблeй
                if board[x + i][y] != EMPTY_CELL and board[x + i][y] != MISS_CELL or \
                        (y > 0 and board[x + i][y - 1] != EMPTY_CELL and board[x + i][y - 1] != MISS_CELL) or \
                        (y < len(board[0]) - 1 and board[x + i][y + 1] != EMPTY_CELL and board[x + i][
                            y + 1] != MISS_CELL) or \
                        (x + i > 0 and board[x + i - 1][y] != EMPTY_CELL and board[x + i - 1][y] != MISS_CELL) or \
                        (x + i < len(board) - 1 and board[x + i + 1][y] != EMPTY_CELL and board[x + i + 1][
                            y] != MISS_CELL) or \
                        (x + i > 0 and y > 0 and board[x + i - 1][y - 1] != EMPTY_CELL and board[x + i - 1][
                            y - 1] != MISS_CELL) or \
                        (x + i > 0 and y < len(board[0]) - 1 and board[x + i - 1][y + 1] != EMPTY_CELL and
                         board[x + i - 1][y + 1] != MISS_CELL) or \
                        (x + i < len(board) - 1 and y > 0 and board[x + i + 1][y - 1] != EMPTY_CELL and
                         board[x + i + 1][y - 1] != MISS_CELL) or \
                        (x + i < len(board) - 1 and y < len(board[0]) - 1 and board[x + i + 1][y + 1] != EMPTY_CELL and
                         board[x + i + 1][y + 1] != MISS_CELL):
                    return False
        return True

    def place_ships(self, board, ship_list):
        for ship_size, count in self.ships.items():
            for _ in range(count):
                placed = False
                while not placed:
                    orientation = random.choice(['H', 'V'])  # Выбор случайной ориентации
                    if orientation == 'H':  # Горизонтальная ориентация
                        x = random.randint(0, 9)
                        y = random.randint(0, 10 - int(ship_size))
                    else:  # Вертикальная ориентация
                        x = random.randint(0, 10 - int(ship_size))
                        y = random.randint(0, 9)
                    if self.can_place_ship(board, x, y, int(ship_size), orientation):
                        # Размещение корабля на доске
                        coordinates = []
                        for i in range(int(ship_size)):
                            if orientation == 'H':
                                board[x][y + i] = SHIP_CELL
                                coordinates.append((x, y + i))
                            else:
                                board[x + i][y] = SHIP_CELL
                                coordinates.append((x + i, y))
                        ship_list.append(Ship(int(ship_size), coordinates))
                        placed = True

    @staticmethod
    def board_to_str(board, hide_ships=False):
        header = "     "
        for i in range(10):
            if i % 3 == 0:
                header += f"{chr(65 + i)} "  # Один пробел
            else:
                header += f"{chr(65 + i)}  "  # Два пробела
        header += "\n"
        rows = []
        for i, row in enumerate(board):
            cells = [cell if not hide_ships or cell != SHIP_CELL else EMPTY_CELL for cell in row]
            rows.append(f"{i + 1:2}  " + "".join(cells))
        return header + "\n".join(rows)

    async def display_boards(self, message: Message):
        player_str = "Ваше игровое поле:\n" + self.board_to_str(self.player_board)
        enemy_str = "Игровое поле противника:\n" + self.board_to_str(self.enemy_board, hide_ships=True)
        await message.answer(f"<pre>{player_str}</pre>\n<pre>{enemy_str}</pre>", parse_mode="HTML")

    def mark_surrounding_cells(self, board, ship):
        surrounding_cells = set()  # Множество окружающих клеток
        for x, y in ship.coordinates:
            # Проходим по всем окружающим клеткам
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 10 and 0 <= ny < 10:
                    surrounding_cells.add((nx, ny))  # Добавляем окружающие клетки
        for x, y in surrounding_cells:
            if board[x][y] == EMPTY_CELL:
                board[x][y] = MISS_CELL  # Помечаем пустые клетки вокруг потопленного корабля

    def shoot(self, target_board, ships, move, user_id):
        try:
            x = int(move[1:]) - 1  # Получение координаты x
            y = ord(move[0]) - ord('A')  # Получение координаты y

            if target_board[x][y] == SHIP_CELL:  # Если попали в корабль
                target_board[x][y] = HIT_CELL  # Помечаем клетку как попадание
                hit_ship = None
                for ship in ships:  # Поиск корабля, в который попали
                    if (x, y) in ship.coordinates:
                        ship.hit_count += 1  # Увеличиваем количество попаданий по кораблю
                        hit_ship = ship
                        if ship.is_sunk():
                            self.mark_surrounding_cells(target_board,
                                                        ship)  # Помечаем окружающие клетки, если корабль потоплен
                            return True, f"Вы потопили корабль на координатах {move}!"  # Возвращаем True, если корабль потоплен
                        else:
                            return True, f"Вы ранили корабль на координатах {move}!"  # Возвращаем True, если попали в раненый корабль

            elif target_board[x][y] == EMPTY_CELL:  # Если промахнулись
                target_board[x][y] = MISS_CELL  # Помечаем клетку как промах
                return False, f"Вы промахнулись на координатах {move}!"  # Возвращаем False, если промахнулись
            else:
                return "Вы уже стреляли в эту клетку.", "Вы уже стреляли в эту клетку."  # Возвращаем сообщение, если стреляли в клетку ранее
        except (ValueError, IndexError):
            return "Некорректный формат ввода. Попробуйте ещё раз (например, A1 или J10).", "Некорректный формат ввода. Попробуйте ещё раз (например, A1 или J10)."  # Возвращаем сообщение, если ввод не корректный

    def check_winner(self, ships):
        return all(ship.is_sunk() for ship in ships)  # Проверка, все ли корабли потоплены

    def add_surrounding_shots(self, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Направления для окружающих клеток
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[nx][ny] not in [HIT_CELL, MISS_CELL]:
                self.enemy_shots.append((nx, ny))  # Добавляем окружающие клетки для выстрела

    def check_for_adjacent_L(self, x, y):
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]  # Направления для окружающих клеток
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10 and self.player_board[nx][ny] == EMPTY_CELL:
                return nx, ny  # Возвращает пустую клетку рядом, если есть
        return None

    def enemy_shoot(self, target_board, ships):
        while True:
            if self.enemy_shots:
                x, y = self.enemy_shots.pop(0)  # Берём выстрел из списка
            else:
                x, y = random.randint(0, 9), random.randint(0, 9)  # Выбираем случайный выстрел
            if target_board[x][y] == EMPTY_CELL:
                target_board[x][y] = MISS_CELL  # Помечаем промах
                return False, f"Противник промахнулся на координатах {chr(y + ord('A'))}{x + 1}."  # Возвращаем False, и сообщение о промахе
            elif target_board[x][y] == SHIP_CELL:
                target_board[x][y] = HIT_CELL  # Помечаем попадание
                for ship in ships:
                    if (x, y) in ship.coordinates:
                        ship.hit_count += 1
                        if ship.is_sunk():
                            self.mark_surrounding_cells(target_board,
                                                        ship)  # Помечаем клетки вокруг уничтоженного корабля
                            return True, f"Противник потопил ваш корабль на координатах {chr(y + ord('A'))}{x + 1}!"  # Возвращаем True и сообщение о попадании и статусе корабля
                        else:
                            self.add_surrounding_shots(x, y)  # Добавляем соседние клетки, если корабль ранен
                            return True, f"Противник ранил ваш корабль на координатах {chr(y + ord('A'))}{x + 1}!"  # Возвращаем True и сообщение о попадании и статусе корабля


# Обработчики команд и ходов
games = {}  # Словарь для хранения игр каждого пользователя


@router.callback_query(F.data == 'game_sea')
async def cmd_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id  # Получение ID пользователя
    game = SeaBattle()  # Создание новой игры
    games[user_id] = game  # Сохранение игры
    await state.set_state(GameStates.waiting_for_player_move_letter)  # Установка состояния ожидания выбора буквы
    await game.display_boards(callback.message)  # Вывод игровых досок
    await callback.message.answer("Выберите букву для выстрела:", reply_markup=create_letter_keyboard())  # Инструкция для игрока


def create_letter_keyboard():
    letters = "ABCDEFGHIJ"
    keyboard = [
        [InlineKeyboardButton(text=letters[i], callback_data=f"letter_{letters[i]}") for i in range(5)],
        # Первая строка
        [InlineKeyboardButton(text=letters[i], callback_data=f"letter_{letters[i]}") for i in range(5, 10)]
        # Вторая строка
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_number_keyboard():
    numbers = [str(i) for i in range(1, 11)]
    keyboard = [
        [InlineKeyboardButton(text=numbers[i], callback_data=f"number_{numbers[i]}") for i in range(5)],
        # Первая строка
        [InlineKeyboardButton(text=numbers[i], callback_data=f"number_{numbers[i]}") for i in range(5, 10)]
        # Вторая строка
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(GameStates.waiting_for_player_move_letter)
async def handle_letter_choice(query: CallbackQuery, state: FSMContext):
    letter = query.data.split("_")[1]
    await state.update_data(selected_letter=letter)
    await state.set_state(GameStates.waiting_for_player_move_number)
    await query.message.answer(f"Выберите цифру для выстрела:", reply_markup=create_number_keyboard())
    await query.answer()


@router.callback_query(GameStates.waiting_for_player_move_number)
async def handle_number_choice(query: CallbackQuery, state: FSMContext):
    number = query.data.split("_")[1]
    await state.update_data(selected_number=number)
    user_data = await state.get_data()
    selected_letter = user_data.get("selected_letter")
    await state.set_state(GameStates.waiting_for_player_move_confirm)
    await query.message.answer(f"Выбрана буква {selected_letter} и цифра {number}. Подтвердить выстрел?",
                               reply_markup=create_confirmation_keyboard(selected_letter, number))
    await query.answer()


def create_confirmation_keyboard(letter, number):
    keyboard = [
        [
            InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_{letter}{number}"),
            InlineKeyboardButton(text="Отменить", callback_data="cancel_move")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(GameStates.waiting_for_player_move_confirm)
async def handle_confirmation(query: CallbackQuery, state: FSMContext):
    if query.data.startswith("confirm_"):
        move = query.data.split("_")[1]
        user_id = query.from_user.id
        game = games.get(user_id)
        if not game:
            await query.message.answer("Игра не найдена.")
            return

        hit_result = True  # Инициализация для цикла
        while hit_result:  # Пока попадания продолжаются
            shoot_result, shoot_message = game.shoot(game.enemy_board, game.enemy_ships, move, user_id)
            if shoot_result == "Вы уже стреляли в эту клетку.":
                await query.message.answer(shoot_message)
                await query.message.answer("Выберите букву для выстрела:", reply_markup=create_letter_keyboard())
                await state.set_state(GameStates.waiting_for_player_move_letter)
                return  # Важно! Возвращаем, чтобы выйти из цикла

            elif shoot_result:
                await query.message.answer(shoot_message)
                await game.display_boards(query.message)
                # Если попадание, предлагаем выбор координат
                await query.message.answer("Выберите букву для выстрела:", reply_markup=create_letter_keyboard())
                await state.set_state(GameStates.waiting_for_player_move_letter)
                break;  # Выходим из цикла, чтобы игрок выбрал координаты
            else:
                await query.message.answer(shoot_message)  # Обрабатываем промах
                await game.display_boards(query.message)
                hit_result = False  # Обновляем hit_result

        if game.check_winner(game.enemy_ships):
            await query.message.answer("Вы победили!")
            await state.clear()
            return

        if not hit_result:  # Только если игрок промахнулся, переходим к ходу противника
            await state.set_state(GameStates.waiting_for_enemy_move)
            await enemy_turn(query.message, game, state)

    elif query.data == "cancel_move":
        await state.set_state(GameStates.waiting_for_player_move_letter)
        await query.message.answer("Выберите букву для выстрела:", reply_markup=create_letter_keyboard())
    await query.answer()


async def enemy_turn(message: Message, game: SeaBattle, state: FSMContext):
    hit_result = True  # инициализируем hit_result в True для цикла while
    while hit_result:  # цикл будет работать пока есть попадания
        hit_result, enemy_result = game.enemy_shoot(game.player_board, game.player_ships)
        if enemy_result:
            await message.answer(enemy_result)
            await game.display_boards(message)

        if game.check_winner(game.player_ships):
            await message.answer("Вы проиграли!")
            await state.clear()
            return

        if not hit_result:
            break  # Выходим из цикла после промаха

    if not game.check_winner(game.player_ships):
        await state.set_state(GameStates.waiting_for_player_move_letter)
        await message.answer("Выберите букву для выстрела:", reply_markup=create_letter_keyboard())
