from lib.bot import command
import sys, os, re, threading, imp







"""
class kick(command):

    rule = r"(.*)"

    def run(self, bot, data):
        reason = data.group(1)
        if not reason:
            reason = data.origin.nick
        bot.say(reason.strip())
	bot.write(['KICK', '##nick', reason])


class op(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
        if not nick:
            nick = data.origin.nick
        #bot.say(nick.strip())
	channel = data.sender
	#bot.say(channel.strip())
	
	bot.msg('ChanServ', 'OP ' + channel + ' ' + nick)
	
	  
class deop(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
        if not nick:
            nick = data.origin.nick
        bot.say(nick.strip())
	channel = data.sender
	bot.say(channel.strip())	
	bot.msg('ChanServ', 'DEOP ' + channel + ' ' +  nick)

class voice(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
        if not nick:
            nick = data.origin.nick
        #bot.say(nick.strip())
	channel = data.sender
	#bot.say(channel.strip())	
	bot.msg('ChanServ', 'VOICE ' + channel + ' ' + nick)

class deVoice(command):

    rule = r"(.*)"

    def run(self, bot, data):
        nick = data.group(1)
        if not nick:
            nick = data.origin.nick
        #bot.say(nick.strip())
	channel = data.sender
	#bot.say(channel.strip())	
	bot.msg('ChanServ', 'DEVOICE ' + channel + ' ' + nick)"""

class Handlekicks(command):

    regex = r'.*'
    event = ["KICK"]
    action = False
    def run(self, bot, data):
	nick = data.origin.nick
	channel = data.sender

	#if data.nick == bot.nick:
        bot.write(['JOIN'], channel.strip()) 	   



class Join(command):

    rule = r" +(#\S+)(?: *(\S+))?"

    syntax = 'join #channel [key]'
    doc = "Join the specified channel. Optionally a key can be provided."

    ## TODO: can we provide a join message?
    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        channel, key = data.group(1), data.group(2)

        if not key:
            bot.write(['JOIN'], channel.strip())
        else:
            bot.write(['JOIN', channel.strip(), key.strip()])

class Part(command):

    rule = r" +(#{1,}\S+)?"

    syntax = 'part [#channel]'
    doc = " ".join(
        [ "Part the specified channel, or if issued on a channel,"
        , "and no channel specified, part that channel"
        ])

    ## TODO: can we provide a part message?
    def run(self, bot, data):
        channel = data.group(1)
        if not channel and data.sender.startswith('#'):
            channel = data.sender

        bot.write(['PART'], channel)

class Quit(command):

    doc = "Quit the network completely, and shut down. Can only be run by owner"

    ## TODO: can we provide a quit message?
    def run(self, bot, data):
        if data.owner:
            bot.write(['QUIT'])
            __import__('os')._exit(0)

class Say(command):

    rule = r" +(#?\S+) (.+)"

    syntax = "say target text"
    doc = "Message target, which can be either a channel or a user"

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        a, b = data.group(1), data.group(2)
        if a and b:
            bot.msg(a, b)

"""class topic(command):

    rule = r" +(#?\S+) (.+)"

    syntax = "say target text"
    doc = "Message target, which can be either a channel or a user"

    def run(self, bot, data):
        ##if data.sender.startswith('#'):
            ##return
        a, b = data.group(1), data.group(2)
	a = 'ChanServ TOPIC'
        if a and b:
            bot.msg(a, b)"""

class Me(command):

    rule = r" +(#?\S+) (.+)"

    syntax = "me target text"
    doc = "Perform text as an action, either in target channel or a private message to target"

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        msg = '\x01ACTION %s\x01' % data.group(2)
        bot.msg(data.group(1), msg)

class Test(command):

    rule = r"(.*)"

    def run(self, bot, data):
        text = data.group(1)
        if not text:
            text = "Test text"
        bot.say(text.strip())



class Reload(command):

    rule = r""

    doc = "Reload config and modules"

    def run(self, bot, data):
        config = bot.load_module(bot.config.configname, bot.config.configfile)
        bot.config = config
        bot.setup(_reload=True)
        bot.say("Reloaded")

class Lock(command):

    rule = r""
    doc = "Lock nobot dispatch. Only command that can be run is unlock"

    def run(self, bot, data):
        import os
        if data.sender.startswith('#'):
            return
        lockfile = "%s.lock" % os.path.join(bot.config.datadir, bot.config.configname)
        open(lockfile, "w").close()
        bot.say("Dispatch locked")

class Unlock(command):

    rule = r""
    doc = "Unlock nobot dispatch"

    def run(self, bot, data):
        import os
        if data.sender.startswith('#'):
            return
        lockfile = "%s.lock" % os.path.join(bot.config.datadir, bot.config.configname)
        if os.path.exists(lockfile):
            os.remove(lockfile)
        bot.say("Unlocked")





