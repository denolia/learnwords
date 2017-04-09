import logging
from pprint import pformat

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from commands import get_operands, WORD_COMMAND, handle_error
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
    date = msg['date']
    username = msg['from']['username']
    args = get_operands(WORD_COMMAND, command)
    word = args[0]

    if word is None:
        handle_error(bot, chat_id, WORD_COMMAND)
        return

    translation = args[1]
    pronunciation = args[2]

    try:
        add_word_for_user(word, translation, pronunciation, date, 0, username)
        bot.sendMessage(chat_id, 'The word is added')
        logging.info("Added word: {word} {translation} {pronunciation} for user {user}"
                     "".format(word=word, translation=translation, pronunciation=pronunciation, user=username))
    except Exception as e:
        handle_error(bot, chat_id, WORD_COMMAND, 'Cannot insert word', e)
        raise e


def check_how_many_to_mode(bot: telepot.Bot, chat_id: int, username: str, mode: Mode):
    log.debug("checking quantity of words to {mode} and starting the lesson".format(mode=mode.name))
    try:
        words_num = count_words_to_mode(username, mode)
        log.info("Words to {mode}: {num}".format(mode=mode.name, num=words_num))
    except Exception as e:
        bot.sendMessage(chat_id, 'Cannot count words to {mode} {err}'.format(mode=mode.name, err=e))
        log.error(e)
        raise e

    if words_num > 0:
        keyboard = compose_kbd_start_mode(mode)
        global message_with_inline_keyboard
        log.debug("message: {}".format(message_with_inline_keyboard))
        message_with_inline_keyboard = bot.sendMessage(chat_id,
                                                       'There are {num} words to {mode}'
                                                       ''.format(num=words_num, mode=mode.name),
                                                       reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id, 'There are no words to {mode}'.format(mode=mode.name))


def compose_kbd_start_mode(mode: Mode):
    if mode == Mode.learn:
        lesson_type = 'learning'
    else:
        lesson_type = 'repetition'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Start {lesson}'.format(lesson=lesson_type),
                              callback_data='start_{lesson}'.format(lesson=lesson_type))]])
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
