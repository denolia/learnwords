import logging
from pprint import pformat

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from db import add_word_for_user, get_one_word_to_repeat, count_words_to_mode, get_word_by_id, \
    set_learnt_word, get_one_word_to_learn, set_repeated_word, count_words, count_words_green
from enums import Mode

log = logging.getLogger(__name__)

message_with_inline_keyboard = None


def show_controls(bot, chat_id):
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Start repetition'), KeyboardButton(text='Stop repetition')],
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
        add_word_for_user(word, translation, pronunciation, date, 0, username)
        bot.sendMessage(chat_id, 'The word is added')
        logging.info("Added word: {} {} {} for user {}".format(word, translation, pronunciation, username))
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot insert word: {}'.format(e))
        print("Cannot insert")
        logging.error(e)
        raise e


def check_how_many_to_learn(bot, chat_id, username):
    log.debug("checking quantity of words to learn and starting the lesson")
    try:
        words_to_learn = count_words_to_mode(username, Mode.learn)
        log.info("Words to learn: {}".format(words_to_learn))
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot count words to repeat {}'.format(e))
        log.error(e)
        raise e

    if words_to_learn > 0:
        keyboard = compose_kbd_start_learning()
        global message_with_inline_keyboard
        log.debug("message: {}".format(message_with_inline_keyboard))
        message_with_inline_keyboard = bot.sendMessage(chat_id,
                                                       'There are {} words to learn'.format(words_to_learn),
                                                       reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id, 'There are no words to learn. Add them using /word command')


def compose_kbd_start_learning():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Start learning', callback_data='start_learning')]])
    return keyboard


def check_how_many_to_repeat(bot, chat_id, username):
    try:
        words_to_repeat = count_words_to_mode(username, Mode.repeat)
        log.info("Words to repeat: {}".format(words_to_repeat))
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot count words to repeat {}'.format(e))
        log.error(e)
        raise e

    if words_to_repeat > 0:
        keyboard = compose_kbd_start_repeat()
        global message_with_inline_keyboard
        log.debug("message: {}".format(message_with_inline_keyboard))
        message_with_inline_keyboard = bot.sendMessage(chat_id,
                                                       'There are {} words to repeat'.format(words_to_repeat),
                                                       reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id, 'There are no words to repeat. Take a cup of tea')


def compose_kbd_start_repeat():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Start repetition', callback_data='start_repetition')]])
    return keyboard


def stop_lesson(bot, chat_id):
    global message_with_inline_keyboard
    if message_with_inline_keyboard:
        log.debug("message: {}".format(message_with_inline_keyboard))

        msg_idf = telepot.message_identifier(message_with_inline_keyboard)
        bot.editMessageText(msg_idf, 'A nice lesson! See you.',
                            reply_markup=None)
        message_with_inline_keyboard = None
        log.debug("message: {}".format(message_with_inline_keyboard))

    else:
        bot.sendMessage(chat_id, 'Nothing to stop')
        logging.info("Nothing to stop")


def edit_word(bot, chat_id):
    bot.sendMessage(chat_id, 'Not implemented yet')


def show_statistics(bot, chat_id, username):
    num_to_learn = count_words_to_mode(username, Mode.learn)
    num_to_repeat = count_words_to_mode(username, Mode.repeat)
    num_all = count_words(username)
    num_green = count_words_green(username)
    stat = 'You have: ' \
           '\n{learn} words to learn' \
           '\n{repeat} ready words to repeat' \
           '\n{green} green words to repeat' \
           '\n{all} total words' \
           ''.format(learn=num_to_learn, repeat=num_to_repeat, all=num_all, green=num_green)
    bot.sendMessage(chat_id, stat)


def show_next_word_to_learn(bot, chat_id, query_id, username):
    log.debug("showing next word to learn")
    word_to_learn = None
    try:
        word_to_learn = get_one_word_to_learn(username)
        log.debug("word to learn: {}".format(word_to_learn))

    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        log.error("Cannot fetch a word {}", e)

    global message_with_inline_keyboard
    if message_with_inline_keyboard:
        log.debug("message: {}".format(message_with_inline_keyboard))
        msg_idf = telepot.message_identifier(message_with_inline_keyboard)
        if word_to_learn is not None:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Show back side',
                                      callback_data='show_back_side_learn_{}'.format(word_to_learn[0]))]])
            bot.editMessageText(msg_idf, '{}'.format(word_to_learn[1]),
                                reply_markup=keyboard)
        else:
            stop_lesson(bot, chat_id)
    else:
        bot.answerCallbackQuery(query_id,
                                text='No previous message to edit')


def show_next_word_to_repeat(bot, chat_id, query_id, date, username):
    log.debug("showing next word to repeat")

    word_to_repeat = None
    try:
        word_to_repeat = get_one_word_to_repeat(date, username)
        log.debug("word to repeat: {}".format(word_to_repeat))

    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        log.error("Cannot fetch a word", exc_info=True)

    global message_with_inline_keyboard
    if message_with_inline_keyboard:
        log.debug("message: {}".format(message_with_inline_keyboard))

        msg_idf = telepot.message_identifier(message_with_inline_keyboard)
        if word_to_repeat is not None:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Show back side',
                                      callback_data='show_back_side_repeat_{}'.format(word_to_repeat[0]))]])
            bot.editMessageText(msg_idf, '{}'.format(word_to_repeat[1]),
                                reply_markup=keyboard)
        else:
            stop_lesson(bot, chat_id)
    else:
        bot.answerCallbackQuery(query_id,
                                text='No previous message to edit')


def show_translation_to_learn(bot, chat_id, query_id, query_data, username):
    word_id = query_data.replace('show_back_side_learn_', '')
    log.debug("show translation to learn word {}".format(word_id))

    word_info = fetch_word_info(bot, chat_id, username, word_id)

    if word_info:
        global message_with_inline_keyboard

        if message_with_inline_keyboard:
            log.debug("message: {}".format(message_with_inline_keyboard))

            msg_idf = telepot.message_identifier(message_with_inline_keyboard)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Not learnt',
                                      callback_data='not_learnt_{}'.format(word_info[0])),
                 InlineKeyboardButton(text='Learnt',
                                      callback_data='learnt_{}'.format(word_info[0]))
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


def show_translation_to_repeat(bot, chat_id, query_id, query_data, username):
    word_id = query_data.replace('show_back_side_repeat_', '')
    log.debug("show translation to repeat word {}".format(word_id))

    word_info = fetch_word_info(bot, chat_id, username, word_id)

    if word_info:
        global message_with_inline_keyboard

        if message_with_inline_keyboard:
            log.debug("message: {}".format(message_with_inline_keyboard))

            msg_idf = telepot.message_identifier(message_with_inline_keyboard)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Don't remember",
                                      callback_data='not_repeated_{}'.format(word_info[0])),
                 InlineKeyboardButton(text='Remember',
                                      callback_data='repeated_{}'.format(word_info[0]))
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


def fetch_word_info(bot, chat_id, username, word_id):
    # go to the db and fetch all for the word
    word_info = None
    try:
        int(word_id)
        word_info = get_word_by_id(word_id, username)
        log.debug(pformat(word_info))

    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        log.error("Cannot fetch a word", exc_info=True)
    return word_info


def update_word_learn(bot, chat_id, query_id, query_data, date_unix, status, username):
    if status == 1:
        word_id = query_data.replace('not_learnt_', '')
    else:
        word_id = query_data.replace('learnt_', '')
    log.debug("Updating learning status for word {}".format(word_id))

    # go to the db update word's dates and write a repetition for the word
    try:
        int(word_id)
        set_learnt_word(word_id, date_unix, status, username)
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        log.error("Cannot fetch a word", exc_info=True)

    show_next_word_to_learn(bot, chat_id, query_id, username)


def update_word_repeat(bot, chat_id, query_id, query_data, date_unix, status, username):
    if status != 0:
        word_id = query_data.replace('not_repeated_', '')
    else:
        word_id = query_data.replace('repeated_', '')
    log.debug("Updating repeat status for word {}".format(word_id))

    # go to the db update word's dates and write a repetition for the word

    # todo set direction
    direction = 0
    try:
        int(word_id)
        repeat_after = set_repeated_word(word_id, date_unix, direction, status, username)
        bot.answerCallbackQuery(query_id,
                                text="We will repeat it after {}".format(repeat_after))
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot fetch a word: {}'.format(e))
        log.error("Cannot fetch a word", exc_info=True)

    show_next_word_to_repeat(bot, chat_id, query_id, date_unix, username)
