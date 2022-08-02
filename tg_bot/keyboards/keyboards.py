from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_search_record_button(topic: str, id_: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=topic, callback_data=f'question_{id_}')


def get_relevant_topics_keyboard(records: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    for topic, id_ in records:
        button = get_search_record_button(topic, id_)
        markup.add(button)

    button = InlineKeyboardButton(text="Добавить ответ на свой вопрос📥",
                                  callback_data=f'addSame')

    markup.add(button)
    return markup
