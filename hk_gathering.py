__author__ = 'daedaluschan'

import sys, time
import telepot
from telepot.delegate import per_chat_id, create_open

from datetime import date
from types import *


class HKGathering(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(HKGathering, self).__init__(seed_tuple, timeout)
        print('constructor is being called')

    def on_message(self, msg):
        print('on_message() is being called')
        flavor = telepot.flavor(msg)

        # normal message
        if flavor == 'normal':
            content_type, chat_type, _chat_id = telepot.glance2(msg)
            print('Normal Message:', content_type, chat_type, _chat_id, '; message content: ', msg)

            if msg['text'] == '/start' or msg['text'] == '/today':
                self.sender.sendMessage(text='Today is ' + str(date.today()) + '. \n' +
                                                       'Use /help for more options')
            elif msg['text'] == '/help':
                self.sender.sendMessage(text='/today - get today\'s date and my day count. \n' +
                                                       '/help - for those who have bad memory. \n' +
                                                       '/query - check my day count for a particular date. \n')
            else:
                self.sender.sendMessage(text='I don\'t understand what you are saying !\n' +
                                                       'Try again ! Or use /help for assistance.')
        else:
            raise telepot.BadFlavor(msg)

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(HKGathering, timeout=60)),])
print('Listening ...')
bot.notifyOnMessage(run_forever=True)
