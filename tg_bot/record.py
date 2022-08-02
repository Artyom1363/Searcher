from telebot import types

import handler_sentences


class Record:
    def __init__(self, button_back=False):
        self.button_back = button_back

    def print(self, cursor, connection):

        markup = types.InlineKeyboardMarkup()

        for record_id in self.rec_ids:
            sen = handler_sentences.get_sentence_by_id(
                record_id, cursor, connection)
            button = types.InlineKeyboardButton(text=sen,
                                                callback_data=f'question_{record_id}')
            markup.add(button)

        button = types.InlineKeyboardButton(
            text="Добавить ответ на свой вопрос📥",
            callback_data=f'addSame')

        markup.add(button)

        letter = ''

        # start = time.time()
        if self.button_back:
            self.bot.edit_message_text(message_id=self.message_id,
                                       chat_id=self.USER_ID_TELEG,
                                       text=letter,
                                       reply_markup=markup,
                                       parse_mode='Markdown')
        else:
            self.bot.send_message(self.USER_ID_TELEG,
                                  letter,
                                  reply_markup=markup,
                                  parse_mode='Markdown')