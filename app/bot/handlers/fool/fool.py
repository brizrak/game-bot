import os.path
import time
import asyncio
import random

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from PIL import Image

from app.config import config
from app.bot.handlers.fool.datas import lobby_list, money, create_deck
from app.bot.handlers.fool.keyboard import startupplayonly, playonly, playpass, playtake, playbeaten, final_kb, weirdfinal_kb
from app.bot.handlers.states import FoolStates

from app.bot.utils.redis import RedisStorage
from app.bot.utils.models import UserData
from app.bot.handlers.windows import Window

router = Router()


def type_to_ru_adj_string(given_type):
    # ["cherv", "boob", "chip", "cross"]
    if given_type == "boob":
        return "Бубен"
    if given_type == "cherv":
        return "Червей"
    if given_type == "chip":
        return "Пик"
    if given_type == "cross":
        return "Крестей"


def type_to_ru_string(given_type):
    # ["cherv", "boob", "chip", "cross"]
    if given_type == "boob":
        return "Бубны"
    if given_type == "cherv":
        return "Черви"
    if given_type == "chip":
        return "Пики"
    if given_type == "cross":
        return "Крести"


def sort_deck(given_deck):
    while True:
        is_sorted = True
        for i in range(len(given_deck) - 1):
            if card_value_as_int(given_deck[i]) > card_value_as_int(given_deck[i + 1]):
                given_deck[i], given_deck[i + 1] = given_deck[i + 1], given_deck[i]
                is_sorted = False
        if is_sorted:
            break;
    return given_deck


def target_is_valid_deck(given_deck, trump_type):
    has_trump_card_flag = 0
    for element in given_deck:
        if element[0] == trump_type:
            has_trump_card_flag = 1
        if not (element[1] == given_deck[0][1]) and has_trump_card_flag:
            return True
    return False


def card_value_as_int(given_card):
    if given_card[1] == "6":
        return 1
    if given_card[1] == "7":
        return 2
    if given_card[1] == "8":
        return 3
    if given_card[1] == "9":
        return 4
    if given_card[1] == "10":
        return 5
    if given_card[1] == "Валет":
        return 6
    if given_card[1] == "Дама":
        return 7
    if given_card[1] == "Король":
        return 8
    if given_card[1] == "Туз":
        return 9
    return 1


def first_card_stronger_than_second_card(first_card, second_card, trump_type):
    if (first_card[0] == trump_type and second_card[0] == trump_type) or (first_card[0] != trump_type and second_card[0] != trump_type):
        if card_value_as_int(first_card) > card_value_as_int(second_card):
            return True
    else:
        if first_card[0] == trump_type:
            return True
    return False


def target_is_valid_card_to_play(given_card, given_field, trump_type, opponent_deck_length, is_attacker):
    for element in given_field:
        if len(element) == 1:
            if not (is_attacker) and (given_card[0] == element[0][0] or given_card[0] == trump_type) and first_card_stronger_than_second_card(given_card, element[0], trump_type):
                return True
            elif is_attacker and not(len(given_field) >= opponent_deck_length) and element[0][1] == given_card[1]:
                return True
        elif is_attacker and not(len(given_field) >= opponent_deck_length) and len(element) == 2 and (element[0][1] == given_card[1] or element[1][1] == given_card[1]):
            return True
    return False


def highest_trump_card_value(given_deck, trump_type):
    trump_value = 0
    for element in given_deck:
        if element[0] == trump_type and card_value_as_int(element) > trump_value:
            trump_value = card_value_as_int(element)
    return trump_value


def stich_generic_trump_field_deck_message(given_pdeck, given_cdeck, given_field, trump_type, given_leftover_deck, gid):
    large_image = Image.open(os.path.join(config.PACK_PATH, "table.jpg"))
    if len(given_leftover_deck):
        ldeck = 0
        if len(given_leftover_deck) < 5:
            ldeck = len(given_leftover_deck)-1
        elif len(given_leftover_deck) < 13:
            ldeck = 7
        else:
            ldeck = 12
        funky_number = len(given_leftover_deck) - 1
        funky_image = Image.open(os.path.join(config.PACK_PATH, f"{given_leftover_deck[funky_number][1]}_{given_leftover_deck[funky_number][0]}.jpg"))
        funky_image = funky_image.resize((200,275))
        funky_pos = (50, 10)
        large_image.paste(funky_image, funky_pos)
        if ldeck > 0:
            for i in range(ldeck):
                small_image = Image.open(os.path.join(config.PACK_PATH, f"cardback.jpg"))
                small_image = small_image.resize((200, 275))
                pos = (50, 75 + 6 * i)  # Позиция для первого маленького изображения
                large_image.paste(small_image, pos)
    pos_player = (0, 0)
    pos_field = (0, 0)
    pos_comp = (0, 0)
    center = 960 - 50 - (25 * len(given_pdeck))
    center_field = 960 - (125 * len(given_field))
    #print(f"center: {center}")
    #print(f"center_field: {center_field}") 
    index = 0
    for el in given_pdeck:
        # Открываем маленькие изображения
        small_image1 = Image.open(os.path.join(config.PACK_PATH, f"{el[1]}_{el[0]}.jpg"))
        small_image1 = small_image1.resize((200, 275))
        # Определяем позиции, где будем размещать маленькие изображения
        pos_player = (center + (50 * index), 750)  # Позиция для первого маленького изображения
        # Накладываем маленькие изображения на большое
        large_image.paste(small_image1, pos_player)
        index += 1
    index = 0
    for el in given_cdeck:
        # Открываем маленькие изображения
        small_image2 = Image.open(os.path.join(config.PACK_PATH, f"cardback.jpg"))
        small_image2 = small_image2.resize((200, 275))
        # Определяем позиции, где будем размещать маленькие изображения
        pos_comp = (center + (50 * index), -100)  # Позиция для первого маленького изображения
        # Накладываем маленькие изображения на большое
        large_image.paste(small_image2, pos_comp)
        index += 1
    index = 0
    for element in given_field:
        microindex = 0
        #print(f"Попытка нарисовать поле, элемент: {element}")
        for elel in element:
            # Открываем маленькие изображения
            #print(f"Попытка нарисовать поле, карта : {elel}; Элемент: {element}")
            small_imagef = Image.open(os.path.join(config.PACK_PATH, f"{elel[1]}_{elel[0]}.jpg"))
            small_imagef = small_imagef.resize((200, 275))
            # Определяем позиции, где будем размещать маленькие изображения
            pos_field = (center_field + (250 * index), 255 + (45 * microindex))  # Позиция для первого маленького изображения
            microindex += 1
            # Накладываем маленькие изображения на большое
            large_image.paste(small_imagef, pos_field)
        index += 1
        
    large_image.save(f"{config.RESULT_PATH}/fool_result_image_{gid}.jpg")
    the_message = f"Козырная масть: {type_to_ru_string(trump_type)}\n\n"
    if len(given_field):
        field_list = "Карты в игре: \n"
        for element in given_field:
            for elel in element:
                field_list+=f"{elel[1]} {type_to_ru_adj_string(elel[0])}    "
            field_list+="\n"
        the_message+=field_list
        the_message+="\n"
    card_list = "Ваши карты: \n"
    for i in range(len(given_pdeck)):
        card_list+=f"{given_pdeck[i][1]} {type_to_ru_adj_string(given_pdeck[i][0])};  "
        if not((i+1)%4) or i == len(given_pdeck)-1:
            card_list+="\n"
    the_message+=card_list
    return the_message



@router.callback_query(F.data == 'game_fool')
async def play_start_fool(callback: CallbackQuery, state: FSMContext):
    uid = callback.message.from_user.id
    slovar = await state.get_data()

    # Проверка наличия "Айди" в словаре
    if "Айди" in slovar:
        pass
    else:
        slovar["Айди"] = uid
    # kb = bet_kb(lobby_list)
    # slovar["Lobby_klava"] = kb.model_dump()
    slovar["Деньги"] = money  # Убедитесь, что переменная money определена
    slovar["attacker"] = True
    slovar["player_takes"] = False
    slovar["comp_takes"] = False
    slovar["should_count_cards"] = False
    slovar["field"] = []

    print(f"Игрок начал игру!")
    # await message.answer(text="Выберите лобби: ", reply_markup=kb)
    await callback.message.answer(
        "Добро пожаловать в Дурака!\n\n"
        "Правила игры:\n"
        "1. Никому не говорить об игре Дурак.\n"
        "2. Побеждает тот, у кого первым кончаются карты.\n"
        "3. Игра не даст вам сделать ход не по правилам, потому больше вам ничего знать не надо.\n", parse_mode="HTML", reply_markup=startupplayonly)
    await state.update_data(slovar)
    await state.set_state(FoolStates.start_play)
    # await state.set_state(FoolStates.bet_chose)


@router.callback_query(FoolStates.start_play)
async def start_game(callback: CallbackQuery, state: FSMContext, bot: Bot):
    slovar = await state.get_data()
    # slovar["Ставка"] = int(callback.data)

    # money_bet_check = money - int(callback.data)
    # await callback.message.answer(f"Ваша ставка: {callback.data}")
    await callback.message.answer(f"Раздаем картишки...")
    await callback.answer()
    time.sleep(1)
    deck = create_deck()
    last_card = deck.pop(0)
    trump_type = last_card[0]
    deck.append(last_card)
    player_deck = [deck.pop(0), deck.pop(1), deck.pop(2), deck.pop(3), deck.pop(4), deck.pop(5)]
    comp_deck = [deck.pop(0), deck.pop(0), deck.pop(0), deck.pop(0), deck.pop(0), deck.pop(0)]
    while not (target_is_valid_deck(player_deck, trump_type)) or not (target_is_valid_deck(comp_deck, trump_type)):
        deck = create_deck()
        last_card = deck.pop(0)
        trump_type = last_card[0]
        deck.append(last_card)
        player_deck = [deck.pop(0), deck.pop(1), deck.pop(2), deck.pop(3), deck.pop(4), deck.pop(5)]
        comp_deck = [deck.pop(0), deck.pop(0), deck.pop(0), deck.pop(0), deck.pop(0), deck.pop(0)]
        await callback.message.answer(f"Перераздаем картишки...")
        time.sleep(1)
    if highest_trump_card_value(player_deck, trump_type) > highest_trump_card_value(comp_deck, trump_type):
        slovar["attacker"] = False
        cdeck_card = random.randint(0, len(comp_deck) - 1)
        while comp_deck[cdeck_card][0] == trump_type:
            cdeck_card -= 1
            if cdeck_card < 0:
                cdeck_card = 5
        slovar["field"].append([comp_deck.pop(cdeck_card)])
        comp_deck = sort_deck(comp_deck)
        slovar["Колода компа"] = comp_deck
    slovar["Колода игрока"] = player_deck
    slovar["Колода компа"] = comp_deck
    slovar["Козырь"] = trump_type
    slovar["Остаток колоды"] = deck
    await state.update_data(slovar)
    await state.set_state(FoolStates.game_is_on)
    field = slovar["field"]
    print(f"Игрок зашел в игру!\n Field: {field}\n Player deck: {player_deck}\n Comp deck: {comp_deck}\n Deck: {deck}")
    message = stich_generic_trump_field_deck_message(player_deck, comp_deck, field, trump_type, deck, slovar["Айди"])
    document = FSInputFile(os.path.join(config.RESULT_PATH, f"fool_result_image_{slovar['Айди']}.jpg"))
    await bot.send_photo(chat_id=callback.message.chat.id, photo=document,
                         caption=message)
    # await callback.message.answer()
    if slovar["attacker"]:
        await callback.message.answer(f"Выберите действие: ", reply_markup=playonly)
    else:
        await callback.message.answer(f"Выберите действие: ", reply_markup=playtake)
        # await bot.send_photo(chat_id=callback.message.chat.id, photo=document,
        # caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")


async def ai_turn(callback: CallbackQuery, state: FSMContext, bot: Bot):
    slovar = await state.get_data()
    player_deck = slovar["Колода игрока"]
    comp_deck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    trump_type = slovar["Козырь"]
    field = slovar["field"]
    attacker = slovar["attacker"]
    player_takes = slovar["player_takes"]
    comp_takes = slovar["comp_takes"]
    should_take_cards = False
    ai_won = False
    if (len(player_deck) > 0 and len(comp_deck) > 0) or len(deck) or slovar["comp_takes"] or slovar["player_takes"]:
        should_get_a_turn = 1
        #print(f"ИИшка пытаешься сходить, карт в колоде: {len(deck)}; карт у игрока и бота: {len(player_deck)}; {len(comp_deck)}")
        while should_get_a_turn > 0:
            # Ход компа
            comp_deck = sort_deck(comp_deck)
            # time.sleep(1)
            if not (attacker) and len(player_deck):
                made_a_play = False
                # пусть пробует сходить НЕ козырями.
                comp_first_trump_card = -1
                for i in range(len(comp_deck)):
                    if i >= len(comp_deck):
                        break
                    if (not (len(field)) or target_is_valid_card_to_play(comp_deck[i], field, trump_type, len(player_deck), not (attacker))):
                        if comp_deck[i][0] == trump_type:
                            if comp_first_trump_card == -1:
                                comp_first_trump_card = i
                        else:
                            field.append([comp_deck.pop(i)])
                            made_a_play = True
                            i -= 1
                # уж лучше сходить козырем чем совсем ничем.
                # однако если бито то козырь наверное выкладывать не стоит
                if not (made_a_play) and comp_first_trump_card != -1 and not (len(deck) and len(field)):
                    field.append([comp_deck.pop(comp_first_trump_card)])
                elif not (len(comp_deck)) and not (len(deck)) and not (slovar["comp_takes"]):
                    ai_won = True
                    break
                elif not (len(field)) and len(comp_deck):
                    print("Ошибка! Компьютер не смог выбрать чем ходить! Выбираю за него...")
                    field.append([comp_deck.pop(0)])
                if not (any(len(element) == 1 for element in field)) and not (player_takes):
                    # Бито
                    await callback.message.answer(f"Бито!")
                    if len(deck):
                        should_take_cards = True
                    attacker = True
                    field.clear()
                    # time.sleep(1)
                if player_takes:
                    player_takes = False
                    should_get_a_turn += 1
                    if len(deck):
                        should_take_cards = True
                    # print("Вы берете:")
                    cards_taken_line = "Вы берете: \n"
                    counter = 0
                    for element in field:
                        for card in element:
                            cards_taken_line += f"{card[1]} {type_to_ru_adj_string(card[0])};  "
                            counter += 1
                            if counter >= 3:
                                counter = 0
                                cards_taken_line += "\n"
                            # print(f" {card}", end = "")
                            player_deck.append(card)
                    await callback.message.answer("" + cards_taken_line)
                    # print("")
                    field.clear()
                    # time.sleep(1)
            # комп защищающийся
            elif len(player_deck):
                for element in field:
                    comp_first_trump_card = -1
                    if len(element) == 1:
                        # пусть пробует сходить НЕ козырями.
                        for i in range(len(comp_deck)):
                            if (comp_deck[i][0] == element[0][0] or comp_deck[i][0] == trump_type) and first_card_stronger_than_second_card(comp_deck[i], element[0], trump_type):
                                if comp_deck[i][0] == trump_type:
                                    if comp_first_trump_card == -1:
                                        comp_first_trump_card = i
                                else:
                                    element.append(comp_deck.pop(i))
                                # i-=1
                                break
                    if len(element) == 1 and comp_first_trump_card != -1:
                        # если не получилось закрыть все не козырями, пускай в дело козыри
                        element.append(comp_deck.pop(comp_first_trump_card))
                if not(len(comp_deck)) and not(len(deck)) and not(slovar["comp_takes"]):
                    ai_won = True
                    break;           
                if any(len(element) == 1 for element in field):
                    await callback.message.answer(f"Беру! Докидываете?")
                    print("Комп: Беру!")
                    comp_takes = True
                    time.sleep(1)

            if should_take_cards and len(deck):
                should_take_cards = False
                # should_show_cards_left = True
                while (len(player_deck) < 6 or len(comp_deck) < 6) and len(deck):
                    if len(player_deck) < 6:
                        player_deck.append(deck.pop(0))
                    if len(comp_deck) < 6 and len(deck):
                        comp_deck.append(deck.pop(0))
                    if not (len(deck)):
                        await callback.message.answer("Конец колоды!")

            slovar["Колода игрока"] = player_deck
            slovar["Колода компа"] = comp_deck
            slovar["Остаток колоды"] = deck
            slovar["field"] = field
            slovar["attacker"] = attacker
            slovar["player_takes"] = player_takes
            slovar["comp_takes"] = comp_takes
            should_get_a_turn -= 1
        await state.update_data(slovar)
        print(f"ИИшка доходила, карт в колоде: {len(deck)}; карт у игрока и бота: {len(player_deck)}; {len(comp_deck)}")

        if not (ai_won):
            field = slovar["field"]
            player_deck = slovar["Колода игрока"]
            # await message.answer(stich_generic_trump_field_deck_message(player_deck, field, trump_type, deck, slovar["Айди"]))
            message = stich_generic_trump_field_deck_message(player_deck, comp_deck, field, trump_type, deck,slovar["Айди"])
            document = FSInputFile(os.path.join(config.RESULT_PATH, f"fool_result_image_{slovar['Айди']}.jpg"))
            await bot.send_photo(chat_id=callback.message.chat.id, photo=document,
                                 caption=message)
            if slovar["attacker"] and not (len(field)):
                await callback.message.answer(f"Выберите действие: ", reply_markup=playonly)
            elif slovar["attacker"] and all(len(element) == 2 for element in field):
                await callback.message.answer(f"Выберите действие: ", reply_markup=playbeaten)
            elif not (slovar["attacker"]) and any(len(element) == 1 for element in field):
                await callback.message.answer(f"Выберите действие: ", reply_markup=playtake)
            else:
                await callback.message.answer(f"Выберите действие: ", reply_markup=playpass)
        else:
            print(f"Игрок проиграл: {len(deck)}; карт у игрока и бота: {len(player_deck)}; {len(comp_deck)}")
            # UserData.fool_stats.total_games += 1
            # UserData.fool_stats.loses += 1
            # UserData.balance -= 100
            # await RedisStorage.update_user(UserData.id, UserData)
            await callback.message.answer(f"Игра окончена, вы проиграли!", reply_markup=weirdfinal_kb)
            await state.update_data(slovar)
            await state.set_state(FoolStates.itog)

    else:
        if len(player_deck):
            print(f"Игрок проиграл: {len(deck)}; карт у игрока и бота: {len(player_deck)}; {len(comp_deck)}")
            # UserData.fool_stats.total_games += 1
            # UserData.fool_stats.loses += 1
            # UserData.balance -= 100
            # await RedisStorage.update_user(UserData.id, UserData)
            await callback.message.answer(f"Игра окончена, вы проиграли!", reply_markup=weirdfinal_kb)
        else:
            print(f"Игрок выиграл: {len(deck)}; карт у игрока и бота: {len(player_deck)}; {len(comp_deck)}")
            # UserData.fool_stats.total_games += 1
            # UserData.fool_stats.wins += 1
            # UserData.balance += 100
            # await RedisStorage.update_user(UserData.id, UserData)
            await callback.message.answer(f"Игра окончена, вы победили!", reply_markup=weirdfinal_kb)
        await state.update_data(slovar)
        await state.set_state(FoolStates.itog)


@router.callback_query(F.data == 'foolplaycard')
# choosing_card
async def play_card(query: CallbackQuery, state: FSMContext, bot: Bot):
    slovar = await state.get_data()
    player_deck = slovar["Колода игрока"]
    comp_deck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    trump_type = slovar["Козырь"]
    field = slovar["field"]
    attacker = slovar["attacker"]

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Назад", callback_data=f"nope"))
    for i in range(len(player_deck)):
        if not (len(field)) or target_is_valid_card_to_play(player_deck[i], field, trump_type, len(comp_deck), attacker):
            the_string = f"{player_deck[i][1]} {type_to_ru_adj_string(player_deck[i][0])}"
            if player_deck[i][0] == trump_type:
                the_string += "*"
            builder.add(InlineKeyboardButton(text=the_string, callback_data=f"cardnum_{i + 1}"))
    builder.adjust(3)
    await query.answer()
    await query.message.answer(
        "Выберите карту (показаны только те, что можно разыграть):",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    await state.set_state(FoolStates.choosing_card)


@router.callback_query(FoolStates.choosing_card)
async def playing_the_card_thing(query: CallbackQuery, state: FSMContext, bot: Bot):
    slovar = await state.get_data()
    player_deck = slovar["Колода игрока"]
    comp_deck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    trump_type = slovar["Козырь"]
    field = slovar["field"]
    attacker = slovar["attacker"]
    if query.data.startswith("cardnum_"):
        pdeck_card = int(query.data.split("_")[1])
        if not (len(field)) or target_is_valid_card_to_play(player_deck[pdeck_card - 1], field, trump_type, len(comp_deck), attacker):
            if not (attacker) and any(len(element) == 1 for element in field):
                for element in field:
                    if len(element) == 1 and (player_deck[pdeck_card - 1][0] == element[0][0] or player_deck[pdeck_card - 1][0] == trump_type) and first_card_stronger_than_second_card(player_deck[pdeck_card - 1],element[0], trump_type):
                        element.append(player_deck.pop(pdeck_card - 1))
                        break
                # if not(any(len(element) == 1 for element in field)):
                    # break;
            elif attacker:
                field.append([player_deck.pop(pdeck_card - 1)])
            else:
                print("Что-то создает скриптовые ошибки - карта не разыграна.")
            slovar["Колода игрока"] = player_deck
            slovar["field"] = field
            await state.update_data(slovar)
            # await query.message.answer(stich_generic_trump_field_deck_message(player_deck, field, trump_type, deck, slovar["Айди"]))
            message = stich_generic_trump_field_deck_message(player_deck, comp_deck, field, trump_type, deck, slovar["Айди"])
            document = FSInputFile(os.path.join(config.RESULT_PATH, f"fool_result_image_{slovar['Айди']}.jpg"))
            await bot.send_photo(chat_id=query.message.chat.id, photo=document,
                                 caption=message)
            if attacker and all(len(element) == 2 for element in field):
                await query.message.answer(f"Сыграть еще карту?", reply_markup=playbeaten)
            elif not (attacker) and any(len(element) == 1 for element in field):
                await query.message.answer(f"Сыграть еще карту?", reply_markup=playtake)
            else:
                await query.message.answer(f"Сыграть еще карту?", reply_markup=playpass)
            await query.answer()
            await state.set_state(FoolStates.game_is_on)
        else:
            print("Вы не можете сыграть эту карту!")
    else:
        # await query.message.answer(stich_generic_trump_field_deck_message(player_deck, field, trump_type, deck, slovar["Айди"]))
        message = stich_generic_trump_field_deck_message(player_deck, comp_deck, field, trump_type, deck, slovar["Айди"])
        document = FSInputFile(os.path.join(config.RESULT_PATH, f"fool_result_image_{slovar['Айди']}.jpg"))
        await query.answer()
        await state.set_state(FoolStates.game_is_on)
        await bot.send_photo(chat_id=query.message.chat.id, photo=document,
                             caption=message)
        if slovar["attacker"] and not (len(field)):
            await query.message.answer(f"Выберите действие: ", reply_markup=playonly)
        elif slovar["attacker"] and all(len(element) == 2 for element in field):
            await query.message.answer(f"Выберите действие: ", reply_markup=playbeaten)
        elif not (slovar["attacker"]) and any(len(element) == 1 for element in field):
            await query.message.answer(f"Выберите действие: ", reply_markup=playtake)
        else:
            await query.message.answer(f"Выберите действие: ", reply_markup=playpass)


@router.callback_query(F.data == 'foolpass')
async def fpass(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # print("huyki")
    slovar = await state.get_data()
    if slovar["comp_takes"]:
        print(f"Игрок пасанул и комп берет?")
        deck = slovar["Остаток колоды"]
        field = slovar["field"]
        comp_deck = slovar["Колода компа"]
        # Комп берет
        slovar["comp_takes"] = False
        if True:
            for element in field:
                for card in element:
                    comp_deck.append(card)
            field.clear()
        player_deck = slovar["Колода игрока"]
        if len(deck):
            # should_show_cards_left = True
            while (len(player_deck) < 6 or len(comp_deck) < 6) and len(deck):
                if len(player_deck) < 6:
                    player_deck.append(deck.pop(0))
                if len(comp_deck) < 6 and len(deck):
                    comp_deck.append(deck.pop(0))
                if not (len(deck)):
                    await callback.message.answer("Конец колоды!")
        slovar["Остаток колоды"] = deck
        slovar["field"] = field
        slovar["Колода компа"] = comp_deck
        await state.update_data(slovar)

        # field = slovar["field"]
        trump_type = slovar["Козырь"]
        player_deck = slovar["Колода игрока"]
        # await message.answer(stich_generic_trump_field_deck_message(player_deck, field, trump_type, deck, slovar["Айди"]))
        message = stich_generic_trump_field_deck_message(player_deck, comp_deck, field, trump_type, deck, slovar["Айди"])
        document = FSInputFile(os.path.join(config.RESULT_PATH, f"fool_result_image_{slovar['Айди']}.jpg"))
        await bot.send_photo(chat_id=callback.message.chat.id, photo=document,
                             caption=message)
        if slovar["attacker"] and not (len(field)):
            await callback.message.answer(f"Выберите действие: ", reply_markup=playonly)
        elif slovar["attacker"] and all(len(element) == 2 for element in field):
            await callback.message.answer(f"Выберите действие: ", reply_markup=playbeaten)
        elif not (slovar["attacker"]) and any(len(element) == 1 for element in field):
            await callback.message.answer(f"Выберите действие: ", reply_markup=playtake)
        else:
            await callback.message.answer(f"Выберите действие: ", reply_markup=playpass)
        await callback.answer()
    else:
        print(f"Игрок пасанул")
        await ai_turn(callback, state, bot)
        await callback.answer()


@router.callback_query(F.data == 'fooltake')
async def ftake(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print("Игрок берет")
    slovar = await state.get_data()
    slovar["player_takes"] = True
    await state.update_data(slovar)
    await ai_turn(callback, state, bot)
    await callback.answer()


@router.callback_query(F.data == 'foolbeaten')
async def fbeaten(callback: CallbackQuery, state: FSMContext, bot: Bot):
    print("Игрок объявил бито")
    slovar = await state.get_data()
    slovar["attacker"] = not (slovar["attacker"])
    slovar["field"].clear()
    player_deck = slovar["Колода игрока"]
    comp_deck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    if len(deck):
        # should_show_cards_left = True
        while (len(player_deck) < 6 or len(comp_deck) < 6) and len(deck):
            if len(player_deck) < 6:
                player_deck.append(deck.pop(0))
            if len(comp_deck) < 6 and len(deck):
                comp_deck.append(deck.pop(0))
            if not (len(deck)):
                await callback.message.answer("Конец колоды!")
    slovar["Колода игрока"] = player_deck
    slovar["Колода компа"] = comp_deck
    slovar["Остаток колоды"] = deck
    await state.update_data(slovar)

    await ai_turn(callback, state, bot)
    await callback.answer()


@router.callback_query(F.data == 'menu')
async def exit(callback: CallbackQuery, user_data: UserData, state: FSMContext, redis: RedisStorage):
    slovar = await state.get_data()
    user_data.fool_stats.total_games += 1
    if len(slovar["Колода игрока"]):
        user_data.fool_stats.loses += 1
        user_data.balance -= 100
    else:
        user_data.fool_stats.total_games += 1
        user_data.fool_stats.wins += 1
        user_data.balance += 100
    await redis.update_user(user_data.id, user_data)
    await state.clear()
    await Window.main_menu(callback.message, user_data, state)