import requests
from django.core.paginator import Paginator
from telebot import types
from telebot.apihelper import ApiException

from bot.brain import bot
from settings import BLOCKONOMICS_API_KEY
from bot.handlers.messages import check_admin
from bot.keyboards import inline, reply
from bot.models import Category, Product, User, Order, Payment, PaymentStatus
from bot.utils.states import States


def create_payment_address():
    url = 'https://www.blockonomics.co/api/new_address'
    headers = {'Authorization': "Bearer " + BLOCKONOMICS_API_KEY}
    r = requests.post(url, headers=headers)
    if r.status_code == 200:
        address = r.json()['address']
        return address
    else:
        return None


def gen_bread_crumb(category):
    result = ''
    if category.parent:
        last_category = category
        crumbs = [category.name]
        while True:
            try:
                parent = last_category.parent
                last_category = parent
                crumbs.append(parent.name)
            except AttributeError:
                break
        crumbs.reverse()
        for crumb in crumbs:
            result += f'{crumb} — '
        result = result[:-3]
    else:
        result = category.name
    return result


@bot.callback_query_handler(func=lambda c: c.data == 'to_shop', state='*')
def to_shop(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    text = '🛒 STORE'
    categories = Category.objects.filter(parent=None)
    try:
        bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.get_categories(categories, to_start=True))
    except Exception:
        bot.delete_message(user_id, msg_id)
        bot.send_message(user_id, text, reply_markup=inline.get_categories(categories, to_start=True))


@bot.callback_query_handler(func=lambda c: c.data.startswith('category_'), state='*')
def category_handler(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    category = Category.objects.get(id=call.data.split('_')[1])
    products = Product.objects.filter(category=category)
    childs = Category.objects.filter(parent=category)
    text = f'🛒 STORE\n\n{gen_bread_crumb(category)}'
    some_exists = True
    if products.exists() and childs.exists():
        markup = inline.get_products_categories(products, childs, prev_category=category.parent)
    elif products.exists():
        markup = inline.get_products(products, prev_category=category.parent)
    elif childs.exists():
        markup = inline.get_categories(childs, prev_category=category.parent)
    else:
        some_exists = False
        markup = inline.get_back_category(category.parent)
    if some_exists:
        try:
            bot.edit_message_text(text, user_id, msg_id, reply_markup=markup)
        except Exception:
            bot.delete_message(user_id, msg_id)
            bot.send_message(user_id, text, reply_markup=markup)
    else:
        text += '\n\n🚫 There is no products'
        try:
            bot.edit_message_text(text, user_id, msg_id, reply_markup=markup)
        except Exception:
            bot.delete_message(user_id, msg_id)
            bot.send_message(user_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'admin_' in c.data, state='*')
def admin____handler(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    if not User.objects.get(user_id=user_id).admin:
        bot.send_message(user_id, 'YOU ARE NOT AN ADMIN!!!', reply_markup=reply.main_menu())
    if call.data == 'admin_add_category':
        bot.set_state(States.new_category_name.value, user_id)
        bot.send_message(user_id, 'OK. Send me the name for new category.')
    if call.data == 'admin_add_product':
        bot.set_state(States.new_product_name.value, user_id)
        bot.send_message(user_id, 'OK. Send me the name for new product.')
    if call.data == 'admin_del_category':
        bot.send_message(user_id, 'OK. Now select the category for delete.', reply_markup=inline.del_category())
    if call.data == 'admin_del_product':
        bot.send_message(user_id, 'OK. Now select the product for delete.', reply_markup=inline.del_product())
    if call.data == 'admin_manage_admins':
        text = 'OK.  Now select the user to grant or remove administrator rights.\n\n'
        text += '❗ If user have ✅ - user is admin ❗'
        bot.send_message(user_id, text, reply_markup=inline.manage_admins(user_id))

    text = 'OK.  Now select the menu where you want to change the text'
    if call.data == 'admin_edit_text':
        text = 'OK.  Now select the menu where you want to change the text'
        bot.send_message(user_id, text, reply_markup=inline.edit_text())
    elif call.data == 'back_admin_edit_text':
        bot.finish_user(user_id)
        bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=inline.edit_text())

    if call.data == 'admin_manage_banned_users':
        text = 'OK.  Now select the user to ban or unban.\n\n'
        text += '❗ If user have 🖍 - user is banned ❗'
        bot.send_message(user_id, text, reply_markup=inline.manage_banned_users(user_id))
    if call.data == 'admin_manage_users_balance':
        text = 'OK. Now select the user to set value of balance.'
        bot.send_message(user_id, text, reply_markup=inline.manage_users_balance(user_id))


@bot.callback_query_handler(func=lambda c: 'manage_admins-' in c.data, state='*')
def manage_admins(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    user = User.objects.get(user_id=call_splited[1])
    text = 'OK.  Now select the user to grant or remove administrator rights.\n\n'
    text += '❗ If user have ✅ - user is admin ❗'
    if user.admin:
        user.admin = False
        user.save()
        bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.manage_admins(user_id))
    else:
        user.admin = True
        user.save()
        bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.manage_admins(user_id))


@bot.callback_query_handler(func=lambda c: 'select_parent-' in c.data, state='*')
def select_category_parent(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    
    if call_splited[2] != 'None':
        bot.update_data({'parent_category_id': int(call_splited[2])}, user_id)
    else:
        bot.update_data({'parent_category_id': None}, user_id)
    
    bot.edit_message_text('OK. Now send price ($) for this category.', user_id, msg_id)
    bot.set_state(States.new_category_price.value, user_id)


@bot.callback_query_handler(func=lambda c: 'addcategorywithout_doc' in c.data)
def addcategorywithout_doc(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    bot.update_data({'new_category_file': None}, user_id)
    bot.set_state(States.new_category_only_one_user.value, user_id)
    bot.edit_message_text('OK, now tell me. Can different users buy this product?', user_id, call.message.message_id,
                          reply_markup=inline.category_only_one_user())


@bot.callback_query_handler(func=lambda c: 'categoryfor' in c.data)
def new_category_only_one_user(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = bot.get_data(user_id)
    print("Collected data : ", data)

    if data['parent_category_id'] == None:
        parent_category = None
    else:
        parent_category = Category.objects.get(id=data['parent_category_id'])
    
    category_schema = {
        'name': data['new_category_name'],
        'parent': parent_category,
        'price': data['new_category_price'],
        'data': data['new_category_data'],
        'doc': data.get('new_category_file')
    }

    if call.data == 'categoryfor_different_users':
        category_schema['for_one_user'] = False
    elif call.data == 'categoryfor_one_user':
        category_schema['for_one_user'] = True
    
    Category.objects.create(**category_schema)
    bot.delete_message(user_id, call.message.message_id)
    bot.send_message(user_id, 'OK! Category successfully added.')
    bot.finish_user(user_id)


@bot.callback_query_handler(func=lambda c: 'select_product_category-' in c.data, state='*')
def select_product_category(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    category_to_chose = Category.objects.get(id=call_splited[1])

    bot.update_data({'new_product_category': category_to_chose.id}, user_id)
    # bot.edit_message_text('OK. Now send price ($) for this product.', user_id, msg_id)
    # bot.set_state(States.new_product_price.value, user_id)

    
    data = bot.get_data(user_id)
    # category = Category.objects.get(id=data['new_product_category'])
    product_schema = {
        'name': data['new_product_name'],
        'category': category_to_chose,
        # 'price': data['new_product_price'],
        # 'data': data['new_product_data'],
        # 'doc': data.get('new_product_file')
    }
    # if call.data == 'product_for_different_users':
    #     product_schema['for_one_user'] = False
    # elif call.data == 'product_for_one_user':
    #     product_schema['for_one_user'] = True
    Product.objects.create(**product_schema)
    bot.delete_message(user_id, call.message.message_id)
    bot.send_message(user_id, 'OK! Product successfully added.')
    bot.finish_user(user_id)


@bot.callback_query_handler(func=lambda c: 'del_category-' in c.data, state='*')
def del_category(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    category = Category.objects.get(id=call_splited[1])
    bot.edit_message_text(f'Are you sure want to delete {category.name}?', user_id, msg_id,
                          reply_markup=inline.sure_delete_category(category.id))


@bot.callback_query_handler(func=lambda c: 'delete_category-' in c.data, state='*')
def sure_delete_category(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    if call_splited[0] == 'yes_delete_category':
        category_to_delete = Category.objects.get(id=call_splited[1])
        category_to_delete.delete()
        bot.edit_message_text(f'Category "{category_to_delete.name}" has been deleted!', user_id, msg_id)
    if call_splited[0] == 'no_delete_category':
        if not check_admin(user_id):
            bot.edit_message_text(user_id, '❗ YOU ARE NOT AN ADMIN ❗', user_id, msg_id, reply_markup=reply.main_menu())
        else:
            bot.edit_message_text('👨‍💻 ADMIN MENU ⚙', user_id, msg_id, reply_markup=inline.admin_menu())


@bot.callback_query_handler(func=lambda c: 'del_product-' in c.data, state='*')
def del_product(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    product = Product.objects.get(id=call_splited[1])
    bot.edit_message_text(f'Are you sure want to delete {product.name}?', user_id, msg_id,
                          reply_markup=inline.sure_delete_product(product.id))


@bot.callback_query_handler(func=lambda c: 'delete_product-' in c.data, state='*')
def sure_delete_product(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    if call_splited[0] == 'yes_delete_product':
        product_to_delete = Product.objects.get(id=call_splited[1])
        product_to_delete.delete()
        bot.edit_message_text(f'Product "{product_to_delete.name}" has been deleted!', user_id, msg_id)
    if call_splited[0] == 'no_delete_product':
        if not check_admin(user_id):
            bot.edit_message_text(user_id, '❗ YOU ARE NOT AN ADMIN ❗', user_id, msg_id, reply_markup=reply.main_menu())
        else:
            bot.edit_message_text('👨‍💻 ADMIN MENU ⚙', user_id, msg_id, reply_markup=inline.admin_menu())


@bot.callback_query_handler(func=lambda c: 'buy_product-' in c.data, state='*')
def buy_product(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    product_to_buy = Product.objects.get(id=call_splited[1])
    user = User.objects.get(user_id=user_id)
    if user.balance < product_to_buy.category.price:
        text = '🛒 STORE\n\n🚫 You do not have enough money'
        bot.edit_message_text(text, user_id, msg_id,
                              reply_markup=inline.get_back_category(product_to_buy.category))
    elif len(Order.objects.filter(user=user, user__order__product=product_to_buy.id)) >= 1:
        bot.edit_message_text('🛒 STORE\n\n✅ Have you already purchased this product!', user_id, msg_id,
                              reply_markup=inline.get_back_category(product_to_buy.category))
    else:
        bot.edit_message_text('OK. Are you sure what want buy this product?', user_id, msg_id,
                              reply_markup=inline.sure_buy_product(product_to_buy.id, product_to_buy.category))


@bot.callback_query_handler(func=lambda c: 'yes_sure_product-' in c.data, state='*')
def sure_buy_product(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    product_to_buy = Product.objects.get(id=call_splited[1])
    user = User.objects.get(user_id=user_id)
    if call_splited[0] == 'yes_sure_product':
        new_purchase = Order.objects.create(user=user, product=product_to_buy)
        user.balance -= product_to_buy.category.price
        user.save()
        text = f'✅ You have successfully bought {product_to_buy.name}\n\n' \
               f'Product data:\n{product_to_buy.category.data}\n\nYou can view it again in the order history.'
        bot.delete_message(user_id, msg_id)
        if product_to_buy.category.doc:
            bot.send_message(user_id, text, reply_markup=inline.get_product_doc(product_to_buy.id))
        else:
            bot.send_message(user_id, text)


@bot.callback_query_handler(func=lambda c: 'pagination_orders-' in c.data, state='*')
def pagination_orders(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    page = call_splited[1]
    user = User.objects.get(user_id=user_id)
    user_orders = Order.objects.filter(user=user).order_by('id')
    paginator = Paginator(user_orders, 1)
    text = '💵 Here you can view your recent purchases:\n\n'
    page_orders = paginator.page(page)
    for order in page_orders:
        text += f'Product id: {order.product.id}\n'
        text += f'Product name: {order.product.name}\n'
        text += f'Product data:\n{order.product.category.data}\n\n'
        text += f'Page: {page} / {paginator.num_pages}'
    bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.pagination_orders(paginator, page))


@bot.callback_query_handler(func=lambda c: 'wallet_upload' in c.data, state='*')
def wallet_upload(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '📤')
    user_id = call.from_user.id
    text = '''
💵 WALLET

Your personal BTC address for loading the wallet is below. 
Your wallet balance will be updated after one bitcoin network confirmation (usually during an hour).
Use 1 address only for 1 transaction or money won't be credited.
'''
    user = User.objects.get(user_id=user_id)
    try:
        payment = Payment.objects.get(user=user, status=PaymentStatus.unconfirmed.value)
    except Payment.DoesNotExist:
        new_payment_address = create_payment_address()
        payment = Payment.objects.create(user=user, address=new_payment_address)
    bot.send_message(user_id, text)
    bot.send_message(user_id, payment.address)


@bot.callback_query_handler(func=lambda c: 'wallet_history' in c.data, state='*')
def wallet_history(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '⏳')
    user_id = call.from_user.id
    text = '⏳ Your recent transactions:\n\n'
    user = User.objects.get(user_id=user_id)
    user_payments = Payment.objects.filter(user=user, status=PaymentStatus.confirmed.value)
    if len(user_payments) < 1:
        text += '🚫 Your have no transactions yet'
    else:
        text += '--------------------------------------------------------\n'
        for payment in user_payments:
            status = 'Confirmed' if payment.status == PaymentStatus.confirmed.value else 'Unconfirmed'
            text += f'Payment id = {payment.id}\n'
            text += f'Payment address = {payment.address}\n'
            text += f'Payment value = {payment.value}\n'
            text += '--------------------------------------------------------\n'
    bot.send_message(user_id, text)


# @bot.callback_query_handler(func=lambda c: 'add_without_doc' in c.data)
# def add_without_doc(call: types.CallbackQuery):
#     bot.answer_callback_query(call.id)
#     user_id = call.from_user.id
#     bot.update_data({'new_product_file': None}, user_id)
#     bot.set_state(States.new_product_only_one_user.value, user_id)
#     bot.edit_message_text('OK, now tell me. Can different users buy this product?', user_id, call.message.message_id,
#                           reply_markup=inline.only_one_user())


# @bot.callback_query_handler(func=lambda c: 'product_for' in c.data)
# def new_product_only_one_user(call: types.CallbackQuery):
#     user_id = call.from_user.id
#     data = bot.get_data(user_id)
#     category = Category.objects.get(id=data['new_product_category'])
#     product_schema = {
#         'name': data['new_product_name'],
#         'category': category,
#         'price': data['new_product_price'],
#         'data': data['new_product_data'],
#         'doc': data.get('new_product_file')
#     }
#     if call.data == 'product_for_different_users':
#         product_schema['for_one_user'] = False
#     elif call.data == 'product_for_one_user':
#         product_schema['for_one_user'] = True
#     Product.objects.create(**product_schema)
#     bot.delete_message(user_id, call.message.message_id)
#     bot.send_message(user_id, 'OK! Product successfully added.')
#     bot.finish_user(user_id)


@bot.callback_query_handler(func=lambda c: 'get_document-' in c.data, state='*')
def get_document(call: types.CallbackQuery):
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    call_splited = call.data.split('-')
    product = Product.objects.get(id=call_splited[1])
    document = product.category.doc
    bot.send_document(user_id, document)


@bot.callback_query_handler(func=lambda c: 'edit_text_welcome_message' in c.data)
def edit_text_welcome_message(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '🤝')
    user_id = call.from_user.id
    msg_id = call.message.message_id
    bot.edit_message_text('OK. Now send new text for welcome message\n\n'
                          '(After restarting the bot will be reset to default)', user_id, msg_id,
                          reply_markup=inline.back_admin_edit_text())
    bot.set_state(States.edit_text_welcome_message.value, user_id)


@bot.callback_query_handler(func=lambda c: 'edit_text_shop_policy' in c.data)
def edit_text_shop_policy(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '⚠')
    user_id = call.from_user.id
    msg_id = call.message.message_id
    bot.edit_message_text('OK. Now send new text for shop policy\n\n'
                          '(After restarting the bot will be reset to default)', user_id, msg_id,
                          reply_markup=inline.back_admin_edit_text())
    bot.set_state(States.edit_text_shop_policy.value, user_id)




@bot.callback_query_handler(func=lambda c: 'navigateto_balance_users_page-' in c.data, state='*')
def navigateto_manage_users_page(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '🖍')
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    page_number = 1 # Start viewing items from page 1
    try:
        page_number_str = call_splited[1]
        page_number = int(page_number_str)
    except Exception as e:
        print("Cannot extract page number from {}. Error is {}".format(page_number_str, str(e)))

    print("navigateto_manage_users_page > Page number is {}".format(page_number))
    
    text = 'OK. Now select the user to set value of balance.\n\n'
    try:
        bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.manage_users_balance(user_id, page_number))
    except ApiException:
        pass


@bot.callback_query_handler(func=lambda c: 'navigateto_banned_users_page-' in c.data, state='*')
def navigateto_banned_users_page(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '🖍')
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    page_number = 1
    try:
        page_number_str = call_splited[1]
        page_number = int(page_number_str)
    except Exception as e:
        print("Cannot extract page number from {}. Error is {}".format(page_number_str, str(e)))

    print("navigateto_banned_users_page > Page number is {}".format(page_number))
    # user = User.objects.get(user_id=call_splited[1])
    # if user.ban_status:
    #     user.ban_status = False
    # else:
    #     user.ban_status = True
    # user.save()
    text = 'OK.  Now select the user to ban or unban.\n\n'
    text += '❗ If user have 🖍 - user is banned ❗'
    try:
        bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.manage_banned_users(user_id, page_number))
    except ApiException:
        pass



@bot.callback_query_handler(func=lambda c: 'navigateto_adminusers_page-' in c.data, state='*')
def mrmnext(call: types.CallbackQuery):
    print("navigateto_adminusers_page")
    bot.answer_callback_query(call.id, '🖍')
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    page_number = 1 # Start viewing items from page 1
    try:
        page_number_str = call_splited[1]
        page_number = int(page_number_str)
    except Exception as e:
        print("Cannot extract page number from {}. Error is {}".format(page_number_str, str(e)))

    print("navigateto_adminusers_page > Page number is {}".format(page_number))
    
    text = 'OK. Now select the user to set value of balance.\n\n'
    try:
        bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.manage_admins(user_id, page_number))
    except ApiException:
        pass



@bot.callback_query_handler(func=lambda c: 'manage_banned_users-' in c.data, state='*')
def manage_banned_users(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '🖍')
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    user = User.objects.get(user_id=call_splited[1])
    if user.ban_status:
        user.ban_status = False
    else:
        user.ban_status = True
    user.save()
    text = 'OK.  Now select the user to ban or unban.\n\n'
    text += '❗ If user have 🖍 - user is banned ❗'
    try:
        bot.edit_message_text(text, user_id, msg_id, reply_markup=inline.manage_banned_users(user_id))
    except ApiException:
        pass


@bot.callback_query_handler(func=lambda c: 'manage_users_balance-' in c.data, state='*')
def manage_users_balance(call: types.CallbackQuery):
    bot.answer_callback_query(call.id, '💵')
    user_id = call.from_user.id
    msg_id = call.message.message_id
    call_splited = call.data.split('-')
    user = User.objects.get(user_id=call_splited[1])
    bot.set_data({'user_to_set_balance': user.user_id}, user_id)
    bot.set_state(States.manage_users_balance.value, user_id)
    bot.edit_message_text(f'Send value to set new balance to {user.full_name}', user_id, msg_id)
