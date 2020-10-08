import json
from decimal import Decimal

import requests
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from telebot import types

from bot import handlers
from bot.brain import bot
from bot.models import PaymentStatus, Payment, User
from settings import WEBHOOK_URL, BLOCKONOMICS_SECRET


def satoshi_to_fiat(coin_value, satoshis):
    fiat_value = float(satoshis * float(10 ** -8) * float(coin_value))
    return '{:.2f}'.format(fiat_value)


def convert_satoshi_to_usd(satoshis):
    url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD'
    r = requests.get(url)
    result = json.loads(r.text)
    return satoshi_to_fiat(result["USD"], float(satoshis))


def index(request):
    return HttpResponse('')


class UpdateBot(APIView):
    def post(self, request):
        # Сюда должны получать сообщения от телеграм и далее обрабатываться ботом
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])

        return Response({'code': 200})


class Payments(APIView):
    def get(self, request):
        secret = request.GET.get('secret')
        txid = request.GET.get('txid')
        value = request.GET.get('value')
        status = request.GET.get('status')
        address = request.GET.get('addr')
        if secret != BLOCKONOMICS_SECRET:
            return Response({'code': 500})
        elif status != PaymentStatus.confirmed.value:
            return Response({'code': 500})
        elif status == PaymentStatus.confirmed.value:
            payment = Payment.objects.get(address=address)
            payment.txid = txid
            payment.value = value
            payment.status = PaymentStatus.confirmed.value

            usd_to_increase = convert_satoshi_to_usd(value)
            user = User.objects.get(user_id=payment.user.user_id)
            user.balance += Decimal(usd_to_increase)
            user.save()
            payment.save()
            bot.send_message(user.user_id, f'✅ Your balance has been increased on {usd_to_increase} USD')
        return Response({'code': 200})


handlers.init()
webhookurl = f'https://{WEBHOOK_URL}/bot_webhook/'
print("Setting the webhook url to ", webhookurl)
bot.set_webhook(url=webhookurl)
