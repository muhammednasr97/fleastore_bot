from telebot.types import ReplyKeyboardMarkup
from telebot.types import ReplyKeyboardRemove


def remove():
    return ReplyKeyboardRemove()


def back():
    markup = ReplyKeyboardMarkup(True)
    return markup.row('↩ BACK')


def main_menu(admin=False):
    markup = ReplyKeyboardMarkup(True)
    markup.row('🛒 STORE', '💵 WALLET')
    markup.row('🗓 ORDER HISTORY', '⚠ SHOP POLICY')
    if admin:
        markup.row('👨‍💻 ADMIN MENU ⚙')
    return markup
