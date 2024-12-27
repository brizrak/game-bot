import os.path
import time
import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from PIL import Image

from app.config import config
from app.bot.handlers.blackjack.datas import lobby_list, create_deck, all_stavkas
from app.bot.handlers.blackjack.keyboard import bet_kb, make_bet_kb, gg, gg1, gg2, final_kb, split_kb
from app.bot.handlers.states import BlackjackStates, GlobalStates
from app.bot.handlers.delete_message import delete_previous_message, add_message
from app.bot.utils.models import UserData
from app.bot.utils.redis import RedisStorage
from app.bot.handlers.windows import Window

router = Router()

maindict = {}


def scoring(deck):
    score = 0
    for el in deck:

        if el[1].isdigit():
            score += int(el[1])
        elif el[1] in ["валет", "дама", "король"]:
            score += 10
        elif el[1] == "туз" and (score + 11) <= 21:
            score += 11
        elif el[1] == "туз" and (score + 11) > 21:
            score += 1
    return score


@router.callback_query(F.data == 'menu')
async def to_menu(callback: CallbackQuery, state: FSMContext, user_data: UserData):
    await delete_previous_message(state, callback.message)
    await state.clear()
    await Window.main_menu(callback.message, user_data, state)


@router.callback_query(F.data == 'game_21')
async def play_start(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    slovar = await state.get_data()

    # Проверка наличия "Айди" в словаре
    if "Айди" in slovar:
        pass
    else:
        slovar["Айди"] = uid
    kb = bet_kb(lobby_list)
    slovar["Lobby_klava"] = kb.model_dump()
    slovar["Action"] = True
    slovar["Split_choose"] = "str"
    slovar["Split_cond"] = 0
    slovar["Split_stop"] = 0

    msg = await callback.bot.send_message(chat_id=callback.message.chat.id, text="Выберите лобби: ", reply_markup=kb)
    await delete_previous_message(state, callback.message)
    await state.update_data(slovar)
    await state.set_state(BlackjackStates.bet_chose)
    await callback.answer()
    await add_message(state, msg)


@router.callback_query(F.data == 'lobby')
async def play(callback: CallbackQuery, state: FSMContext):
    slovar = await state.get_data()
    # Проверка наличия "Айди" в словаре
    if "Айди" not in slovar:
        uid = callback.from_user.id
        slovar["Айди"] = uid

    kb = bet_kb(lobby_list)
    slovar["Lobby_klava"] = kb.model_dump()
    slovar["Action"] = True

    msg = await callback.message.answer(text="Выберите лобби: ", reply_markup=kb)
    await delete_previous_message(state, callback.message)
    await state.update_data(slovar)
    await add_message(state, msg)
    await state.set_state(BlackjackStates.bet_chose)
    await callback.answer()


@router.callback_query(F.data == "yes")
@router.callback_query((BlackjackStates.bet_chose) or (F.data.contains("/")))
async def bet_take(callback: CallbackQuery, state: FSMContext, user_data: UserData):
    if callback.data == "yes":
        data = await state.get_data()
        bet = data["lobby"].split("/")
    else:
        await state.update_data(lobby=callback.data)
        bet = callback.data.split("/")
    if user_data.balance < int(bet[1]):
        msg = await callback.message.answer(text="Недостаточно денег. Выберите другое лобби",
                                            reply_markup=bet_kb(lobby_list))
        await delete_previous_message(state, callback.message)
        await add_message(state, msg)
    else:
        x = int(bet[1]) / int(bet[0]) + 1
        bet_list = [int(bet[0]) * i for i in range(1, int(x))]
        msg = await callback.message.answer(text="Отлично. Сделайте ставку", reply_markup=make_bet_kb(bet_list))
        await delete_previous_message(state, callback.message)
        await add_message(state, msg)
        await state.set_state(BlackjackStates.start_play)
    await callback.answer()


@router.callback_query(BlackjackStates.start_play)
@router.callback_query(F.data.in_(all_stavkas))
async def bet_make(callback: CallbackQuery, state: FSMContext, bot: Bot, user_data: UserData, redis: RedisStorage):
    slovar = await state.get_data()
    messages = slovar["old_messages"]
    if not messages:
        messages = []
    is_double = False
    slovar["Статус"] = is_double

    slovar["Ставка"] = int(callback.data)

    money_bet_check = user_data.balance - int(callback.data)
    await callback.message.answer(f"Ваша ставка: {callback.data}")
    await delete_previous_message(state, callback.message)

    time.sleep(1)
    msg = await callback.message.answer(f"Раздаем картишки...")
    messages.append(msg.message_id)
    time.sleep(4)
    deck = create_deck()
    player_deck = [deck.pop(), deck.pop()]
    comp_deck = [deck.pop(), deck.pop()]
    slovar["Колода игрока"] = player_deck
    slovar["Колода компа"] = comp_deck
    slovar["Остаток колоды"] = deck
    large_image = Image.open(os.path.join(config.PACK_PATH, "table_dealer.jpg"))
    index = 0
    player_score = scoring(player_deck)
    await callback.answer()

    comp_score = scoring([comp_deck[0]])
    for elem, el in zip(player_deck, comp_deck):
        # Открываем маленькие изображения
        small_image1 = Image.open(os.path.join(config.PACK_PATH, f"{elem[1]}_{elem[0]}.jpg"))
        small_image1 = small_image1.resize((225, 225))
        if index == 1:
            small_image2 = Image.open(os.path.join(config.PACK_PATH, f"cardback.jpg"))
            small_image2 = small_image2.resize((225, 225))
            # Определяем позиции, где будем размещать маленькие изображения
            pos_player = (500 + 250 * index, 800)  # Позиция для первого маленького изображения
            pos_comp = (500 + 250 * index, 50)  # Позиция для второго маленького изображения
            slovar["Ppos"] = pos_player
            slovar["Cpos"] = pos_comp

            # Накладываем маленькие изображения на большое
            large_image.paste(small_image2, pos_comp)
            large_image.paste(small_image1, pos_player)
        else:
            small_image2 = Image.open(os.path.join(config.PACK_PATH, f"{el[1]}_{el[0]}.jpg"))
            small_image2 = small_image2.resize((225, 225))
            # Определяем позиции, где будем размещать маленькие изображения
            pos_player = (500 + 250 * index, 800)  # Позиция для первого маленького изображения
            pos_comp = (500 + 250 * index, 50)  # Позиция для второго маленького изображения
            slovar["Ppos"] = pos_player
            slovar["Cpos"] = pos_comp

            # Накладываем маленькие изображения на большое
            large_image.paste(small_image2, pos_comp)
            large_image.paste(small_image1, pos_player)
        index += 1

        # Сохраняем результат
    large_image.save(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")
    document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))
    action = slovar["Action"]

    msg = await bot.send_photo(chat_id=callback.message.chat.id, photo=document,
                               caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
    messages.append(msg.message_id)
    exit = False
    if player_score == 21:
        user_data.balance += 2 * int(callback.data)
        await callback.message.answer(f"Блэкджэк! Ваш баланс: {user_data.balance}")
        maindict = slovar
        await state.clear()
        msg = await callback.message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
        messages.append(msg.message_id)
        exit = True
    if comp_score == 21:
        user_data.balance -= int(callback.data)
        await callback.message.answer(f"Не повезло! Вы проиграли! Ваш баланс: {user_data.balance}")
        maindict = slovar
        await state.clear()
        msg = await callback.message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
        messages.append(msg.message_id)
        exit = True

    if not exit:
        if player_deck[0][1] == player_deck[1][1] and money_bet_check >= 0 and action == True:
            msg = await callback.message.answer(f"Выберите действие: ", reply_markup=gg)
            messages.append(msg.message_id)

        if money_bet_check < 0 or action == False:
            msg = await callback.message.answer(f"Выберите действие: ", reply_markup=gg1)
            messages.append(msg.message_id)
        if action == True:
            msg = await callback.message.answer(f"Выберите действие: ", reply_markup=gg2)
            messages.append(msg.message_id)

    slovar["old_messages"] = messages
    await state.update_data(slovar)
    await redis.update_user(user_data.id, user_data)


@router.message(F.text == "Взять карту")
async def take_card(message: Message, state: FSMContext, user_data: UserData, bot: Bot):
    slovar = await state.get_data()
    messages = slovar["old_messages"]
    if not messages:
        messages = []
    messages.append(message.message_id)
    split_ch = slovar["Split_choose"]
    act = slovar["Action"]
    pdeck = slovar["Колода игрока"]
    cdeck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    cond = slovar["Split_cond"]
    if act:
        lrg_img = Image.open(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")
        pdeck.append(deck.pop())
        slovar["Колода игрока"] = pdeck
        player_score = scoring(pdeck)
        comp_score = scoring(cdeck)
        small_image1 = Image.open(os.path.join(config.PACK_PATH, f"{pdeck[-1][1]}_{pdeck[-1][0]}.jpg"))
        small_image1 = small_image1.resize((225, 225))

        # Определяем позиции, где будем размещать маленькие изображения
        pos_player = (slovar["Ppos"][0] + 250, 800)  # Позиция для первого маленького изображения
        slovar["Ppos"] = pos_player
        # Накладываем маленькие изображения на большое
        lrg_img.paste(small_image1, pos_player)

        lrg_img.save(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")

        document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))

        msg = await bot.send_photo(chat_id=message.chat.id, photo=document,
                                   caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
        messages.append(msg.message_id)
        if player_score > 21:
            await message.answer(f"Вы проиграли! Ваш баланс: {user_data.balance}")
            msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
            messages.append(msg.message_id)
        else:
            msg = await message.answer(f"Выберите действие: ", reply_markup=gg2)
            messages.append(msg.message_id)
        slovar["old_messages"] = messages
        await state.update_data(slovar)


@router.message(F.text == "Хватит")
async def hvatit(message: Message, state: FSMContext, bot: Bot, user_data: UserData, redis: RedisStorage):
    slovar = await state.get_data()

    messages = slovar["old_messages"]
    if not messages:
        messages = []
    messages.append(message.message_id)
    pdeck = slovar["Колода игрока"]
    cdeck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    is_double = slovar["Статус"]
    bet = slovar["Ставка"]
    money = user_data.balance
    if slovar["Action"]:
        slovar["Колода игрока"] = pdeck
        player_score = scoring(pdeck)
        large_image = Image.open(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))

        comp_score = scoring(cdeck)

        small_image2 = Image.open(os.path.join(config.PACK_PATH, f"{cdeck[-1][1]}_{cdeck[-1][0]}.jpg"))
        small_image2 = small_image2.resize((225, 225))
        pos_comp = slovar["Cpos"]
        large_image.paste(small_image2, pos_comp)
        while comp_score <= 17:
            cdeck.append(deck.pop())
            comp_score = scoring(cdeck)

        small_image2 = Image.open(os.path.join(config.PACK_PATH, f"{cdeck[-1][1]}_{cdeck[-1][0]}.jpg"))
        small_image2 = small_image2.resize((225, 225))
        pos_comp = (pos_comp[0] + 250, 50)
        large_image.paste(small_image2, pos_comp)
        large_image.save(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")
        document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))
        msg = await bot.send_photo(chat_id=message.chat.id, photo=document,
                                   caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
        messages.append(msg.message_id)
        await asyncio.sleep(1)

        if (player_score < comp_score and comp_score <= 21) or player_score > 21:
            if not is_double:
                money -= bet
                await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                maindict = slovar
                # await state.clear()
                msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                messages.append(msg.message_id)
            else:
                money -= 2 * bet
                await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                maindict = slovar
                # await state.clear()
                msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                messages.append(msg.message_id)
        elif player_score == 21 and player_score != comp_score:
            if is_double == False:
                money += bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                maindict = slovar
                # await state.clear()
                msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                messages.append(msg.message_id)

            else:
                money += 2 * bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                maindict = slovar
                # await state.clear()
                msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                messages.append(msg.message_id)

        elif (player_score <= 21 and player_score > comp_score) or comp_score > 21:
            if is_double == False:
                money += bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                maindict = slovar
                # await state.clear()
                msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                messages.append(msg.message_id)
            else:
                money += 2 * bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                maindict = slovar
                # await state.clear()
                msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                messages.append(msg.message_id)



        elif player_score == comp_score:
            await message.answer(f"Ничья! Ваш баланс: {money}")
            await asyncio.sleep(1)
            maindict = slovar
            # await state.clear()
            msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
            messages.append(msg.message_id)
        user_data.balance = money

        slovar["old_messages"] = messages
        await state.update_data(slovar)
        await redis.update_user(user_data.id, user_data)


@router.message(F.text == "Удвоить ставку")
async def double(message: Message, state: FSMContext, user_data: UserData, bot: Bot):
    slovar = await state.get_data()
    messages = slovar["old_messages"]
    if not messages:
        messages = []
    messages.append(message.message_id)
    pdeck = slovar["Колода игрока"]
    cdeck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    lrg_img = Image.open(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")
    pdeck.append(deck.pop())
    slovar["Колода игрока"] = pdeck
    player_score = scoring(pdeck)
    comp_score = scoring(cdeck)

    small_image1 = Image.open(os.path.join(config.PACK_PATH, f"{pdeck[-1][1]}_{pdeck[-1][0]}.jpg"))
    small_image1 = small_image1.resize((225, 225))

    # Определяем позиции, где будем размещать маленькие изображения
    pos_player = (slovar["Ppos"][0] + 250, 800)  # Позиция для первого маленького изображения
    slovar["Ppos"] = pos_player
    # Накладываем маленькие изображения на большое
    lrg_img.paste(small_image1, pos_player)

    lrg_img.save(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")
    document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))
    slovar["Статус"] = True

    msg = await bot.send_photo(chat_id=message.chat.id, photo=document,
                               caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
    messages.append(msg.message_id)
    if player_score > 21:
        await message.answer(f"Вы проиграли! Ваш баланс: {user_data.balance}")
        time.sleep(1)
        msg = await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
        messages.append(msg.message_id)
    else:
        msg = await message.answer("Выберите действие: ", reply_markup=gg1)
        messages.append(msg.message_id)
    slovar["old_messages"] = messages
    await state.update_data(slovar)

# @router.callback_query(F.data == 'lobby')
# async def exit(callback:CallbackQuery,state:FSMContext):
#     print("sasi")
#     kb = bet_kb(lobby_list)
#     await callback.message.answer(text="Выберите лобби: ", reply_markup=kb)

# @router.callback_query(F.data == 'menu')
# async def exit(callback:CallbackQuery,state:FSMContext):
#     await state.clear()


# @router.message(F.text == "Сплит")
# async def split(message: Message, state: FSMContext):
#     slovar = await state.get_data()
#     slovar["Action"] = False
#     await state.update_data(slovar)
#     sl1 = slovar.copy()
#     await state.clear()
#     await state.update_data(sl1)
#     await message.answer("Выберите колоду:", reply_markup=split_kb)


# @router.callback_query(F.data == "left")
# @router.callback_query(F.data == "right")
# async def add(callback: CallbackQuery, state: FSMContext):
#     slovar = await state.get_data()
#     print("tuta zdesya")
#     slovar["Split_choose"] = callback.data
#     await state.update_data(slovar)
#
#     await callback.message.answer(f"Выберите действие: ", reply_markup=gg1)
