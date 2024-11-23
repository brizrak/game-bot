from aiogram.types import InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



def bet_kb(slovar: list):
    rkb = InlineKeyboardBuilder()
    for el in slovar:
        rkb.button(text= f"{el[0]}/{el[1]}", callback_data=f"{el[0]}/{el[1]}")
    return rkb.adjust(2).as_markup()

def make_bet_kb(spis:list):
    rkb = InlineKeyboardBuilder()
    for el in spis:
        rkb.button(text=f"{el} денег", callback_data=f"{el}")
    return rkb.adjust(2).as_markup()


button1 = KeyboardButton(text="Взять карту")
button2 = KeyboardButton(text="Хватит")
button3 = KeyboardButton(text="Удвоить ставку")
button4 = KeyboardButton(text="Сплит")

# Создаем разметку клавиатуры
gg = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3, button4]], resize_keyboard=True)
gg1 = ReplyKeyboardMarkup(keyboard=[[button1, button2]],resize_keyboard=True)
gg2 = ReplyKeyboardMarkup(keyboard=[[button1, button2, button3]],resize_keyboard=True)

yes = InlineKeyboardButton(text = "Да",callback_data="yes")
lobby = InlineKeyboardButton(text = "Выйти в лобби",callback_data="lobby")
menu = InlineKeyboardButton(text = "Главное меню",callback_data="menu")
final_kb = InlineKeyboardMarkup(inline_keyboard=[[yes,lobby,menu]],resize_keyboard = True)

left= InlineKeyboardButton(text = "Левая колода",callback_data="left")
right = InlineKeyboardButton(text = "Правая колода",callback_data="right")
split_kb = InlineKeyboardMarkup(inline_keyboard=[[left,right]],resize_keyboard = True)
