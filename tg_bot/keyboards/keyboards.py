from typing import List, Tuple
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.data_types import Comment


def get_search_record_button(topic: str, id_: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=topic, callback_data=f'question_{id_}')


def get_relevant_topics_keyboard(records: List[Tuple[str, str]]
                                 ) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    counter = 1
    buttons_loop = []
    for topic, id_ in records:
        button = get_search_record_button(topic, id_)
        button_loop = InlineKeyboardButton(
            text="🔍" + str(counter),
            callback_data=f'questionScale_{id_}'
        )
        counter += 1
        buttons_loop.append(button_loop)
        markup.add(button)
    markup.row(*buttons_loop)

    button = InlineKeyboardButton(
        text="Добавить ответ на свой вопрос📥",
        callback_data="selfAns"
    )

    markup.add(button)
    return markup


def get_comment_markup(comment: Comment) -> InlineKeyboardMarkup:
    liked = comment.get_like().is_on()
    likes = comment.get_like().get_total_likes()
    comment_id = comment.get_id()
    favorite = comment.get_favorite().is_on()
    comment_text = comment.get_value().get_sentence()

    if liked:
        like_expose = str(likes) + "❤️"
    else:
        like_expose = str(likes) + "♡"

    button_like = InlineKeyboardButton(
        text=like_expose,
        callback_data=f'like_{comment_id}'
    )

    button_before = InlineKeyboardButton(
        text='⬅️',
        callback_data=f'prev_{comment_id}'
    )

    button_add = InlineKeyboardButton(
        text='📥',
        callback_data=f'add_{comment_id}'
    )

    button_after = InlineKeyboardButton(
        text='➡️',
        callback_data=f'next_{comment_id}'
    )

    button_comment = InlineKeyboardButton(
        text=comment_text,
        callback_data=f'comment_{comment_id}'
    )

    if favorite:
        button_favorite = InlineKeyboardButton(
            text='✅',
            callback_data=f'favorite_{comment_id}'
        )
    else:
        button_favorite = InlineKeyboardButton(
            text='➕',
            callback_data=f'favorite_{comment_id}'
        )

    markup = InlineKeyboardMarkup()
    markup.add(button_comment)
    markup.row(button_like, button_add, button_favorite)
    markup.row(button_before, button_after)

    return markup
