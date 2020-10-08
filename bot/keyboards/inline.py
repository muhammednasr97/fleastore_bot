from django.core.paginator import Paginator, EmptyPage
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

from bot.models import Category, Product, User, Payment, Order

import math

to_shop_btn = InlineKeyboardButton('↩ BACK', callback_data='to_shop')
to_start_btn = InlineKeyboardButton('↩ BACK', callback_data='to_start')


def back_admin_edit_text():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('↩ BACK', callback_data='back_admin_edit_text'))
    return markup


def get_back_category(prev_category):
    markup = InlineKeyboardMarkup()
    if prev_category:
        markup.add(InlineKeyboardButton('↩ BACK', callback_data=f'category_{prev_category.id}'))
    else:
        markup.add(to_shop_btn)
    return markup


def get_categories(categories, prev_category=None, to_start=False):
    markup = InlineKeyboardMarkup()
    for category in categories:
        markup.add(InlineKeyboardButton(category.name, callback_data=f'category_{category.id}'))
    if prev_category:
        markup.add(InlineKeyboardButton('↩ BACK', callback_data=f'category_{prev_category.id}'))
    elif to_start:
        markup.add(to_start_btn)
    else:
        markup.add(to_shop_btn)
    return markup


def get_products(products, prev_category=None, to_start=False):
    markup = InlineKeyboardMarkup()
    for product in products:
        orders = Order.objects.filter(product=product)
        if not (orders.exists() and product.category.for_one_user):
            markup.add(InlineKeyboardButton(f'{product.name} - ${product.category.price}', callback_data=f'buy_product-{product.id}'))
    if prev_category:
        markup.add(InlineKeyboardButton('↩ BACK', callback_data=f'category_{prev_category.id}'))
    elif to_start:
        markup.add(to_start_btn)
    else:
        markup.add(to_shop_btn)
    return markup


def get_products_categories(products, categories, prev_category=None, to_start=False):
    markup = InlineKeyboardMarkup()
    for category in categories:
        markup.add(InlineKeyboardButton(category.name, callback_data=f'category_{category.id}'))
    for product in products:
        orders = Order.objects.filter(product=product)
        if not (orders.exists() and product.category.for_one_user):
            markup.add(InlineKeyboardButton(f'{product.name} - ${product.category.price}', callback_data=f'buy_product-{product.id}'))
    if prev_category:
        markup.add(InlineKeyboardButton('↩ BACK', callback_data=f'category_{prev_category.id}'))
    elif to_start:
        markup.add(to_start_btn)
    else:
        markup.add(to_shop_btn)
    return markup


def admin_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('✏ Add category', callback_data='admin_add_category'))
    markup.add(InlineKeyboardButton('📦 Add product', callback_data='admin_add_product'))
    markup.add(InlineKeyboardButton('❌ Delete category', callback_data='admin_del_category'))
    markup.add(InlineKeyboardButton('❌ Delete product', callback_data='admin_del_product'))
    markup.add(InlineKeyboardButton('📝 Edit text messages', callback_data='admin_edit_text'))
    markup.add(InlineKeyboardButton('💵 Manage users balance', callback_data='admin_manage_users_balance'))
    markup.add(InlineKeyboardButton('🖍 Manage banned users', callback_data='admin_manage_banned_users'))
    markup.add(InlineKeyboardButton('👨‍💻 Manage admins', callback_data='admin_manage_admins'))
    markup.add(to_start_btn)
    return markup


def select_parent(category_id: int):
    markup = InlineKeyboardMarkup()
    for category in Category.objects.all():
        if category_id == None:
            markup.add(InlineKeyboardButton(category.name, callback_data=f'select_parent-None-{category.id}'))
        elif category.id != category_id:
            markup.add(InlineKeyboardButton(category.name, callback_data=f'select_parent-{category_id}-{category.id}'))
    markup.add(InlineKeyboardButton('None', callback_data=f'select_parent-{category_id}-None'))
    return markup


def select_product_category():
    markup = InlineKeyboardMarkup()
    for category in Category.objects.filter():
        markup.add(InlineKeyboardButton(category.name,
                                        callback_data=f'select_product_category-{category.id}'))
    return markup



def del_category():
    markup = InlineKeyboardMarkup()
    for category in Category.objects.filter():
        markup.add(InlineKeyboardButton(category.name,
                                        callback_data=f'del_category-{category.id}'))
    return markup


def sure_delete_category(category_id):
    markup = InlineKeyboardMarkup()
    yes_btn = InlineKeyboardButton('Yes!', callback_data=f'yes_delete_category-{category_id}')
    no_btn = InlineKeyboardButton('No!', callback_data=f'no_delete_category-{category_id}')
    markup.row(yes_btn, no_btn)
    return markup


def add_doc_to_category():
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('Add without document', callback_data='addcategorywithout_doc')
    markup.row(btn)
    return markup


def get_category_doc(category_id):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('Get document', callback_data=f'get_category_document-{category_id}')
    markup.row(btn)
    return markup


def category_only_one_user():
    markup = InlineKeyboardMarkup()
    btn_different = InlineKeyboardButton('Yes.', callback_data=f'categoryfor_different_users')
    btn_only_one = InlineKeyboardButton('No. Only one user', callback_data=f'categoryfor_one_user')
    markup.add(btn_only_one)
    markup.add(btn_different)
    return markup


def del_product():
    markup = InlineKeyboardMarkup()
    for product in Product.objects.filter():
        orders = Order.objects.filter(product=product)
        if not (orders.exists() and product.category.for_one_user):
            markup.add(InlineKeyboardButton(product.name,
                                            callback_data=f'del_product-{product.id}'))
    return markup


def sure_delete_product(product_id):
    markup = InlineKeyboardMarkup()
    yes_btn = InlineKeyboardButton('Yes!', callback_data=f'yes_delete_product-{product_id}')
    no_btn = InlineKeyboardButton('No!', callback_data=f'no_delete_product-{product_id}')
    markup.row(yes_btn, no_btn)
    return markup


def sure_buy_product(product_id, prev_category):
    markup = InlineKeyboardMarkup()
    yes_btn = InlineKeyboardButton('Yes!', callback_data=f'yes_sure_product-{product_id}')
    no_btn = InlineKeyboardButton('No!', callback_data=f'category_{prev_category.id}')
    markup.row(yes_btn, no_btn)
    return markup


def manage_admins(admin_id, page = 1):
    markup = InlineKeyboardMarkup()
    users = User.objects.all().order_by('id')
    
    pagesize = 90
    offset = (page - 1) * pagesize + 1
    page_lbound = offset
    page_ubound = offset + pagesize
    prev_page = max(1, (page-1))
    next_page = page + 1
    total_num_page = math.ceil(len(users)/pagesize)

    print("Users length = {}, Page = {}. Lower bound = {}, Upper bound = {}".format(len(users), page, page_lbound, page_ubound))
    print("Prev page = {}, Next page = {}, Total #pages = {}".format(prev_page, next_page, total_num_page))

    if users.count()-1 < 1:
        btn = InlineKeyboardButton('Nothing was found but you', callback_data='none')
        markup.row(btn)
    elif users.count()-1 == 1:
        for user in users[page_lbound: page_ubound+1]:
            if user.user_id != admin_id:
                if user.admin:
                    text = f'✅ {user.full_name}'
                else:
                    text = f'{user.full_name}'
                btn = InlineKeyboardButton(text, callback_data=f'manage_admins-{user.user_id}')
                markup.row(btn)
        if page > 1 : # No prev page if we are in page 1
            markup.row(InlineKeyboardButton("⏮️ Previous page", callback_data=f'navigateto_adminusers_page-{prev_page}'))
        if next_page <= total_num_page: # No next button if we are in the last page
            markup.row(InlineKeyboardButton("Next page ⏭️", callback_data=f'navigateto_adminusers_page-{next_page}'))
    else:
        for user in users[page_lbound: page_ubound+1]:
            if user.user_id != admin_id:
                if user.admin:
                    text = f'✅ {user.full_name}'
                else:
                    text = f'{user.full_name}'
                btn = InlineKeyboardButton(text, callback_data=f'manage_admins-{user.user_id}')
                markup.row(btn)
        if page > 1 : # No prev page if we are in page 1
            markup.row(InlineKeyboardButton("⏮️ Previous page", callback_data=f'navigateto_adminusers_page-{prev_page}'))
        if next_page <= total_num_page: # No next button if we are in the last page
            markup.row(InlineKeyboardButton("Next page ⏭️", callback_data=f'navigateto_adminusers_page-{next_page}'))
    return markup


def pagination_orders(paginator: Paginator, page):
    markup = InlineKeyboardMarkup()
    page = paginator.page(page)
    text_prev_page = '⬅'
    text_next_page = '➡'
    if paginator.num_pages <= 1:
        text_next_page = text_prev_page = '⏺'
        prev_page = paginator.num_pages
        next_page = paginator.num_pages
    else:
        try:
            next_page = page.next_page_number()
        except EmptyPage:
            next_page = 1
            text_next_page = '↩'
        try:
            prev_page = page.previous_page_number()
        except EmptyPage:
            prev_page = paginator.num_pages
            text_prev_page = '↪'
    prev_btn = InlineKeyboardButton(text_prev_page, callback_data=f'pagination_orders-{prev_page}')
    next_btn = InlineKeyboardButton(text_next_page, callback_data=f'pagination_orders-{next_page}')
    markup.row(prev_btn, next_btn)
    order = page[0]
    if order.product.category.doc:
        show_doc = InlineKeyboardButton('Get document', callback_data=f'get_document-{order.product.id}')
        markup.row(show_doc)
    return markup


def wallet():
    markup = InlineKeyboardMarkup()
    load_btn = InlineKeyboardButton('📤 LOAD', callback_data='wallet_upload')
    history_btn = InlineKeyboardButton('⏳ HISTORY', callback_data='wallet_history')
    markup.row(load_btn, history_btn)
    return markup


def add_doc_to_product():
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('Add without document', callback_data='add_without_doc')
    markup.row(btn)
    return markup


def get_product_doc(product_id):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton('Get document', callback_data=f'get_document-{product_id}')
    markup.row(btn)
    return markup


def edit_text():
    markup = InlineKeyboardMarkup()
    btn_welcome_message = InlineKeyboardButton('🤝 Welcome message', callback_data=f'edit_text_welcome_message')
    btn_shop_policy = InlineKeyboardButton('⚠ Shop policy', callback_data=f'edit_text_shop_policy')
    markup.add(btn_welcome_message)
    markup.add(btn_shop_policy)
    return markup


def manage_banned_users(admin_id, page = 1):
    
    markup = InlineKeyboardMarkup()
    users = User.objects.all().order_by('id')
    pagesize = 90
    offset = (page - 1) * pagesize + 1
    page_lbound = offset
    page_ubound = offset + pagesize
    prev_page = max(1, (page-1))
    next_page = page + 1
    total_num_page = math.ceil(len(users)/pagesize)

    print("Users length = {}, Page = {}. Lower bound = {}, Upper bound = {}".format(len(users), page, page_lbound, page_ubound))
    print("Prev page = {}, Next page = {}, Total #pages = {}".format(prev_page, next_page, total_num_page))

    if users.count()-1 < 1:
        btn = InlineKeyboardButton('Nothing was found but you', callback_data='none')
        markup.row(btn)
    elif users.count()-1 == 1:
        for user in users[page_lbound: page_ubound+1]:
            if user.user_id != admin_id:
                if user.ban_status:
                    text = f'🖍 {user.full_name}'
                else:
                    text = f'{user.full_name}'
                btn = InlineKeyboardButton(text, callback_data=f'manage_banned_users-{user.user_id}')
                markup.row(btn)
        if page > 1 : # No prev page if we are in page 1
            markup.row(InlineKeyboardButton("⏮️ Previous page", callback_data=f'navigateto_banned_users_page-{prev_page}'))
        if next_page <= total_num_page: # No next button if we are in the last page
            markup.row(InlineKeyboardButton("Next page ⏭️", callback_data=f'navigateto_banned_users_page-{next_page}'))
    else:
        for user in users[page_lbound: page_ubound+1]:
            if user.user_id != admin_id:
                if user.ban_status:
                    text = f'🖍 {user.full_name}'
                else:
                    text = f'{user.full_name}'
                btn = InlineKeyboardButton(text, callback_data=f'manage_banned_users-{user.user_id}')
                markup.row(btn)
        if page > 1 : # No prev page if we are in page 1
            markup.row(InlineKeyboardButton("⏮️ Previous page", callback_data=f'navigateto_banned_users_page-{prev_page}'))
        if next_page <= total_num_page: # No next button if we are in the last page
            markup.row(InlineKeyboardButton("Next page ⏭️", callback_data=f'navigateto_banned_users_page-{next_page}'))
    return markup


def only_one_user():
    markup = InlineKeyboardMarkup()
    btn_different = InlineKeyboardButton('Yes.', callback_data=f'product_for_different_users')
    btn_only_one = InlineKeyboardButton('No. Only one user', callback_data=f'product_for_one_user')
    markup.add(btn_only_one)
    markup.add(btn_different)
    return markup


def manage_users_balance(user_id, page = 1):
    # Manage the users balance
    users = User.objects.all().order_by('id')

    pagesize = 90
    offset = (page - 1) * pagesize + 1
    page_lbound = offset
    page_ubound = offset + pagesize
    prev_page = max(1, (page-1))
    next_page = page + 1
    total_num_page = math.ceil(len(users)/pagesize)

    print("Users length = {}, Page = {}. Lower bound = {}, Upper bound = {}".format(len(users), page, page_lbound, page_ubound))
    print("Prev page = {}, Next page = {}, Total #pages = {}".format(prev_page, next_page, total_num_page))


    markup = InlineKeyboardMarkup()
    for user in users[page_lbound: page_ubound+1]:
        btn_text = f'{user.full_name} (${user.balance})'
        markup.add(InlineKeyboardButton(btn_text, callback_data=f'manage_users_balance-{user.user_id}'))
    
    # Add the navigation buttons
    if page > 1 : # No prev page if we are in page 1
        markup.row(InlineKeyboardButton("⏮️ Previous page", callback_data=f'navigateto_balance_users_page-{prev_page}'))
    if next_page <= total_num_page: # No next button if we are in the last page
        markup.row(InlineKeyboardButton("Next page ⏭️", callback_data=f'navigateto_balance_users_page-{next_page}'))
    return markup
