import telepot
from pprint import pprint

import time

bot = telepot.Bot('TOKEN')
print(bot.getMe())
# need to monitor the offset :(
# response = bot.getUpdates()
# pprint(response)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    if content_type == 'text':
        bot.sendMessage(chat_id, msg['text'])

bot.message_loop(handle)
print ('Listening ...')
# chat shall exist

# Keep the program running.
while 1:
    time.sleep(10)