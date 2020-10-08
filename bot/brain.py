import os

from bot import fsm_telebot
from settings import BOT_TOKEN
from bot.fsm_telebot.storage.redis import RedisStorage

storage = RedisStorage(url=os.environ.get('REDIS_URL'))
bot = fsm_telebot.TeleBot(BOT_TOKEN, storage)
