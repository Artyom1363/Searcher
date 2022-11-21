from aiogram.utils import executor
from tg_bot.create_bot import dp
from tg_bot.handlers import client
from src.pg import pool

client.register_handlers_client(dp, pool)

if __name__ == '__main__':
    executor.start_polling(dp)
