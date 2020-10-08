from settings import FREEZE
from bot.keyboards import reply
from bot.models import User
from bot.strings import strings

from telebot import types

from bot.brain import bot


def user_banned(msg: types.Message) -> bool:
    if User.objects.filter(user_id=msg.from_user.id).exists():
        if User.objects.get(user_id=msg.from_user.id).ban_status:
            return True
    return False


@bot.message_handler(func=lambda msg: user_banned(msg), state='*')
def banned_users_handler(message: types.Message):
    pass


@bot.message_handler(func=lambda msg: FREEZE, state='*')
def freeze_state_handler(message: types.Message):
    bot.send_message(message.from_user.id, 'BOT maintainence in progress shall be back soon!')


@bot.callback_query_handler(func=lambda c: c.data == 'to_start', state='*')
@bot.message_handler(func=lambda msg: msg.text == '↩ BACK', state='*')
@bot.message_handler(commands=['start', 'help'], state='*')
def start_cmd_handler(message: types.Message):
    user_id = message.from_user.id
    user = User.objects.filter(user_id=user_id)
    admin = False
    if not user.exists():
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        full_name = f'{first_name}'
        if last_name:
            full_name += f' {last_name}'
        new_user = User.objects.create(user_id=user_id, full_name=full_name, username=username)
    elif User.objects.get(user_id=user_id).admin:
        admin = True
    print(user_id)
    bot.send_message(message.from_user.id, strings.get('welcome_message'), reply_markup=reply.main_menu(admin))
    bot.finish_user(user_id)
