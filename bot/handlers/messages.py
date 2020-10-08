import json
from decimal import Decimal, InvalidOperation

import requests
from django.core.paginator import Paginator
from telebot import types

from bot.brain import bot
from bot.keyboards import inline, reply
from bot.models import Category, User, Product, Order
from bot.strings import strings
from bot.utils.states import States


def check_admin(user_id) -> bool:
    return User.objects.get(user_id=user_id).admin


@bot.message_handler(func=lambda msg: msg.text == '🛒 STORE', state='*')
def store(msg: types.Message):
    user_id = msg.from_user.id
    text = '🛒 STORE\n\n'
    categories = Category.objects.filter(parent=None)
    if len(categories) < 1:
        text += '\n🚫 There is no categories'
        bot.send_message(user_id, text)
    else:
        bot.send_message(user_id, text, reply_markup=inline.get_categories(categories, to_start=True))


@bot.message_handler(func=lambda msg: msg.text == '💵 WALLET', state='*')
def wallet(msg: types.Message):
    user_id = msg.from_user.id
    user = User.objects.get(user_id=user_id)
    url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD'
    r = requests.get(url)
    result = json.loads(r.text)
    text = f'''
💵 WALLET

🌞 Actual BTC rates: 1 BTC = {result["USD"]} USD

Your balance: {user.balance} USD
'''
    bot.send_message(user_id, text, reply_markup=inline.wallet())


@bot.message_handler(func=lambda msg: msg.text == '🗓 ORDER HISTORY', state='*')
def order_history(msg: types.Message):
    user_id = msg.from_user.id
    user = User.objects.get(user_id=user_id)
    user_orders = Order.objects.filter(user=user).order_by('id')
    paginator = Paginator(user_orders, 1)
    text = '💵 Here you can view your recent purchases:\n\n'
    if len(user_orders) < 1:
        text += '🚫 Your have no purchases yet'
        bot.send_message(user_id, text)
    else:
        page_orders = paginator.page(1)
        for order in page_orders:
            text += f'Product id: {order.product.id}\n'
            text += f'Product name: {order.product.name}\n'
            text += f'Product data:\n{order.product.category.data}\n\n'
            text += f'Page: 1 / {paginator.num_pages}'
        bot.send_message(user_id, text, reply_markup=inline.pagination_orders(paginator, 1))


@bot.message_handler(func=lambda msg: msg.text == '⚠ SHOP POLICY', state='*')
def shop_policy(msg: types.Message):
    user_id = msg.from_user.id
    bot.send_message(user_id, strings['shop_policy'])


@bot.message_handler(func=lambda msg: msg.text == '👨‍💻 ADMIN MENU ⚙', state='*')
def admin_menu(msg: types.Message):
    user_id = msg.from_user.id
    if not check_admin(user_id):
        bot.send_message(user_id, '❗ YOU ARE NOT AN ADMIN ❗', reply_markup=reply.main_menu())
    else:
        bot.send_message(user_id, msg.text, reply_markup=inline.admin_menu())


@bot.message_handler(state=States.new_category_name.value)
def new_category_name(msg: types.Message):
    user_id = msg.from_user.id
    bot.reset_state(user_id)
    bot.set_data({'new_category_name': msg.text}, user_id)
    print("Bot data", bot.get_data(user_id))
    bot.send_message(user_id, 'OK. Now select the parent for this category',
                     reply_markup=inline.select_parent(None))


@bot.message_handler(state=States.new_category_price.value)
def new_category_price(msg: types.Message):
    user_id = msg.from_user.id
    try:
        price = Decimal(msg.text)
        bot.update_data({'new_category_price': str(price)}, user_id)
        bot.send_message(user_id, 'OK. Now send the data that the bot will give to the user after the purchase.')
        bot.set_state(States.new_category_data.value, user_id)
    except InvalidOperation:
        bot.send_message(user_id, 'It\'s not like the price. Try again.')


@bot.message_handler(state=States.new_category_data.value)
def new_category_data(msg: types.Message):
    user_id = msg.from_user.id
    bot.update_data({'new_category_data': msg.text}, user_id)
    bot.set_state(States.new_category_file.value, user_id)
    bot.send_message(user_id, 'OK. Now send the DOCUMENT that the bot will give to the user after the purchase.',
                     reply_markup=inline.add_doc_to_category())


@bot.message_handler(state=States.new_category_file.value, content_types=['text', 'document'])
def new_category_file(msg: types.Message):
    user_id = msg.from_user.id
    content_type = msg.content_type
    if content_type == 'text':
        bot.send_message(user_id, 'It\'s not like the document. Try again.')
    if content_type == 'document':
        file_id = msg.document.file_id
        bot.update_data({'new_category_file': file_id}, user_id)
        bot.set_state(States.new_category_only_one_user.value, user_id)
        bot.send_message(user_id, 'OK, now tell me. Can different users buy the products in the category??',
                         reply_markup=inline.category_only_one_user())


@bot.message_handler(state=States.new_product_name.value)
def new_product_name(msg: types.Message):
    user_id = msg.from_user.id
    bot.reset_state(user_id)
    bot.set_data({'new_product_name': msg.text}, user_id)
    bot.send_message(user_id, 'OK. Now select the category for this product',
                     reply_markup=inline.select_product_category())


# @bot.message_handler(state=States.new_product_price.value)
# def new_product_price(msg: types.Message):
#     user_id = msg.from_user.id
#     try:
#         price = Decimal(msg.text)
#         bot.update_data({'new_product_price': str(price)}, user_id)
#         bot.send_message(user_id, 'OK. Now send the data that the bot will give to the user after the purchase.')
#         bot.set_state(States.new_product_data.value, user_id)
#     except InvalidOperation:
#         bot.send_message(user_id, 'It\'s not like the price. Try again.')


# @bot.message_handler(state=States.new_product_data.value)
# def new_product_data(msg: types.Message):
#     user_id = msg.from_user.id
#     bot.update_data({'new_product_data': msg.text}, user_id)
#     bot.set_state(States.new_product_file.value, user_id)
#     bot.send_message(user_id, 'OK. Now send the DOCUMENT that the bot will give to the user after the purchase.',
#                      reply_markup=inline.add_doc_to_product())


# @bot.message_handler(state=States.new_product_file.value, content_types=['text', 'document'])
# def new_product_file(msg: types.Message):
#     user_id = msg.from_user.id
#     content_type = msg.content_type
#     if content_type == 'text':
#         bot.send_message(user_id, 'It\'s not like the document. Try again.')
#     if content_type == 'document':
#         file_id = msg.document.file_id
#         bot.update_data({'new_product_file': file_id}, user_id)
#         bot.set_state(States.new_product_only_one_user.value, user_id)
#         bot.send_message(user_id, 'OK, now tell me. Can different users buy this product??',
#                          reply_markup=inline.only_one_user())


@bot.message_handler(state=States.edit_text_welcome_message.value)
def edit_text_welcome_message(msg: types.Message):
    user_id = msg.from_user.id
    strings['welcome_message'] = msg.text
    bot.send_message(user_id, 'OK. Welcome message has been changed.\nUse /start for check changes')


@bot.message_handler(state=States.edit_text_shop_policy.value)
def edit_text_welcome_message(msg: types.Message):
    user_id = msg.from_user.id
    strings['shop_policy'] = msg.text
    bot.send_message(user_id, 'OK. Shop policy has been changed.')


@bot.message_handler(state=States.manage_users_balance.value)
def manage_users_balance(msg: types.Message):
    user_id = msg.from_user.id
    state_data = bot.get_data(user_id)
    user_id_to_set_balance = state_data.get('user_to_set_balance')
    try:
        value = Decimal(msg.text)
        user_to_set_balance = User.objects.get(user_id=user_id_to_set_balance)
        user_to_set_balance.balance = value
        user_to_set_balance.save()
        bot.send_message(user_id, f'New balance for {user_to_set_balance.full_name} is {user_to_set_balance.balance}')
        bot.finish_user(user_id)
    except InvalidOperation:
        bot.send_message(user_id, 'It\'s not like the value for balance. Try again.')
