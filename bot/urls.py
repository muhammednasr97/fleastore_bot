from django.urls import path

from bot.views import UpdateBot, index
from bot.views import Payments

urlpatterns = [
    path('', index),
    path('bot_webhook/', UpdateBot.as_view(), name='update'),
    path('payments/', Payments.as_view(), name='payment'),
]