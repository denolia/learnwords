import time

import schedule
import telepot

import log_conf
from enums import Mode
from words import add_word, show_next_word_to_repeat, check_how_many_to_mode, show_translation_to_learn, \
    update_word_learn, stop_lesson, \
    edit_word, show_statistics, show_controls, show_next_word_to_learn, \
    show_translation_to_repeat, update_word_repeat

log = log_conf.get_logger(__name__)

CHATS = [0, 0]
BOT = None


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    log.debug("{}, {}, {}"
              .format(content_type, chat_type, chat_id))

    username = msg['from']['username']

    if content_type != 'text':
        bot.sendMessage(chat_id, "I don't understand")
        return

    command = msg['text'].strip().lower()
    date = msg['date']
    if command == '/start':
        show_controls(bot, chat_id)
    elif command.startswith('/word'):
        add_word(bot, msg, command, chat_id)
    elif command == '/showall':
        bot.sendMessage(chat_id, str("not implemented yet"))
    elif command == 'start learning':
        check_how_many_to_mode(bot, chat_id, username, Mode.learn)
    elif command == 'start repetition':
        check_how_many_to_mode(bot, chat_id, username, Mode.repeat)
    elif command == 'stop learning':
        stop_lesson(bot, chat_id)
    elif command == 'stop repetition':
        stop_lesson(bot, chat_id)
    elif command == 'edit word':
        edit_word(bot, chat_id)
    elif command == 'show statistics':
        show_statistics(bot, chat_id, username)


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    log.debug('Callback Query:{} {} {}'.format(query_id, from_id, query_data))
    chat_id = msg['message']['chat']['id']
    date = msg['message']['date']
    username = msg['from']['username']
    if query_data == 'start_learning':
        show_next_word_to_learn(bot, chat_id, query_id, username)
    elif query_data == 'start_repetition':
        show_next_word_to_repeat(bot, chat_id, query_id, date, username)
    elif query_data.startswith('show_back_side_learn_'):
        show_translation_to_learn(bot, chat_id, query_id, query_data, username)
    elif query_data.startswith('show_back_side_repeat_'):
        show_translation_to_repeat(bot, chat_id, query_id, query_data, username)
    elif query_data.startswith('learnt_'):
        update_word_learn(bot, chat_id, query_id, query_data, date, 2, username)
    elif query_data.startswith('not_learnt_'):
        update_word_learn(bot, chat_id, query_id, query_data, date, 1, username)
    elif query_data.startswith('repeated_'):
        update_word_repeat(bot, chat_id, query_id, query_data, date, 0, username)
    elif query_data.startswith('not_repeated_'):
        update_word_repeat(bot, chat_id, query_id, query_data, date, -1, username)


def job():
    if BOT is not None:
        for chat in CHATS:
            bot.sendMessage(chat, 'Hey! Time to learn something'
                                  '\nOr maybe you have found new words for me? ^__^')
            log.debug("sent scheduled message to chat {}".format(chat))


if __name__ == '__main__':
    TOKEN = 'TOKEN'
    schedule.every().day.at("7:00").do(job)

    bot = telepot.Bot(TOKEN)
    BOT = bot
    log.info(bot.getMe())

    bot.message_loop({'chat': handle,
                      'callback_query': on_callback_query})
    log.info('Listening ...')

    # Keep the program running.
    while 1:
        schedule.run_pending()
        time.sleep(10)
