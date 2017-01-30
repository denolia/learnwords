import telepot
from pprint import pprint

import time
from words_storage import WordsStorage

bot = telepot.Bot('TOKEN')
print(bot.getMe())
# need to monitor the offset :(
# response = bot.getUpdates()
# pprint(response)

storage = WordsStorage()

storage.add_word("utter", "вымолвить, произносить", "Аттер")


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type != 'text':
        bot.sendMessage(chat_id,"I don't understand")
        return

    command = msg['text'].strip().lower()

    # Tells who has sent you how many messages
    if command.startswith('/word'):
        args = command.replace('/word', '').strip().split(" ")
        res = storage.add_word(*args)

        print(res)

        bot.sendMessage(chat_id, 'The word is added')

    # read next sender's messages
    elif command == '/showall':
        bot.sendMessage(chat_id, str(storage.show_all()))

bot.message_loop(handle)
print ('Listening ...')
# chat shall exist

# Keep the program running.
while 1:
    time.sleep(10)