# coding=utf-8

import logging
from collections import namedtuple

SEPARATOR = ';'

Command = namedtuple('Command', 'name, command, max_operands, format, example')

WORD_COMMAND = Command(name='word',
                       command='/word',
                       max_operands=3,
                       format='/word word [; translation; transcription]',
                       example='/word hello; привет; хэлОу')

SHOW_ALL_COMMAND = Command(name='showall',
                           command='/showall',
                           max_operands=0,
                           format='/showall',
                           example='/showall')


def get_operands(command: Command, message: str) -> list:
    """Parses message string and retrieves command operands

    """

    if not isinstance(command, Command):
        raise ValueError("Illegal argument types: "
                         "expected '{type_expected}', "
                         "actual '{type_actual}'".format(type_expected=Command.__name__,
                                                         type_actual=type(command).__name__))
    operands = message.replace('/{}'.format(command.name), '').strip().split(SEPARATOR)
    result = []

    if len(operands) > command.max_operands:
        raise ValueError("Too many arguments")

    for i, _ in enumerate(operands):
        result.append(operands[i].strip())
        if result[i] is "":
            result[i] = None

    while len(result) < command.max_operands:
        result.append(None)

    return result


def handle_error(bot, chat_id, command: Command, custom_msg='', exception=None):
    msg = '{custom_msg}\n{format}\n{example}'.format(custom_msg=custom_msg,
                                                     format=command.format,
                                                     example=command.example)
    bot.sendMessage(chat_id=chat_id, text=msg)
    if exception is not None:
        logging.error(exception)
