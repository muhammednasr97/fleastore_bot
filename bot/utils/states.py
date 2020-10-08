from enum import Enum


class States(Enum):
    new_category_name = '1'
    new_category_parent = '2'
    new_category_price = '8'
    new_category_data = '9'
    new_category_file = '10'
    new_category_only_one_user = '11'
    new_product_name = '3'
    # new_product_price = '4'
    # new_product_data = '5'
    # new_product_file = '6'
    # new_product_only_one_user = '7'

    edit_text_welcome_message = '1_1'
    edit_text_shop_policy = '1_2'

    manage_users_balance = '2_2'
