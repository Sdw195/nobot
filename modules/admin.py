from lib.bot import __command__

class Join(__command__):
    """Join the specified channel. This is an admin-only command."""

    rule = r" +(#\S+)(?: *(\S+))?"
    example = '%(prefix)sjoin #example or %(prefix)sjoin #example key'

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
            channel, key = data.group(1), data.group(2)
            if not key:
                bot.write(['JOIN'], channel)
            else:
                bot.write(['JOIN', channel, key])

class Part(__command__):

    example = '%(prefix)spart #example'

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
            bot.write(['PART'], data.group(1))

class Quit(__command__):

    def run(self, bot, data):
        if input.sender.startswith('#'):
            return
        if input.owner:
            bot.write(['QUIT'])
            __import__('os')._exit(0)

class Msg(__command__):

    rule = r" +(#?\S+) (.+)"

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        a, b = data.group(1), data.group(2)
        if a and b and data.admin:
            bot.msg(a, b)

class Me(__command__):

    rule = r" +(#?\S+) (.+)"

    def run(self, bot, data):
        if data.sender.startswith('#'):
            return
        if data.admin:
            msg = '\x01ACTION %s\x01' % data.group(2)
            bot.msg(data.group(1), msg)
