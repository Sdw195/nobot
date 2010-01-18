from lib.bot import command

class Join(command):
    """Join the specified channel. This is an admin-only command."""

    rule = r" +(#\S+)(?: *(\S+))?"
    example = '%(prefix)sjoin #example or %(prefix)sjoin #example key'
    limit = ['admin']

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
            channel, key = data.group(1), data.group(2)

            if not key:
                bot.write(['JOIN'], channel)
            else:
                bot.write(['JOIN', channel, key])

class Part(command):

    example = '%(prefix)spart #example'
    limit = ['admin']

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
            bot.write(['PART'], data.group(1))

class Quit(command):

    limit = ['admin']

    def run(self, bot, data):
        if input.sender.startswith('#'):
            return
        if input.owner:
            bot.write(['QUIT'])
            __import__('os')._exit(0)

class Say(command):

    rule = r" +(#?\S+) (.+)"
    limit = ['admin']

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        a, b = data.group(1), data.group(2)
        if a and b and data.admin:
            bot.msg(a, b)

class Me(command):

    rule = r" +(#?\S+) (.+)"
    limit = ['admin']

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
            msg = '\x01ACTION %s\x01' % data.group(2)
            bot.msg(data.group(1), msg)

class Reload(command):
    """Reloads modules and config"""

    rule = r""
    limit = ['admin']

    def run(self, bot, data):
        if data.admin:
            config = bot.load_module(bot.config.configname, bot.config.configfile)
            bot.config = config
            bot.setup(_reload=True)
            bot.private("Reloaded")

