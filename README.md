# HKGathering

This is a telegram bot used to collect preference from different group chat attendees and come to a commonly agreed proposal. It works like a poll bot, except:

* It is in Traditional Chinese (正體中文)
* People have the flexibility to vote on multiple choice
* People can add new preference on a poll
* Creating poll and individual polling happen in PM mode (private message). So won't cause too much disturb to the group chat.

## How to run: 
* clone the package into your own cloud hosting environment. (Assuming a python 2.7 enabled environment)
* There should only be 2 dependent module - telepot and enum. You may use 'pip install -r requirements.txt' to install both in 1-go.
* Register your new bot via Telegram [botfather](https://telegram.me/BotFather). 
* update in the code \( _hk\_gathering.py_ \) the name of your bot: **_botName = 'yourBot_bot'_**
* Run it \! The command is \: **python hk\_gathering.py "your bot token"**

## How to use: 

I am hosting an instance of this bot and it can be found on Telegram by searching "@HKGathering". 

* To create a new poll, talk to the bot in private message and use the /new option.
* Follow the instruction and provide the content of the question and choices you might have.
* The bot will then generate an URL which you can use to place the poll into a group chat.
* Each individual to join the poll by via the other URL being broadcast in the group chat, which will launch a PM for the user to continue the poll.
* Everyone can query the current poll result by only the poll creator can end the poll.


## Library used: 

* [Telepot](https://github.com/nickoala/telepot) as the Telegram bot library
