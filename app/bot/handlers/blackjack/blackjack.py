import os.path
import time
import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from PIL import Image

from app.config import config
from app.bot.handlers.blackjack.datas import lobby_list, money, create_deck
from app.bot.handlers.blackjack.keyboard import bet_kb, make_bet_kb, gg, gg1, gg2, final_kb, split_kb
from app.bot.handlers.states import BlackjackStates

router = Router()


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


async def play_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    slovar = await state.get_data()

    # Проверка наличия "Айди" в словаре
    if "Айди" in slovar:
        pass
    else:
        slovar["Айди"] = uid
    kb = bet_kb(lobby_list)
    slovar["Lobby_klava"] = kb.model_dump()
    slovar["Деньги"] = money  # Убедитесь, что переменная money определена
    slovar["Action"] = True
    slovar["Split_choose"] = "str"
    slovar["Split_cond"] = 0
    slovar["Split_stop"] = 0

    await message.answer(text="Выберите лобби: ", reply_markup=kb)
    await state.update_data(slovar)
    await state.set_state(BlackjackStates.bet_chose)


@router.callback_query(F.data == "yes")
@router.callback_query(BlackjackStates.one_more)
async def play(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # Подтверждение нажатия кнопки
    slovar = await state.get_data()

    # Проверка наличия "Айди" в словаре
    if "Айди" not in slovar:
        uid = callback.from_user.id
        slovar["Айди"] = uid

    kb = bet_kb(lobby_list)
    slovar["Lobby_klava"] = kb.model_dump()
    slovar["Деньги"] = money  # Убедитесь, что переменная money определена
    slovar["Action"] = True

    await callback.message.answer(text="Выберите лобби: ", reply_markup=kb)
    await state.update_data(slovar)
    await state.set_state(BlackjackStates.bet_chose)


@router.callback_query((BlackjackStates.bet_chose) or (F.data.contains("/")))
async def bet_take(callback: CallbackQuery, state: FSMContext):
    bet = callback.data.split("/")

    if money < int(bet[1]):
        await callback.message.answer(text="Недостаточно денег. Выберите другое лобби", reply_markup=bet_kb(lobby_list))
    else:
        x = int(bet[1]) / int(bet[0]) + 1
        bet_list = [int(bet[0]) * i for i in range(1, int(x))]
        await callback.message.answer(text="Отлично. Сделайте ставку", reply_markup=make_bet_kb(bet_list))
        await state.set_state(BlackjackStates.start_play)


@router.callback_query(BlackjackStates.start_play)
async def bet_make(callback: CallbackQuery, state: FSMContext, bot: Bot):
    slovar = await state.get_data()
    is_double = False
    slovar["Статус"] = is_double

    slovar["Ставка"] = int(callback.data)

    money_bet_check = money - int(callback.data)
    await callback.message.answer(f"Ваша ставка: {callback.data}")
    time.sleep(1)
    await callback.message.answer(f"Раздаем картишки...")
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

    await bot.send_photo(chat_id=callback.message.chat.id, photo=document,
                         caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
    if player_score == 21:
        slovar["Деньги"] += 2 * int(callback.data)
        await callback.message.answer(f"Блэкджэк! Ваш баланс: {slovar['Деньги']}")
    if comp_score == 21:
        slovar['Деньги'] -= int(callback.data)
        await callback.message.answer(f"Не повезло! Вы проиграли! Ваш баланс: {slovar['Деньги']}")
    if player_deck[0][1] == player_deck[1][1] and money_bet_check >= 0 and action == True:
        await callback.message.answer(f"Выберите действие: ", reply_markup=gg)

    elif money_bet_check < 0 or action == False:
        await callback.message.answer(f"Выберите действие: ", reply_markup=gg1)
    elif action == True:
        await callback.message.answer(f"Выберите действие: ", reply_markup=gg2)

    await state.update_data(slovar)


@router.message(F.text == "Взять карту")
async def take_card(message: Message, state: FSMContext, bot: Bot):
    slovar = await state.get_data()
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
        await state.update_data(slovar)
        await bot.send_photo(chat_id=message.chat.id, photo=document,
                             caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
        if player_score > 21:
            await message.answer("Вы проиграли!")
            await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
        else:
            await message.answer(f"Выберите действие: ", reply_markup=gg2)
    else:
        if split_ch == "left":
            lrg_img = Image.open(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")

            comp_score = scoring([cdeck[0]])
            small_image1 = Image.open(os.path.join(config.PACK_PATH, f"{pdeck[-1][1]}_{pdeck[-1][0]}.jpg"))
            small_image1 = small_image1.resize((225, 225))

            if "Ppos_left" not in slovar:
                pdeck = [pdeck[0]]
                pdeck.append(deck.pop())
                slovar["Колода лево"] = pdeck
                pleft_score = scoring(pdeck)
                slovar["Pleft"] = pleft_score
                # Определяем позиции, где будем размещать маленькие изображения
                pos_player = (slovar["Ppos"][0] - 250, 700)  # Позиция для первого маленького изображения
                slovar["Ppos_left"] = pos_player
                # Накладываем маленькие изображения на большое
                lrg_img.paste(small_image1, pos_player)

                lrg_img.save(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")

                document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))
                await state.update_data(slovar)
                await bot.send_photo(chat_id=message.chat.id, photo=document,
                                     caption=f"Ваш счет (левая колода): {pleft_score}\nСчет дилера: {comp_score}")
                if pleft_score > 21:
                    await message.answer("Левая колода не сыграла! Попробуйте правую")
                    slovar["Split_choose"] = "right"
                    slovar["Split_cond"] += 1
                    if slovar["Split_cond"] == 2:
                        await message.answer(f"Не повезло(. Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        await message.answer(f"Выберите действие: ", reply_markup=gg2)
                    # await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                else:

                    await message.answer(f"Выберите действие: ", reply_markup=gg2)
            else:
                pdeck = slovar["Колода лево"]
                pdeck.append(deck.pop())
                slovar["Колода лево"] = pdeck
                pleft_score = scoring(pdeck)
                slovar["Pleft"] = pleft_score
                pos_player = (
                    slovar["Ppos"][0] - 250, slovar["Ppos_left"][1] - 100)  # Позиция для первого маленького изображения
                slovar["Ppos_left"] = pos_player
                # Накладываем маленькие изображения на большое
                lrg_img.paste(small_image1, pos_player)

                lrg_img.save(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")

                document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))
                await state.update_data(slovar)
                await bot.send_photo(chat_id=message.chat.id, photo=document,
                                     caption=f"Ваш счет (левая колода): {pleft_score}\nСчет дилера: {comp_score}")
                if pleft_score > 21:
                    await message.answer("Левая колода не сыграла! Попробуйте правую")
                    slovar["Split_choose"] = "right"
                    slovar["Split_cond"] += 1
                    if slovar["Split_cond"] == 2:
                        await message.answer(f"Не повезло(. Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        await message.answer(f"Выберите действие: ", reply_markup=gg2)
                    # await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                else:

                    await message.answer(f"Выберите действие: ", reply_markup=gg2)


        elif split_ch == "right":
            lrg_img = Image.open(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")
            # pdeck = [pdeck[1]]
            # pdeck.append(deck.pop())
            # slovar["Колода право"] = pdeck
            # pright_score = scoring(pdeck)
            # slovar["Pright"] = pright_score
            comp_score = scoring(cdeck)
            small_image1 = Image.open(os.path.join(config.PACK_PATH, f"{pdeck[-1][1]}_{pdeck[-1][0]}.jpg"))
            small_image1 = small_image1.resize((225, 225))

            # Определяем позиции, где будем размещать маленькие изображения
            if "Ppos_right" not in slovar:
                pdeck = [pdeck[1]]
                pdeck.append(deck.pop())
                slovar["Колода право"] = pdeck
                pright_score = scoring(pdeck)
                slovar["Pright"] = pright_score
                pos_player = (slovar["Ppos"][0], 700)  # Позиция для первого маленького изображения
                slovar["Ppos_right"] = pos_player
                # Накладываем маленькие изображения на большое
                lrg_img.paste(small_image1, pos_player)

                lrg_img.save(f"{config.RESULT_PATH}/{slovar['Айди']}.jpg")

                document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))
                await state.update_data(slovar)
                await bot.send_photo(chat_id=message.chat.id, photo=document,
                                     caption=f"Ваш счет (правая колода): {pright_score}\nСчет дилера: {comp_score}")
                if pright_score > 21:
                    await message.answer("Правая колода не сыграла! Попробуйте левую")
                    slovar["Split_choose"] = "left"
                    slovar["Split_cond"] += 1
                    if slovar["Split_cond"] == 2:
                        await message.answer(f"Не повезло(. Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        await message.answer(f"Выберите действие: ", reply_markup=gg2)
                else:
                    await message.answer(f"Выберите действие: ", reply_markup=gg2)
            else:
                pdeck = slovar["Колода право"]
                pdeck.append(deck.pop())
                slovar["Колода право"] = pdeck
                pright_score = scoring(pdeck)
                slovar["Pright"] = pright_score
                pos_player = (
                    slovar["Ppos"][0], slovar["Ppos_right"][1] - 100)  # Позиция для первого маленького изображения
                slovar["Ppos_right"] = pos_player
                # Накладываем маленькие изображения на большое
                lrg_img.paste(small_image1, pos_player)

                lrg_img.save(f"{config.RESULT_PATH}/result_image_{slovar['Айди']}.jpg")

                document = FSInputFile(os.path.join(config.RESULT_PATH, f"result_image_{slovar['Айди']}.jpg"))
                await state.update_data(slovar)
                await bot.send_photo(chat_id=message.chat.id, photo=document,
                                     caption=f"Ваш счет (правая колода): {pright_score}\nСчет дилера: {comp_score}")
                if pright_score > 21:
                    await message.answer("Правая колода не сыграла! Попробуйте левую")
                    slovar["Split_choose"] = "left"
                    slovar["Split_cond"] += 1
                    if slovar["Split_cond"] == 2:
                        await message.answer(f"Не повезло(. Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        await message.answer(f"Выберите действие: ", reply_markup=gg2)
                else:
                    await message.answer(f"Выберите действие: ", reply_markup=gg2)


@router.message(F.text == "Хватит")
async def hvatit(message: Message, state: FSMContext, bot: Bot):
    print("huyki")
    slovar = await state.get_data()
    print(slovar["Action"])

    pdeck = slovar["Колода игрока"]
    cdeck = slovar["Колода компа"]
    deck = slovar["Остаток колоды"]
    is_double = slovar["Статус"]
    bet = slovar["Ставка"]
    money = slovar["Деньги"]
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
        await state.update_data(slovar)
        await bot.send_photo(chat_id=message.chat.id, photo=document,
                             caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
        await asyncio.sleep(1)

        if (player_score < comp_score and comp_score <= 21) or player_score > 21:
            if not is_double:
                money -= bet
                await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
            else:
                money -= 2 * bet
                await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
        elif player_score == 21 and player_score != comp_score:
            if is_double == False:
                money += bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)

            else:
                money += 2 * bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)

        elif (player_score <= 21 and player_score > comp_score) or comp_score > 21:
            if is_double == False:
                money += bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
            else:
                money += 2 * bet
                await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                await asyncio.sleep(1)
                await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)


        elif player_score == comp_score:
            await message.answer(f"Ничья! Ваш баланс: {money}")
            await asyncio.sleep(1)
            await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
    else:
        if slovar["Split_choose"] == "left":
            slovar["Split_choose"] = "right"
            slovar["Split_stop"] += 1
            await state.update_data(slovar)
            if slovar["Split_stop"] == 2:
                comp_score = scoring(cdeck)
                while comp_score <= 17:
                    cdeck.append(deck.pop())
                    comp_score = scoring(cdeck)
                if (slovar["Pleft"] < comp_score and comp_score <= 21) or (
                        slovar["Pright"] < comp_score and comp_score <= 21):
                    if not (slovar["Pleft"] < comp_score and comp_score <= 21) and (
                            slovar["Pright"] < comp_score and comp_score <= 21):
                        money -= bet
                        await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        money -= 2 * bet
                        await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                elif (slovar["Pleft"] == 21 and slovar["Pleft"] != comp_score) or (
                        slovar["Pright"] == 21 and slovar["Pright"] != comp_score):
                    if not (slovar["Pleft"] == 21 and slovar["Pleft"] != comp_score) and (
                            slovar["Pright"] == 21 and slovar["Pright"] != comp_score):
                        money += bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)

                    else:
                        money += 2 * bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)

                elif (slovar["Pleft"] <= 21 and slovar["Pleft"] > comp_score) or (
                        slovar["Pright"] <= 21 and slovar["Pright"] > comp_score) or comp_score > 21:
                    if not (slovar["Pleft"] <= 21 and slovar["Pleft"] > comp_score) and (
                            slovar["Pright"] <= 21 and slovar["Pright"] > comp_score):
                        money += bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        money += 2 * bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)


                elif (slovar["Pleft"] == comp_score) or (slovar["Pright"] == comp_score):
                    await message.answer(f"Ничья! Ваш баланс: {money}")
                    await asyncio.sleep(1)
                    await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
            else:
                await message.answer(f"Выберите действие для правой колоды", reply_markup=gg1)

        elif slovar["Split_choose"] == "right":
            slovar["Split_choose"] = "left"
            slovar["Split_stop"] += 1
            await state.update_data(slovar)
            if slovar["Split_stop"] == 2:
                comp_score = scoring(cdeck)
                while comp_score <= 17:
                    cdeck.append(deck.pop())
                    comp_score = scoring(cdeck)
                if (slovar["Pleft"] < comp_score and comp_score <= 21) or (
                        slovar["Pright"] < comp_score and comp_score <= 21):
                    if not (slovar["Pleft"] < comp_score and comp_score <= 21) and (
                            slovar["Pright"] < comp_score and comp_score <= 21):
                        money -= bet
                        await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        money -= 2 * bet
                        await message.answer(f"Вы проиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                elif (slovar["Pleft"] == 21 and slovar["Pleft"] != comp_score) or (
                        slovar["Pright"] == 21 and slovar["Pright"] != comp_score):
                    if not (slovar["Pleft"] == 21 and slovar["Pleft"] != comp_score) and (
                            slovar["Pright"] == 21 and slovar["Pright"] != comp_score):
                        money += bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)

                    else:
                        money += 2 * bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)

                elif (slovar["Pleft"] <= 21 and slovar["Pleft"] > comp_score) or (
                        slovar["Pright"] <= 21 and slovar["Pright"] > comp_score) or comp_score > 21:
                    if not (slovar["Pleft"] <= 21 and slovar["Pleft"] > comp_score) and (
                            slovar["Pright"] <= 21 and slovar["Pright"] > comp_score):
                        money += bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
                    else:
                        money += 2 * bet
                        await message.answer(f"Вы выиграли! Ваш баланс: {money}")
                        await asyncio.sleep(1)
                        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)


                elif (slovar["Pleft"] == comp_score) or (slovar["Pright"] == comp_score):
                    await message.answer(f"Ничья! Ваш баланс: {money}")
                    await asyncio.sleep(1)
                    await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
            else:
                await message.answer(f"Выберите действие для левой колоды", reply_markup=gg1)


@router.message(F.text == "Удвоить ставку")
async def double(message: Message, state: FSMContext, bot: Bot):
    slovar = await state.get_data()
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
    await state.update_data(slovar)
    await bot.send_photo(chat_id=message.chat.id, photo=document,
                         caption=f"Ваш счет: {player_score}\nСчет дилера: {comp_score}")
    if player_score > 21:
        await message.answer("Вы проиграли!")
        time.sleep(1)
        await message.answer(f"Хотите сыграть еще раз?", reply_markup=final_kb)
    else:
        await message.answer("Выберите действие: ", reply_markup=gg1)


# @router.callback_query(F.data == 'lobby')
# async def exit(callback:CallbackQuery,state:FSMContext):
#     await state.clear()

# @router.callback_query(F.data == 'menu')
# async def exit(callback:CallbackQuery,state:FSMContext):
#     await state.clear()


@router.message(F.text == "Сплит")
async def split(message: Message, state: FSMContext):
    slovar = await state.get_data()
    slovar["Action"] = False
    await state.update_data(slovar)
    sl1 = slovar.copy()
    await state.clear()
    await state.update_data(sl1)
    await message.answer("Выберите колоду:", reply_markup=split_kb)


@router.callback_query(F.data == "left")
@router.callback_query(F.data == "right")
async def add(callback: CallbackQuery, state: FSMContext):
    slovar = await state.get_data()
    print("tuta zdesya")
    slovar["Split_choose"] = callback.data
    await state.update_data(slovar)

    await callback.message.answer(f"Выберите действие: ", reply_markup=gg1)
