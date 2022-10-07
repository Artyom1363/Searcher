from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from tg_bot.config import TG_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tg_bot.pg import create_pool
import asyncio


storage = MemoryStorage()

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=storage)

loop = asyncio.get_event_loop()
pool = loop.run_until_complete(create_pool())
