__author__ = 'daedaluschan'

# importing libraries


import sys, time
import telepot
from telepot.delegate import per_chat_id, create_open

from datetime import date
from types import *
from enum import Enum

# Constants

start_group_url = 'https://telegram.me/HKGathering_bot?startgroup=test'

# Defining enums


class ConverType(Enum):
    nothing=1
    create_poll=2

class CreatePollFlow(Enum):
    not_start=1
    poll_question=2
    poll_choice=3


# Poll data structure


class Poll():
    def __init__(self):
        self._question = ''
        self._choices = []

    def __str__(self):
        choice_str = ''
        for each_choice in self._choices:
            choice_str = choice_str + ' - ' + each_choice
        return  'question: ' + self._question + '; choice: ' + choice_str


# main class of message handling


class HKGathering(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(HKGathering, self).__init__(seed_tuple, timeout)
        print('constructor is being called')
        self._converType = ConverType.nothing
        self._createPollFlow = CreatePollFlow.not_start
        self._poll = Poll()

    def on_message(self, msg):
        print('on_message() is being called')
        flavor = telepot.flavor(msg)

        # normal message
        if flavor == 'normal':
            content_type, chat_type, _chat_id = telepot.glance2(msg)
            print('Normal Message:', content_type, chat_type, _chat_id, '; message content: ', msg)

            if self._converType == ConverType.nothing:

                if msg['text'] == '/start':
                    self.sender.sendMessage(text='今日的日期係：' + str(date.today()) + '. \n' +
                                                 'User /new to create new poll. Or,' +
                                                 'use /help for more options')
                elif msg['text'] == '/new':
                    self._converType = ConverType.create_poll
                    self._createPollFlow = CreatePollFlow.poll_question
                    self.sender.sendMessage(text='Please send me over the question you want to ask.')

                elif msg['text'] == '/help':
                    self.sender.sendMessage(text='/new - create new poll. \n' +
                                                 '/result - for query on the latest result \n')
                else:
                    self.sender.sendMessage(text='I don\'t understand what you are saying !\n' +
                                                 'Try again ! Or use /help for assistance.')
            elif self._converType == ConverType.create_poll :
                if msg['text'] == '/done':
                    self.sender.sendMessage(text='Thank You!')
                elif msg['text'] != '':
                    if self._createPollFlow == CreatePollFlow.poll_question:
                        self._poll._question = msg['text']
                        self._createPollFlow = CreatePollFlow.poll_choice
                        self.sender.sendMessage(text='Please give me your preference')
                    elif self._createPollFlow == CreatePollFlow.poll_choice:
                        self._poll._choices.append(msg['text'])
                        self.sender.sendMessage(text='Please give me your next preference, if any.\n' +
                                                     'use /done to complete creating your poll.')

        else:
            raise telepot.BadFlavor(msg)

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(HKGathering, timeout=20)),])
print('Listening ...')
bot.notifyOnMessage(run_forever=True)
