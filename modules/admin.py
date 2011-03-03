from lib.bot import command
import sys, os, re, threading, imp









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




class still_alive(command):

    rule = r"(.*)"

    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
	text = 'This was a triumph. Im making a note here: HUGE SUCCESS. Its hard to overstate my satisfaction. Aperture  Science: We do what we must because we can. For the good of all of us Except the ones who are dead. But theres no sense crying over every mistake You just keep on trying till you run out of cake And the science gets done and you make a neat gun For the people who are still alive. Im not even angry. Im being so sincere right now.'
	text2 = 'Even though you broke my heart and killed me. And tore me to pieces. And threw every piece into a fire. As they burned it hurt because I was so happy for you. Now these points of data make a beautiful line And were out of beta were releasing on time. So Im GLaD I got burned think of all the things we learned For the people who are still alive. Go ahead and leave me. I think I prefer to stay inside. Maybe youll find someone else to help you.'
	text3 = 'Maybe Black Mesa -THAT WAS A JOKE. HA HA, FAT CHANCE. Anyway, this cake is great: Its so delicious and moist. Look at me still talking when theres science to do. When I look out there it makes me GLaD Im not you. Ive experiments to run there is research to be done On the people who are still alive And believe me I am still alive. Im doing science and Im still alive. I feel FANTASTIC and Im still alive. While youre dying Ill be still alive.'
	text4 = 'And when youre dead I will be still alive.' 
	text5 = 'Still alive'
	text6 = 'Still alive'	
        bot.say(text.strip())
	bot.say(text2.strip())
	bot.say(text3.strip())
	bot.say(text4.strip())
	bot.say(text5.strip())
	bot.say(text6.strip())
