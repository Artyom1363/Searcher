from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from tg_bot.config import TG_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=storage)
