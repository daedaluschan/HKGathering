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

from types import  *

# Constants & global data

allPoll = {}
botName = 'HKGathering_bot'
start_private_url = 'https://telegram.me/' + botName + '?start='
start_group_url = 'https://telegram.me/' + botName + '?startgroup='


# Defining enums


class ConverType(Enum):
    nothing = 1
    create_poll = 2
    response_poll = 3


class CreatePollFlow(Enum):
    not_start = 1
    poll_question = 2
    poll_choice = 3


# Response data structure

class Response():
    def __init__(self):
        self.userid = 0
        self.display_name = ''
        self.preference = []

    def __str__(self):
        return '[response_obj][' + self.userid.__str__() + '][' + self.display_name + '][' + \
               len(self.preference).__str__() + ']'

    @property
    def userid(self):
        return self._userid

    @userid.setter
    def userid(self, value):
        self._userid = value

    @property
    def preference(self):
        return self._preference

    @preference.setter
    def preference(self, value):
        self._preference = value

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

# Poll data structure


class Poll():
    def __init__(self):
        self.question = ''
        self.creatorId = 0
        self.choices = []
        self.groupId = 0
        self.response = {}

    def __str__(self):
        choice_str = ''
        response_str = ''
        for each_choice in self.choices:
            choice_str = choice_str + ' - ' + each_choice
        for each_response in self.response:
            response_str = response_str + '<' + each_response + '>'
        return '[Poll_obj][question: ' + self.question + '][choice: ' + choice_str + '][group: ' + \
               self.groupId.__str__() + '][all_resp: ' + response_str + ']'

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, value):
        self._question = value

    @property
    def creatorId(self):
        return self._creatorId

    @creatorId.setter
    def creatorId(self, value):
        self._creatorId = value

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, value):
        self._choices = value

    @property
    def groupId(self):
        return self._groupId

    @groupId.setter
    def groupId(self, value):
        self._groupId = value

    @property
    def survey_str(self, response_attached=[]):
        choice_str = ''
        i = 1
        for choice in self.choices:
            if len(response_attached) == 0:
                choice_str = choice_str + '- ' + choice.encode('utf-8') + '\n'
            else:
                choice_str = choice_str + '- /' + i.__str__() + ' ' + choice.encode('utf-8') + \
                ' -- 現在回應：' + 'Yes' if response_attached[i-1] else 'No' +' \n'
            i += 1

        survey_text = '依家問你：' + self.question.encode('utf-8') + '\n\n' + '現有選擇係：\n\n' + choice_str + '\n'

        return survey_text

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    def genNullResponse(self):
        preference_vector = []
        for each_choice in self.choices:
            preference_vector.append(False)
        return preference_vector


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
        self._converType = ConverType.nothing

    def get_invited(self, poll_id):
        self._poll = allPoll[poll_id]
        print('Linked poll: ' + self._poll.__str__())
        choice_str = ''
        for choice in self._poll.choices:
            choice_str = choice_str + choice.encode('utf-8') + '\n'
        ans_link = '/answer' +'_' + poll_id.encode(encoding='utf-8')
        show_keyboard = {'keyboard': [['開始回應']]}

        self.sender.sendMessage(text=self._poll.survey_str + '\n' +
                                     '請用 ' + ans_link +  ' 回應問題。\n' +
                                     '或者用 pop up 鍵盤開始回應。',
                                reply_markup=show_keyboard)

    def initiate_survey(self, poll_id, target_id, display_name):
        print('answer to: ' + target_id.__str__())
        new_response = Response()
        new_response.userid = target_id
        new_response.display_name = display_name
        new_response.preference = allPoll[poll_id].genNullResponse()
        allPoll[poll_id].response[target_id.__str__()] = new_response
        # allPoll[poll_id].response.append({target_id.__str__(): new_response})


        print ('new_response: ' + new_response.__str__())
        print ('saved resposne: ' + allPoll[poll_id].response[target_id.__str__()].__str__())

        show_keyboard = {'keyboard': [['開始']]}
        self.bot.sendMessage(target_id,
                             text=self._poll.survey_str + '\n' +
                                  '請用 /begin 或者用 pop up 鍵盤開始。',
                             reply_markup=show_keyboard)

    def start_survey(self, poll_id, userid):
        print('start survey with poll id: ' + poll_id)
        self._poll = allPoll[poll_id]
        self.sender.sendMessage(text=self._poll.survey_str(response_attached=allPoll[poll_id].response[userid.__str__()]) +
                                     '\n' + '或者用 /add_pref 加入新選項。')

    def on_message(self, msg):
        print('on_message() is being called')
        print('==== all poll in cache ====')
        if len(allPoll) == 0:
            print('No poll yet')
        else:
            for each_poll in allPoll:
                print(allPoll[each_poll].__str__())
        print('========== END ============')
        flavor = telepot.flavor(msg)

        print('flavor: ' + flavor)

        # normal message
        if flavor == 'normal':
            content_type, chat_type, _chat_id = telepot.glance2(msg)
            print('Normal Message:', content_type, chat_type, _chat_id, '; message content: ', msg)

            if content_type == 'text' and chat_type == 'private':

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

                    elif msg['text'].encode(encoding='utf-8') == '開始' or msg['text'].startswith('/begin'):
                        found_poll = 0
                        for poll_key in allPoll.keys():
                            print ('in_all_poll: ' + allPoll[poll_key].__str__())
                            for each_resp in allPoll[poll_key].response:
                                print('each_resp: ' + each_resp.__str__())
                                if each_resp.userid == msg['from']['id']:
                                    found_poll = poll_key
                        if found_poll != 0:
                            self._converType = ConverType.response_poll
                            self.start_survey(found_poll, msg['from']['id'])
                        else:
                            self.sender.sendMessage(text='搵唔到你的問題。')
                    else:
                        self.sender.sendMessage(text='唔知你想點，麻煩你再試過。\n' +
                                                     '或者用 /help 睇其他選項。')
                elif self._converType == ConverType.create_poll:
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

            elif content_type == 'text' and chat_type == 'group':
                if msg['text'].startswith('/start@' + botName):
                    print('invited into group')
                    poll_id = msg['text'].split(' ')[1]
                    self.get_invited(poll_id)
                    allPoll[poll_id].groupId = _chat_id
                elif msg['text'].startswith('/answer_'):
                    poll_id = msg['text'].split('_')[1].split('@')[0]
                    self.initiate_survey(poll_id,
                                         target_id=msg['from']['id'],
                                         display_name=msg['from']['first_name'] + ' ' + msg['from']['last_name'])
                elif msg['text'].encode(encoding='utf-8') == '開始回應':
                    orig_text = msg['reply_to_message']['text']
                    poll_id = orig_text.split('/answer_')[1].split(' ')[0]
                    self.initiate_survey(poll_id,
                                         target_id=msg['from']['id'],
                                         display_name=msg['from']['first_name'] + ' ' + msg['from']['last_name'])

            print('Poll:' + self._poll.__str__())
        else:
            raise telepot.BadFlavor(msg)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(HKGathering, timeout=20)), ])
print('Listening ...')
bot.notifyOnMessage(run_forever=True)
