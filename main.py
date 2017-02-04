import telepot
from pprint import pprint

import time

from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from db import add_word_for_user, get_words_to_repeat


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    pprint(msg)
    username = msg['from']['username']

    if content_type != 'text':
        bot.sendMessage(chat_id, "I don't understand")
        return

    command = msg['text'].strip().lower()
    date = msg['date']

    # Tells who has sent you how many messages
    if command.startswith('/word'):
        args = command.replace('/word', '').strip().split(";")
        word = args[0].strip()
        if word is "":
            bot.sendMessage(chat_id=chat_id, text="Формат: /word word [; перевод; произношение]."
                                                                 "\nПример: /word cat; котик; кЭт")
            return
        translation = args[1].strip() if len(args) > 1 else None
        pronunciation = args[2].strip() if len(args) > 2 else None

        try:
            add_word_for_user(word, translation, pronunciation, date, username)
            bot.sendMessage(chat_id, 'The word is added')
        except Exception as e:
            bot.sendMessage(chat_id, 'Cannot insert word: {}'.format(e))
            print("Cannot insert")

    # read next sender's messages
    elif command == '/showall':
        bot.sendMessage(chat_id, str("not implemented yet"))

    elif command == '/howmany':
        try:
            words_to_repeat = get_words_to_repeat(date, username)
            pprint(words_to_repeat)
            num = len(words_to_repeat)
            bot.sendMessage(chat_id, 'There are {} words to repeat'.format(num))
        except Exception as e:
            bot.sendMessage(chat_id, 'Cannot insert word: {}'.format(e))
            print("Cannot insert")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='', callback_data='press')],
        ])

        bot.sendMessage(chat_id, 'Use inline keyboard', reply_markup=keyboard)

    elif command == '/начать':

        print("it works")


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    bot.answerCallbackQuery(query_id, text='Got it')

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