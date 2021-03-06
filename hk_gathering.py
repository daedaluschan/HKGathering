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

from re import compile
import re
from gathering_util import chkNConv
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
    add_pref = 4


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
        resp_str = ''
        for resp in self.preference:
            if resp:
                resp_str = resp_str + '1'
            else:
                resp_str = resp_str + '0'

        return '[response_obj][' + self.userid.__str__() + '][' + self.display_name + '][' + \
               resp_str + ']'

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
            response_str = response_str + '<' + self.response[each_response].__str__() + '>'
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

    def gen_survey_str(self, response_attached=[]):
        choice_str = u''
        i = 1
        print(self.choices)
        for choice in self.choices:
            if len(response_attached) == 0:
                choice_str = chkNConv(choice_str) + '- ' + chkNConv(choice) + '\n'
            else:
                choice_str = chkNConv(choice_str) + '- /' + i.__str__() + ' ' + chkNConv(choice) + \
                u' -- 你答：'
                if response_attached[i-1]:
                    choice_str = chkNConv(choice_str) + u'Yes\n'
                else:
                    choice_str = chkNConv(choice_str) + u'No\n'
            i = i + 1

        survey_text = u'依家問你：' + chkNConv(self.question) + u'\n\n現有選擇係：\n\n' + chkNConv(choice_str)

        return survey_text

    def gen_start_survey_str(self, poll_id):
        start_link = start_private_url + poll_id
        return u'請用 ' + chkNConv(start_link) + u' \n\n回應問題。或者用 pop up 鍵盤作其他操作。'

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

    def genResponseKeyboard(self, current_response=[]):
        show_keyboard = {'keyboard': [[]]}
        i=0

        if len(current_response) == 0:
            current_response = self.genNullResponse()

        for choice in self.choices:
            if current_response[i]:
                show_keyboard['keyboard'].append(['反對: /' + (i+1).__str__() + ' - ' + choice.encode('utf-8')])
            else:
                show_keyboard['keyboard'].append(['撐: /' + (i+1).__str__() + ' - ' + choice.encode('utf-8')])
            i = i + 1

        show_keyboard['keyboard'].append(['加入新選項'])
        show_keyboard['keyboard'].append(['完'])
        return  show_keyboard

    def get_supporting_count(self, choice):
        support_count = 0
        for each_response in self.response:
            if self.response[each_response].preference[choice]:
                support_count = support_count + 1

        return support_count

    def genResponseStatus(self, poll_id, completd_userid=0):
        status_str = u''
        resp_str =u''
        for idx_choice, choice in enumerate(self.choices):
            resp_str = chkNConv(resp_str) + chkNConv((idx_choice+1).__str__()) + u'. ' + \
                       chkNConv(choice) + u' -- 有 ' + chkNConv(self.get_supporting_count(idx_choice).__str__()) + \
                       u' 個人贊成\n'

        if completd_userid != 0:
            status_str = chkNConv(status_str) + chkNConv(self.response[completd_userid.__str__()].display_name) + \
                         u' 己原成作答，但你仍可以 ' + \
                         chkNConv(start_private_url) + chkNConv(poll_id) + u' 繼續回應。\n\n'

        status_str = chkNConv(status_str) + u'問題係：' + chkNConv(self.question) + u'\n\n' + \
                     u'現在的回應概況：\n\n' + chkNConv(resp_str)

        return status_str

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
        # self._converType = ConverType.nothing

    def get_invited(self, poll_id):
        self._poll = allPoll[poll_id]
        print('Linked poll: ' + self._poll.__str__())
        choice_str = u''
        for choice in self._poll.choices:
            choice_str = choice_str + chkNConv(choice) + '\n'
        ans_link = u'/answer' + u'_' + chkNConv(poll_id)
        show_keyboard = {'keyboard': [[u'查詢回應URL'], [u'統計'], [u'結束提問']]}
        self.sender.sendMessage(text= chkNConv(self._poll.gen_survey_str()) + u'\n' +
                                      self._poll.gen_start_survey_str(poll_id=poll_id),
                                reply_markup=show_keyboard)

    def initiate_survey(self, poll_id, target_id, display_name):
        print('answer to: ' + target_id.__str__())

        if poll_id not in allPoll:
            self.sender.sendMessage(text=u'搵唔返你個問題。好大可能已經完左。')
        else:
            self._poll = allPoll[poll_id]

            if target_id.__str__() not in allPoll[poll_id].response:
                new_response = Response()
                new_response.userid = target_id
                new_response.display_name = chkNConv(display_name)
                new_response.preference = allPoll[poll_id].genNullResponse()
                allPoll[poll_id].response[target_id.__str__()] = new_response
                self._converType = ConverType.response_poll
                self.start_survey(poll_id=poll_id, userid=target_id)

    def start_survey(self, poll_id, userid):
        print('start survey with poll id: ' + poll_id)

        show_keyboard = self._poll.genResponseKeyboard(allPoll[poll_id].response[userid.__str__()].preference)
        self.sender.sendMessage(text=self._poll.gen_survey_str(response_attached=allPoll[poll_id].response[userid.__str__()].preference).encode(encoding='utf-8') +
                                     '\n你可以用 / 〈數字〉更改你對相關選項的回應，用 pop up 鍵盤亦可。\n' +
                                     '或者用 /add_pref 加入新選項。\n\n' +
                                     '當完成時請用 /finish 。',
                                reply_markup=show_keyboard)

    def search_poll_id(self, userid):
        found_poll = 0
        for poll_key in allPoll.keys():
            for each_resp in allPoll[poll_key].response:
                if allPoll[poll_key].response[each_resp].userid == userid:
                    found_poll = poll_key
        return found_poll

    def change_preference(self, poll_id, userid, pref_id):
        print('amend userid: ' + userid.__str__() + ' on preference: ' + pref_id.__str__())
        self._poll.response[userid.__str__()].preference[pref_id - 1] = not self._poll.response[userid.__str__()].preference[pref_id - 1]
        allPoll[poll_id].response[userid.__str__()] = self._poll.response[userid.__str__()]

        self.start_survey(poll_id=poll_id, userid=userid)

    def finish_surey(self, poll_id, completd_userid=0):
        print('completed surevey. responding back to group: ' + self._poll.groupId.__str__())
        self.bot.sendMessage(self._poll.groupId, text=self._poll.genResponseStatus(poll_id=poll_id,
                                                                  completd_userid=completd_userid))
        self.sender.sendMessage(text=u'唔該，你的回應將會反映在 group 裡面。',
                                reply_markup = {'hide_keyboard': True})

    def extract_poll_id_from_chat(self, chat_msg):
        return chat_msg.split(u'https://telegram.me/' + chkNConv(botName) + u'?start=')[1].split(u' ')[0]

    def ask_for_new_pref(self):
        self.sender.sendMessage(text=u'話俾我知你仲有 d 乜野 suggestion。',
                                reply_markup = {'hide_keyboard': True})

    def add_pref(self, poll_id, new_pref, userid):
        print('Add new pref for poll [ ' + poll_id + ' ]. New pref : ' + chkNConv(new_pref))
        allPoll[poll_id].choices.append(new_pref)
        for each_response in allPoll[poll_id].response:
            allPoll[poll_id].response[each_response].preference.append(False)
        self.change_preference(poll_id=poll_id, userid=userid, pref_id=len(allPoll[poll_id].choices))

    def end_poll(self, poll_id, userid):
        if userid == allPoll[poll_id].creatorId:
            print('End Poll: ' + poll_id)
            self.sender.sendMessage(text=u'提問已完結。\n\n' + chkNConv(self._poll.genResponseStatus(poll_id=poll_id)),
                                    reply_markup={'hide_keyboard': True})
            del allPoll[poll_id]
        else:
            self.sender.sendMessage(text=u'唔好意思，只有開 post 者可以結束提問。')

    def find_poll_by_group_id(self, groupid):
        found_poll = 0
        for each_poll in allPoll:
            if allPoll[each_poll].groupId == groupid:
                found_poll = each_poll

        return  found_poll

    def show_keyboad_to_group(self, groupid):
        found_poll = self.find_poll_by_group_id(groupid=groupid)
        if found_poll == 0:
            self.sender.sendMessage(u'搵唔返你個 poll，可能太耐了。')
        else:
            self.get_invited(poll_id=found_poll)

    def suppress_keyboard(self):
        self.sender.sendMessage(text=u'暫時收埋 customized keyboard。可以用 /keyboard 叫返出來。',
                                reply_markup = {'hide_keyboard': True})

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
                        self._poll = Poll()
                        self._converType = ConverType.create_poll
                        self._createPollFlow = CreatePollFlow.poll_question
                        self._poll.creatorId = msg['from']['id']
                        self.sender.sendMessage(text='唔該 send 你個問題俾我。')

                    elif msg['text'] == '/help':
                        self.sender.sendMessage(text='用 /new 黎 create 一個新問題。\n'
                                                #     '或者用 /result 黎查詢回應統計。\n'
                                                )

                    elif re.compile('.*/start\s(\w)+').match(msg['text']) != None:
                        match_obj = re.compile('.*/start\s(\w+)').match(msg['text'])
                        found_poll = match_obj.group(1)
                        self.__uid = found_poll
                        print('start from deep link on poll: ' + found_poll)
                        # self.initiate_survey(poll_id=found_poll, target_id=msg['from']['id'],
                        #                      display_name=msg['from']['first_name'] + ' ' + msg['from']['last_name'])
                        self._converType = ConverType.response_poll
                        self.initiate_survey(poll_id=found_poll, target_id=msg['from']['id'],
                                             display_name=msg['from']['first_name'])
                    else:
                        self.sender.sendMessage(text='唔知你想點，麻煩你再試過。\n' +
                                                     '或者用 /help 睇其他選項。')
                elif self._converType == ConverType.create_poll:
                    if msg['text'] == '/done':
                        self.complte_poll_creation()
                        self._converType = ConverType.nothing
                    elif msg['text'] != '':
                        if self._createPollFlow == CreatePollFlow.poll_question:
                            self._poll.question = msg['text']
                            self._createPollFlow = CreatePollFlow.poll_choice
                            self.sender.sendMessage(text='好，咁你自己有乜意見？')
                        elif self._createPollFlow == CreatePollFlow.poll_choice:
                            self._poll.choices.append(msg['text'])
                            self.sender.sendMessage(text='好，仲有冇？有就繼續 send 下個個選擇。\n' +
                                                         '如果冇就用 /done 完成建立問題。')

                elif self._converType == ConverType.response_poll:
                    found_poll = self.__uid
                    self._poll = allPoll[found_poll]
                    match_obj = re.compile('.*\/(\d+).*').match(msg['text'])
                    if match_obj != None:
                        self.change_preference(poll_id=found_poll,
                                               userid = msg['from']['id'],
                                               pref_id=(int)(match_obj.group(1)))
                    elif msg['text'] == '/finish' or msg['text'].encode(encoding='utf-8') == '完':
                        self.finish_surey(poll_id=found_poll, completd_userid=msg['from']['id'])
                        self._converType = ConverType.nothing
                    elif chkNConv(msg['text']) == u'/add_pref' or chkNConv(msg['text']) == u'加入新選項':
                        self.ask_for_new_pref()
                        self._converType = ConverType.add_pref

                elif self._converType == ConverType.add_pref:
                    found_poll = self.__uid
                    self.add_pref(poll_id=found_poll,
                                  new_pref=chkNConv(msg['text']),
                                  userid = msg['from']['id'])
                    self._converType = ConverType.response_poll

            elif content_type == 'text' and (chat_type == 'group' or chat_type == 'supergroup'):
                if msg['text'].startswith('/start@' + botName):
                    print('invited into group')
                    poll_id = msg['text'].split(' ')[1]
                    self.get_invited(poll_id)
                    allPoll[poll_id].groupId = _chat_id
                elif msg['text'].startswith('/answer_'):
                    poll_id = msg['text'].split('_')[1].split('@')[0]
                    self.initiate_survey(poll_id,
                                         target_id=msg['from']['id'],
                                         display_name=msg['from']['first_name'])
                    #                      display_name=msg['from']['first_name'] + ' ' + msg['from']['last_name'])

                elif chkNConv(msg['text']) == u'查詢回應URL':
                    poll_id = self.extract_poll_id_from_chat(msg['reply_to_message']['text'])
                    self._poll = allPoll[poll_id]
                    self.sender.sendMessage(text=u'回應URL：' + chkNConv(start_private_url + poll_id) + u' ')
                elif chkNConv(msg['text']) == u'統計':
                    poll_id = self.extract_poll_id_from_chat(msg['reply_to_message']['text'])
                    self._poll = allPoll[poll_id]
                    self.sender.sendMessage(text=self._poll.genResponseStatus(poll_id))
                elif chkNConv(msg['text']) == u'結束提問':
                    poll_id = self.extract_poll_id_from_chat(msg['reply_to_message']['text'])
                    self._poll = allPoll[poll_id]
                    self.end_poll(poll_id=poll_id, userid=msg['from']['id'])
                elif msg['text'].startswith('/keyboard'):
                    self.show_keyboad_to_group(_chat_id)
                elif msg['text'].startswith('/timeout'):
                    self.suppress_keyboard()


            print('Poll:' + self._poll.__str__())
        else:
            raise telepot.BadFlavor(msg)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(HKGathering, timeout=600)), ])
print('Listening ...')
bot.notifyOnMessage(run_forever=True)
