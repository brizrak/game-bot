from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


button1 = InlineKeyboardButton(text="Сыграть карту", callback_data="foolplaycard")
button2 = InlineKeyboardButton(text="Пас", callback_data="foolpass")
button3 = InlineKeyboardButton(text="Взять", callback_data="fooltake")
button4 = InlineKeyboardButton(text="Бито", callback_data="foolbeaten")

# Создаем разметку клавиатуры
playonly = InlineKeyboardMarkup(inline_keyboard=[[button1]], resize_keyboard=True)
playpass = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]], resize_keyboard=True)
playtake = InlineKeyboardMarkup(inline_keyboard=[[button1, button3]], resize_keyboard=True)
playbeaten = InlineKeyboardMarkup(inline_keyboard=[[button1, button4]], resize_keyboard=True)

yes = InlineKeyboardButton(text="Да", callback_data="yes")
lobby = InlineKeyboardButton(text="Выйти в лобби", callback_data="lobby")
menu = InlineKeyboardButton(text="Главное меню", callback_data="menu")
start = InlineKeyboardButton(text="Начать", callback_data="fool_start")
final_kb = InlineKeyboardMarkup(inline_keyboard=[[yes, lobby, menu]], resize_keyboard=True)
weirdfinal_kb = InlineKeyboardMarkup(inline_keyboard=[[menu]], resize_keyboard=True)
startupplayonly = InlineKeyboardMarkup(inline_keyboard=[[start]], resize_keyboard=True)
