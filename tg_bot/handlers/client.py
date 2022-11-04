from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext

from tg_bot.config import USER_GUIDE, VIDEO_GUIDE
from tg_bot.keyboards import get_relevant_topics_keyboard, get_comment_markup
from tg_bot.create_bot import bot
from tg_bot.states import UserState

from src.search import Searcher

from src.data_types import Sentence

from functools import partial


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


async def show_topic(callback):
    # Вы нажали на кнопку и сработал call back handler
    _type, _id = callback.data.split('_', 1)
    assert (_type == 'questionScale')

    topic = Searcher.get_topic_by_id(_id)
    await callback.answer(f"{topic[0:200]}", show_alert=True)


async def show_comments_by_topic(callback, pool=None):
    _type, topic_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id
    assert (_type == 'question')

    topic = Searcher.get_topic_by_id(topic_id)
    comments = await Searcher.get_comments_by_topic_id(topic_id, user_id, pool, limit=1)

    if len(comments) == 0:
        await callback.answer(f"По данной теме все комментарии удалены", show_alert=True)
        return

    markup = get_comment_markup(comment=comments[0])
    await bot.send_message(user_id,
                           text=f'Сейчас вы видите комментарии пользователей на вопрос: *{topic}*',
                           reply_markup=markup,
                           parse_mode='Markdown')
    # await callback.answer(f"Тут откроются коменты", show_alert=True)


async def self_ans_callback_handler(callback, state=FSMContext):
    # search_values = await state.get_data()
    await bot.send_message(callback.message.chat.id, f"Введи ответ (это может быть текст)")
    await UserState.adding.set()


async def self_answer_text_message(message: types.Message, state=FSMContext):
    sentence = Sentence(sentence=message.text)
    search_values = await state.get_data()

    Searcher.add_record(topic=search_values.get('search'), value=sentence)

    await message.answer("Спасибо вы добавили ответ на свой вопрос.")
    await UserState.search.set()


async def search(message: types.Message, state: FSMContext):
    await state.update_data(search=message.text)

    relevant = Searcher.get_relevant_topics(message=message.text)
    if len(relevant) == 0:
        await message.answer("К сожалению по вашему запросу нам ничего не удалось найти!")
    else:
        markup = get_relevant_topics_keyboard(relevant)
        await message.answer("Вот что нам удалось найти", reply_markup=markup, parse_mode='Markdown')


async def like_callback_handler(callback, state=FSMContext, pool=None):
    _type, comment_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id
    comment = await Searcher.get_comment_by_id(comment_id=comment_id, user_id=user_id, pool=pool)
    await comment.get_like().switch()
    markup = get_comment_markup(comment)

    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=markup,
                                     parse_mode='Markdown')


async def favorite_callback_handler(callback, state=FSMContext, pool=None):
    _type, comment_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id

    comment = await Searcher.get_comment_by_id(comment_id=comment_id, user_id=user_id, pool=pool)
    await comment.get_favorite().switch()
    markup = get_comment_markup(comment)

    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=markup,
                                     parse_mode='Markdown')


async def default_callback_handler(callback, state=FSMContext):
    search_values = await state.get_data()

    await callback.answer(f"Пока что не существует обработчика, search_value={search_values}", show_alert=True)


def register_handlers_client(dp: Dispatcher, pool_):
    show_comments_by_topic_partial = partial(show_comments_by_topic, pool=pool_)
    like_callback_handler_partial = partial(like_callback_handler, pool=pool_)
    favorite_callback_handler_partial = partial(favorite_callback_handler, pool=pool_)
    dp.register_message_handler(send_welcome,
                                commands=['start', 'help'],
                                state=[None, UserState.search])

    dp.register_callback_query_handler(show_topic,
                                       lambda call: call.data.startswith("questionScale_"),
                                       state=[None, UserState.search])

    dp.register_callback_query_handler(show_comments_by_topic_partial,
                                       lambda call: call.data.startswith("question_"),
                                       state=[None, UserState.search])

    dp.register_message_handler(self_answer_text_message,
                                lambda call: True,
                                state=UserState.adding)

    dp.register_callback_query_handler(self_ans_callback_handler,
                                       lambda call: call.data == 'selfAns',
                                       state=[None, UserState.search])

    dp.register_callback_query_handler(like_callback_handler_partial,
                                       lambda call: call.data.startswith('like_'),
                                       state=[None, UserState.search])

    dp.register_callback_query_handler(favorite_callback_handler_partial,
                                       lambda call: call.data.startswith('favorite_'),
                                       state=[None, UserState.search])

    dp.register_callback_query_handler(default_callback_handler,
                                       lambda call: True,
                                       state=[None, UserState.search])

    dp.register_message_handler(search,
                                state=[None, UserState.search])
