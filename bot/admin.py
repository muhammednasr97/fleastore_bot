from django.contrib import admin

from bot.models import User, Product, Category, Order, Payment

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Payment)
