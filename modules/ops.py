from lib.bot import command

import lib.irc as irc
import random 
import datetime

auth = []
#put admin nicks in power1
admin = ['me', 'myself', 'I']


class iam (command):


    rule = r"\s+(\S+)\s+(\S+)"
    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
        text = data.group(1)
	password = data.group(2)	
        if not text:
            text = data.origin.nick
	
	if not data.nick in admin:
	    text = 'i do not know who you are ' + data.origin.nick
	    bot.say(text.strip())
	    return
	if data.nick in auth:
	    text = 'i already now you as ' + data.origin.nick
	    bot.say(text.strip())
	    return

	if text == data.origin.nick:
	   if password == "password":
		power.append(text)
	        text = 'i now know you as ' + data.group(1) 
                bot.say(text.strip())
	   else:
	        text = 'error wrong passowrd' 
                bot.say(text.strip())	   	


	else:
	   text = 'you are not ' + data.group(1) + ' you are ' + data.origin.nick
	   bot.say(text.strip())

class iamnot (command):

    rule = " +(\S+)"

    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
        text = data.group(1)	
        if not text:
            text = data.origin.nick
        if data.nick in auth:
	    a = auth.index(text)
	    del(auth[a])
	text = 'i do not know you as ' + data.group(1) + ' anymore'
        bot.say(text.strip())


class whoami (command):

    rule = r"(.*)"


    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
        text = data.group(1)	
        if not text:
            text = data.origin.nick
	
	if not data.nick in auth:
	    text = "I don't know who you are, you should ask yourself"
	    bot.say(text.strip())
	    return
	if data.nick in auth:
	    text = 'You are ' + data.origin.nick
	    bot.say(text.strip())
	    return

	


class HandleOps(command):
    regex = r'.*'
    event = ["PART", "JOIN", "QUIT"]
    action = False
    def run(self, bot, data):
	text = data.nick
        if data.nick in auth:
	    a = auth.index(text)
	    del(auth[a])


class kick(command):

    rule = r"(.*)"

    def run(self, bot, data):
        reason = data.group(1)
        if not reason:
            reason = data.origin.nick
	if data.nick in auth:
	   bot.write(['KICK', '##nick', reason])
	else:
	  bot.msg( nick , 'you cant do that please tell me who you are and try agian')

class op(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
	nick1 = data.origin.nick
        if not nick:
            nick = data.origin.nick
	channel = data.sender
	if data.nick in auth:	
	   bot.msg('ChanServ', 'OP ' + channel + ' ' + nick)
	else:
	  bot.msg( nick1 , 'you cant do that please tell me who you are and try agian')


	
	  
class deop(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
	nick1 = data.origin.nick
        if not nick:
            nick = data.origin.nick
	channel = data.sender
	if data.nick in auth:	
	   bot.msg('ChanServ', 'DEOP ' + channel + ' ' + nick)
	else:
	  bot.msg( nick1 , 'you cant do that please tell me who you are and try agian')


class voice(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
	nick1 = data.origin.nick
        if not nick:
            nick = data.origin.nick
	channel = data.sender	
	if data.nick in auth:	
	   bot.msg('ChanServ', 'VOICE ' + channel + ' ' + nick)
	else:
	  bot.msg( nick1 , 'you cant do that please tell me who you are and try agian')


class deVoice(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
	nick1 = data.origin.nick
        if not nick:
            nick = data.origin.nick
	channel = data.sender	
	if data.nick in auth:	
	   bot.msg('ChanServ', 'DEVOICE ' + channel + ' ' + nick)
	else:
	  bot.msg( nick1 , 'you cant do that please tell me who you are and try agian')


