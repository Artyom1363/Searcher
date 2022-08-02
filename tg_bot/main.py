from aiogram.utils import executor
from tg_bot.create_bot import dp
from tg_bot.handlers import client

client.register_handlers_client(dp)

if __name__ == '__main__':
    executor.start_polling(dp)
