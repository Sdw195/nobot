from lib.bot import command

class Join(command):
    """Join the specified channel. This is an admin-only command."""

    rule = r" +(#\S+)(?: *(\S+))?"
    example = '%(prefix)sjoin #example or %(prefix)sjoin #example key'

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
            channel, key = data.group(1), data.group(2)

            if not key:
                bot.write(['JOIN'], channel.strip())
            else:
                bot.write(['JOIN', channel.strip(), key.strip()])

class Part(command):

    rule = r" *(#{1,}\S+)?"
    example = '%(prefix)spart #example'

    def run(self, bot, data):
        if data.admin:
            channel = data.group(1)
            if not channel and data.sender.startswith('#'):
                channel = data.sender
            channel = channel.strip()

            bot.write(['PART'], channel)

class Quit(command):

    def run(self, bot, data):
        if data.owner:
            bot.write(['QUIT'])
            __import__('os')._exit(0)

class Say(command):

    rule = r" +(#?\S+) (.+)"

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        a, b = data.group(1), data.group(2)
        if a and b and data.admin:
            bot.msg(a, b)

class Me(command):

    rule = r" +(#?\S+) (.+)"

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
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
    """Reloads modules and config"""

    rule = r""

    def run(self, bot, data):
        if data.admin:
            config = bot.load_module(bot.config.configname, bot.config.configfile)
            bot.config = config
            bot.setup(_reload=True)
            bot.private("Reloaded")

