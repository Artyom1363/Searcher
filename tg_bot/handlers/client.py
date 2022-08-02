from aiogram import types
from aiogram.dispatcher import Dispatcher

from tg_bot.config import USER_GUIDE, VIDEO_GUIDE
from tg_bot.keyboards.keyboards import get_relevant_topics_keyboard
from tg_bot.create_bot import bot

from search.elastic_searcher import ElasticSearcher


# @dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(text='Пожалуйста, потратьте 30 секунд и ознакомьтесь с Руководством пользователя:')
    await bot.send_document(message.chat.id, USER_GUIDE)
    await bot.send_video(message.chat.id, VIDEO_GUIDE)
    await bot.send_message(message.chat.id, text='Введите запрос:')
    # await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


async def callback_handler(callback):
    # Вы нажали на кнопку и сработал call back handler
    await callback.answer(f" callback data: {callback.data}", show_alert=True)
    # bot.send_message(call.message.chat.id, )


# @dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    relevant = ElasticSearcher.get_relevant_topics(message=message.text)
    if len(relevant) == 0:
        await message.answer("К сожалению по заданному запросу нам ничего не удалось найти!")
    else:
        markup = get_relevant_topics_keyboard(relevant)
        await message.answer("Вот что нам удалось найти", reply_markup=markup, parse_mode='Markdown')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_callback_query_handler(callback_handler, lambda call: True)
    dp.register_message_handler(echo)
    # dp.register_message_handler()
