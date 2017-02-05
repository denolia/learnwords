from pprint import pprint

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from db import add_word_for_user, get_one_word_to_repeat, count_words_to_repeat, get_word_by_id, \
    set_fetched_word

message_with_inline_keyboard = None


def show_controls(bot, chat_id):
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Start learning'), KeyboardButton(text='Stop learning')],
        [KeyboardButton(text='Edit word'), KeyboardButton(text='Show statistics')]
    ], resize_keyboard=True)
    bot.sendMessage(chat_id, 'Hello! See buttons below to control your lesson', reply_markup=markup)


def add_word(bot, msg, command, chat_id):
    args = command.replace('/word', '').strip().split(";")
    word = args[0].strip()
    date = msg['date']
    username = msg['from']['username']

    if word is "":
        bot.sendMessage(chat_id=chat_id, text="Формат: /word word [; перевод; произношение]."
                                              "\nПример: /word cat; котик; кЭт")
        return
    translation = args[1].strip() if len(args) > 1 else None
    pronunciation = args[2].strip() if len(args) > 2 else None

    try:
        add_word_for_user(word, translation, pronunciation, date, 1, username)
        bot.sendMessage(chat_id, 'The word is added')
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot insert word: {}'.format(e))
        print("Cannot insert")


def check_how_many_to_learn(bot, chat_id, date, username):

    words_to_repeat = None
    try:
        words_to_repeat = count_words_to_repeat(date, username)
        pprint(words_to_repeat)

    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot count words to repeat {}'.format(e))
        print("Cannot count words to repeat")
    if words_to_repeat > 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Start learning', callback_data='start_learning')],
        ])
        global message_with_inline_keyboard
        message_with_inline_keyboard = bot.sendMessage(chat_id,
                                                       'There are {} words to repeat'.format(words_to_repeat),
                                                       reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id, 'There are no words to repeat. Take a cup of tea')


def stop_learning(bot, chat_id):
    global message_with_inline_keyboard
    msg_idf = telepot.message_identifier(message_with_inline_keyboard)
    if message_with_inline_keyboard:
        bot.editMessageText(msg_idf, 'A nice lesson! See you.',
                            reply_markup=None)
        message_with_inline_keyboard = None
    else:
        bot.sendMessage(chat_id, 'Nothing to stop')
        print("Cannot fetch a word")


def edit_word(bot, chat_id):
    bot.sendMessage(chat_id, 'Not implemented yet')


def show_statistics(bot, chat_id):
    bot.sendMessage(chat_id, 'Not implemented yet')


def show_next_word(bot, chat_id, query_id, date, username):
    word_to_repeat = None
    try:
        word_to_repeat = get_one_word_to_repeat(date, username)
        pprint(word_to_repeat)

    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        print("Cannot fetch a word")

    global message_with_inline_keyboard
    if message_with_inline_keyboard:
        msg_idf = telepot.message_identifier(message_with_inline_keyboard)
        if word_to_repeat is not None:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Show back side',
                                      callback_data='show_back_side_{}'.format(word_to_repeat[0]))],
            ])
            bot.editMessageText(msg_idf, '{}'.format(word_to_repeat[1]),
                                reply_markup=keyboard)
        else:
            stop_learning(bot, chat_id)
    else:
        bot.answerCallbackQuery(query_id,
                                text='No previous message to edit')


def show_translation(bot, chat_id, query_id, query_data, username):
    word_id = query_data.replace('show_back_side_', '')
    # go to the db and fetch all for the word
    word_info = None
    try:
        word_info = get_word_by_id(word_id, username)
        pprint(word_info)

    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        print("Cannot fetch a word")

    if word_info:
        global message_with_inline_keyboard

        if message_with_inline_keyboard:
            msg_idf = telepot.message_identifier(message_with_inline_keyboard)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Not fetched',
                                      callback_data='not_fetched_{}'.format(word_info[0])),
                 InlineKeyboardButton(text='Fetched',
                                      callback_data='fetched_{}'.format(word_info[0]))
                 ]
            ])
            word = word_info[1] if word_info[1] is not None else ""
            translation = word_info[2] if word_info[2] is not None else ""
            pronunciation = word_info[3] if word_info[3] is not None else ""
            bot.editMessageText(msg_idf, '{}\n{}\n{}'.format(word, translation, pronunciation),
                                reply_markup=keyboard)
        else:
            bot.answerCallbackQuery(query_id,
                                    text='No previous message to edit')


def word_fetched(bot, chat_id, query_id, query_data, date_unix, status, username):
    word_id = None
    if status != 0:
        word_id = query_data.replace('not_fetched_', '')
    else:
        word_id = query_data.replace('fetched_', '')

    # go to the db update word's dates and write a repetition for the word

    # todo set direction
    direction = 0
    try:
        int(word_id)
        repeat_after = set_fetched_word(word_id, date_unix, direction, status, username)
        #todo after what?
        bot.answerCallbackQuery(query_id,
                                text="We will repeat it after {}".format(repeat_after))
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        print("Cannot fetch a word")
        print(e)

    show_next_word(bot, chat_id, query_id, date_unix, username)
