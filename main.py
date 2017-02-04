import telepot
from pprint import pprint

import time

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from db import add_word_for_user, get_words_to_repeat, get_translation_for_word
from words import add_word, show_next_word, check_how_many_to_learn, show_translation, word_fetched


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    username = msg['from']['username']

    if content_type != 'text':
        bot.sendMessage(chat_id, "I don't understand")
        return

    command = msg['text'].strip().lower()
    date = msg['date']

    if command.startswith('/word'):
        add_word(bot, msg, command, chat_id)
    elif command == '/showall':
        bot.sendMessage(chat_id, str("not implemented yet"))

    elif command == '/howmany':
        check_how_many_to_learn(bot, chat_id, date, username)

    elif command == '/learn':
        print("it works")


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    chat_id = msg['message']['chat']['id']
    date = msg['message']['date']
    username = msg['from']['username']
    # bot.answerCallbackQuery(query_id, text='Got it')
    if query_data == 'start_learning':
        show_next_word(bot, chat_id, query_id, date, username)
    if query_data.startswith('show_back_side'):
        show_translation(bot, chat_id, query_id, query_data, username)
    if query_data.startswith('fetched'):
        word_fetched(bot, chat_id, query_id, query_data, date, 0, username)
    if query_data.startswith('not_fetched'):
        word_fetched(bot, chat_id, query_id, query_data, date, -1, username)


if __name__ == '__main__':
    TOKEN = 'TOKEN'

    bot = telepot.Bot(TOKEN)
    print(bot.getMe())
    # need to monitor the offset :(
    # response = bot.getUpdates()
    # pprint(response)

    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})
    print('Listening ...')
    # chat shall exist

    # Keep the program running.
    while 1:
        time.sleep(10)
