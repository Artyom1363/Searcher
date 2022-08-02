from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from tg_bot.config import TG_TOKEN

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)