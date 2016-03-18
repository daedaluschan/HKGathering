# coding=UTF8
__author__ = 'daedaluschan'

# importing libraries


import sys, time
import telepot
from telepot.delegate import per_chat_id, create_open

from datetime import date
from types import *
from enum import Enum
import uuid

# Constants & globa data

allPoll = {}
botName = 'HKGathering_bot'
start_group_url = 'https://telegram.me/' + botName + '?startgroup='

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
        self.question = ''
        self.creatorId = 0
        self.choices = []

    def __str__(self):
        choice_str = ''
        for each_choice in self.choices:
            choice_str = choice_str + ' - ' + each_choice
        return  'question: ' + self._question + '; choice: ' + choice_str

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, value):
        self._question = value

    @property
    def creatorId(self):
        return  self._creatorId

    @creatorId.setter
    def creatorId(self, value):
        self._creatorId = value

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, value):
        self._choices = value


# main class of message handling


class HKGathering(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(HKGathering, self).__init__(seed_tuple, timeout)
        print('constructor is being called')
        self._converType = ConverType.nothing
        self._createPollFlow = CreatePollFlow.not_start
        self.__uid = ''
        self._poll = Poll()

    def complte_poll_creation(self):
        self.__uid = uuid.uuid4().hex
        allPoll[self.__uid] = self._poll
        self.sender.sendMessage(text='用呢條 link 將問題放落 chat group 裡邊：\n' +
                                     start_group_url + self.__uid)

    def get_invited(self, inviterId):
        for poll in allPoll:
            if poll.creatorId == inviterId:
                self._poll = poll
        self.sender.sendMessage(text='依家問你：' + self._poll.question + '\n' +
                                     '請用 /start@' + botName + '回應問題。')

    def on_message(self, msg):
        print('on_message() is being called')
        flavor = telepot.flavor(msg)

        print('flavor: ' + flavor)

        # normal message
        if flavor == 'normal':
            content_type, chat_type, _chat_id = telepot.glance2(msg)
            print('Normal Message:', content_type, chat_type, _chat_id, '; message content: ', msg)

            if chat_type == 'private':

                if self._converType == ConverType.nothing:

                    if msg['text'] == '/start':
                        self.sender.sendMessage(text='今日的日期係：' + str(date.today()) + '. \n' +
                                                     '用 /new 黎 create 一個新問題，' +
                                                     '或者用 /help 睇其他選項。')
                    elif msg['text'] == '/new':
                        self._converType = ConverType.create_poll
                        self._createPollFlow = CreatePollFlow.poll_question
                        self._poll.creatorId = msg['from']['id']
                        self.sender.sendMessage(text='唔該 send 你個問題俾我。')

                    elif msg['text'] == '/help':
                        self.sender.sendMessage(text='用 /new 黎 create 一個新問題，\n' +
                                                     '或者用 /result 黎查詢回應統計。\n')
                    else:
                        self.sender.sendMessage(text='唔知你想點，麻煩你再試過。\n' +
                                                     '或者用 /help 睇其他選項。')
                elif self._converType == ConverType.create_poll :
                    if msg['text'] == '/done':
                        self.complte_poll_creation()
                    elif msg['text'] != '':
                        if self._createPollFlow == CreatePollFlow.poll_question:
                            self._poll.question = msg['text']
                            self._createPollFlow = CreatePollFlow.poll_choice
                            self.sender.sendMessage(text='好，咁你自己有乜意見？')
                        elif self._createPollFlow == CreatePollFlow.poll_choice:
                            self._poll.choices.append(msg['text'])
                            self.sender.sendMessage(text='好，仲有冇？有就繼續 send 下個個選擇。\n' +
                                                         '如果冇就用 /done 完成建立問題。')

            elif chat_type == 'new_chat_participant':
                print('invited into group')
                inviterId = msg['from']['id']
                self.get_invited(inviterId)


            print('Poll:' + self._poll.__str__())
        else:
            raise telepot.BadFlavor(msg)

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(HKGathering, timeout=20)),])
print('Listening ...')
bot.notifyOnMessage(run_forever=True)
