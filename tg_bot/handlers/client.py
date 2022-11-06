from functools import partial

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from asyncpg import Connection

from src.search import Searcher

from src.data_types import Sentence

from tg_bot.config import USER_GUIDE, VIDEO_GUIDE
from tg_bot.keyboards import get_relevant_topics_keyboard, get_comment_markup
from tg_bot.create_bot import bot
from tg_bot.states import UserState
from tg_bot.messages import (
    HELLO_MESSAGE,
    COMMENTS_DELETED,
    SHOWING_COMMENTS,
    NOTHING_FOUND,
    ENTER_YOUR_COMMENT,
    ENTER_SELF_ANSWER,
    ENTERED_ANSWER,
    VIEWED_ALL_COMMENTS,
    WARNING_MESSAGE
)


# @dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(text=HELLO_MESSAGE)
    await bot.send_document(message.chat.id, USER_GUIDE)
    await bot.send_video(message.chat.id, VIDEO_GUIDE)
    await bot.send_message(message.chat.id, text='Введите запрос:')
    await UserState.search.set()


async def show_topic(callback):
    # Вы нажали на кнопку и сработал call back handler
    _type, _id = callback.data.split('_', 1)
    # assert (_type == 'questionScale')

    topic = Searcher.get_topic_by_id(_id)
    await callback.answer(f"{topic[0:200]}", show_alert=True)


async def show_comments_by_topic(callback, pool: Connection = None):
    _type, topic_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id
    # assert (_type == 'question')

    topic = Searcher.get_topic_by_id(topic_id)
    comment = await Searcher.get_best_comment_by_topic_id(topic_id,
                                                          user_id,
                                                          pool)

    if comment is None:
        await callback.answer(COMMENTS_DELETED, show_alert=True)
        return

    markup = get_comment_markup(comment=comment)
    await bot.send_message(user_id,
                           text=SHOWING_COMMENTS.format(topic=topic),
                           reply_markup=markup,
                           parse_mode='Markdown')
    # await callback.answer(f"Тут откроются коменты", show_alert=True)


async def self_ans_callback_handler(callback, state=FSMContext):
    # search_values = await state.get_data()
    await bot.send_message(callback.message.chat.id, ENTER_SELF_ANSWER)
    await UserState.adding.set()


async def self_answer_text_message(message: types.Message,
                                   state=FSMContext,
                                   pool: Connection = None):
    sentence = Sentence(sentence=message.text)
    search_values = await state.get_data()

    await Searcher.add_record(topic=search_values.get('search'),
                              value=sentence, pool=pool)

    await message.answer(ENTERED_ANSWER)
    await UserState.search.set()


async def search(message: types.Message, state: FSMContext):
    await state.update_data(search=message.text)

    relevant = Searcher.get_relevant_topics(message=message.text)
    if len(relevant) == 0:
        await message.answer(NOTHING_FOUND)
    else:
        markup = get_relevant_topics_keyboard(relevant)
        await message.answer("Вот что нам удалось найти",
                             reply_markup=markup,
                             parse_mode='Markdown')


async def like_callback_handler(callback, state=FSMContext,
                                pool: Connection = None):
    _type, comment_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id
    comment = await Searcher.get_comment_by_id(comment_id=comment_id,
                                               user_id=user_id,
                                               pool=pool)
    await comment.get_like().switch()
    markup = get_comment_markup(comment)

    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=markup,
                                     parse_mode='Markdown')


async def favorite_callback_handler(callback, state=FSMContext,
                                    pool: Connection = None):
    _type, comment_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id

    comment = await Searcher.get_comment_by_id(comment_id=comment_id,
                                               user_id=user_id, pool=pool)
    await comment.get_favorite().switch()
    markup = get_comment_markup(comment)

    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=markup,
                                     parse_mode='Markdown')


async def next_comment_callback_handler(callback, state=FSMContext,
                                        pool: Connection = None):
    # print(f"next_comment_callback_handler called")
    _type, comment_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id

    comment = await Searcher.get_next_comment(comment_id=comment_id,
                                              user_id=user_id, pool=pool)
    if comment is None:
        await callback.answer(VIEWED_ALL_COMMENTS, show_alert=True)
        return

    markup = get_comment_markup(comment)
    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=markup,
                                     parse_mode='Markdown')


async def prev_comment_callback_handler(callback, state=FSMContext,
                                        pool: Connection = None):
    # print(f"next_comment_callback_handler called")
    _type, comment_id = callback.data.split('_', 1)
    user_id = callback.message.chat.id

    comment = await Searcher.get_prev_comment(comment_id=comment_id,
                                              user_id=user_id, pool=pool)
    if comment is None:
        await callback.answer(VIEWED_ALL_COMMENTS, show_alert=True)
        return

    markup = get_comment_markup(comment)
    await callback.message.edit_text(text=callback.message.text,
                                     reply_markup=markup,
                                     parse_mode='Markdown')


async def additional_answer_handler(callback, state=FSMContext):
    await bot.send_message(callback.message.chat.id, ENTER_YOUR_COMMENT)
    await UserState.additional_ans.set()
    await state.update_data(comment_id=callback.data.split('_', 1)[1])


async def additional_answer_text_message(message: types.Message,
                                         state=FSMContext,
                                         pool: Connection = None):
    sentence = Sentence(sentence=message.text)
    state_data = await state.get_data()
    comment_id = state_data.get('comment_id')
    user_id = message.chat.id
    comment = await Searcher.get_comment_by_id(comment_id=comment_id,
                                               user_id=user_id,
                                               pool=pool)
    topic_id = comment.get_topic_id()
    await Searcher.append_comment_by_topic_id(topic_id=topic_id,
                                              value=sentence,
                                              user_id=user_id, pool=pool)

    await message.answer(ENTERED_ANSWER)
    await UserState.search.set()


async def default_callback_handler(callback, state=FSMContext):
    search_values = await state.get_data()
    await callback.answer(WARNING_MESSAGE.format(search_values),
                          show_alert=True)


def register_handlers_client(dp: Dispatcher, pool):
    show_comments_by_topic_partial = partial(
        show_comments_by_topic, pool=pool
    )
    self_answer_text_message_partial = partial(
        self_answer_text_message, pool=pool
    )
    like_callback_handler_partial = partial(
        like_callback_handler, pool=pool
    )
    favorite_callback_handler_partial = partial(
        favorite_callback_handler, pool=pool
    )
    next_comment_callback_handler_partial = partial(
        next_comment_callback_handler, pool=pool
    )
    prev_comment_callback_handler_partial = partial(
        prev_comment_callback_handler, pool=pool
    )
    additional_answer_text_message_partial = partial(
        additional_answer_text_message, pool=pool
    )

    dp.register_message_handler(send_welcome,
                                commands=['start', 'help'],
                                state=[None, UserState.search])

    dp.register_callback_query_handler(
        show_topic,
        lambda call: call.data.startswith("questionScale_"),
        state=[None, UserState.search]
    )

    dp.register_callback_query_handler(
        show_comments_by_topic_partial,
        lambda call: call.data.startswith("question_"),
        state=[None, UserState.search]
    )

    dp.register_message_handler(
        self_answer_text_message_partial,
        lambda call: True,
        state=UserState.adding
    )

    dp.register_callback_query_handler(
        self_ans_callback_handler,
        lambda call: call.data == 'selfAns',
        state=[None, UserState.search]
    )

    dp.register_callback_query_handler(
        like_callback_handler_partial,
        lambda call: call.data.startswith('like_'),
        state=[None, UserState.search]
    )

    dp.register_callback_query_handler(
        favorite_callback_handler_partial,
        lambda call: call.data.startswith('favorite_'),
        state=[None, UserState.search]
    )

    dp.register_callback_query_handler(
        next_comment_callback_handler_partial,
        lambda call: call.data.startswith('next_'),
        state=[None, UserState.search]
    )

    dp.register_callback_query_handler(
        prev_comment_callback_handler_partial,
        lambda call: call.data.startswith('prev_'),
        state=[None, UserState.search]
    )

    dp.register_callback_query_handler(
        additional_answer_handler,
        lambda call: call.data.startswith('add_'),
        state=[None, UserState.search]
    )

    dp.register_message_handler(
        additional_answer_text_message_partial,
        lambda call: True,
        state=UserState.additional_ans
    )

    dp.register_callback_query_handler(
        default_callback_handler,
        lambda call: True,
        state=[None, UserState.search]
    )

    dp.register_message_handler(
        search,
        state=[None, UserState.search]
    )
