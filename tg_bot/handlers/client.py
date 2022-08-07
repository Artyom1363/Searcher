from typing import Any

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext

from tg_bot.config import USER_GUIDE, VIDEO_GUIDE
from tg_bot.keyboards.keyboards import get_relevant_topics_keyboard, get_comment_markup
from tg_bot.create_bot import bot
from tg_bot.states import UserState

from search.elastic_searcher import ElasticSearcher

from data_types.values import Sentence
from data_types.post import Post


# @dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(text='Пожалуйста, потратьте 30 секунд и ознакомьтесь с Руководством пользователя:')
    await bot.send_document(message.chat.id, USER_GUIDE)
    await bot.send_video(message.chat.id, VIDEO_GUIDE)
    await bot.send_message(message.chat.id, text='Введите запрос:')
    await UserState.search.set()
    # print(type(UserState))
    # await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


async def show_topic(callback):
    # Вы нажали на кнопку и сработал call back handler
    _type, _id = callback.data.split('_')
    assert (_type == 'questionScale')

    topic = ElasticSearcher.get_topic_by_id(_id)
    await callback.answer(f"{topic[0:200]}", show_alert=True)


async def show_comments(callback):
    _type, _id = callback.data.split('_')
    assert (_type == 'question')
    topic = ElasticSearcher.get_topic_by_id(_id)
    comments = ElasticSearcher.get_comments_by_topic_id(_id, limit=1)
    if len(comments) == 0:
        await callback.answer(f"По данной теме все комментарии удалены", show_alert=True)
        return

    markup = get_comment_markup(comments[0].get_sentence(), comments[0].get_id())

    await bot.send_message(callback.message.chat.id,
                           text=f'Сейчас вы видите комментарии пользователей на вопрос: *{topic}*',
                           reply_markup=markup,
                           parse_mode='Markdown')
    # message_id = callback.message.message_id,
    # chat_id = callback.message.chat.id,
    # await callback.answer(f"Тут откроются коменты", show_alert=True)


async def self_ans_callback_handler(callback, state=FSMContext):
    # search_values = await state.get_data()
    await bot.send_message(callback.message.chat.id, f"Введи ответ (это может быть текст)")
    await UserState.adding.set()


async def self_answer_text_message(message: types.Message, state=FSMContext):
    sentence = Sentence(sentence=message.text)
    search_values = await state.get_data()
    # message.answer()
    # print("search_values: ", search_values, " ", type(search_values))
    post = Post(
        key=search_values.get('search'),
        values=[sentence])

    ElasticSearcher.add_record(post)

    await message.answer("Спасибо вы добавили ответ на свой вопрос.")
    await UserState.search.set()


async def search(message: types.Message, state: FSMContext):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await state.update_data(search=message.text)

    relevant = ElasticSearcher.get_relevant_topics(message=message.text)
    if len(relevant) == 0:
        await message.answer("К сожалению по вашему запросу нам ничего не удалось найти!")
    else:
        markup = get_relevant_topics_keyboard(relevant)
        await message.answer("Вот что нам удалось найти", reply_markup=markup, parse_mode='Markdown')


async def default_callback_handler(callback, state=FSMContext):
    search_values = await state.get_data()

    await callback.answer(f"Пока что не существует обработчика, search_value={search_values}", show_alert=True)
    # await


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(send_welcome,
                                commands=['start', 'help'],
                                state=[None, UserState.search])

    dp.register_callback_query_handler(show_topic,
                                       lambda call: call.data.startswith("questionScale_"),
                                       state=[None, UserState.search])

    dp.register_callback_query_handler(show_comments,
                                       lambda call: call.data.startswith("question_"),
                                       state=[None, UserState.search])

    dp.register_message_handler(self_answer_text_message,
                                lambda call: True,
                                state=UserState.adding)

    dp.register_callback_query_handler(self_ans_callback_handler,
                                       lambda call: call.data == 'selfAns',
                                       state=[None, UserState.search])

    dp.register_callback_query_handler(default_callback_handler,
                                       lambda call: True,
                                       state=[None, UserState.search])

    dp.register_message_handler(search,
                                state=[None, UserState.search])