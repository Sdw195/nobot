from lib.bot import command

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

    rule = r" *(#{1,}\S+)?"

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

