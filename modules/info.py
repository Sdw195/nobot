from lib.bot import __command__

class List(__command__):

    def run(self, bot, data):
        # This function only works in private message
        if data.sender.startswith('#'):
            return
        names = []
        for cmd in self.modules:
            if cmd.action:
                names.append(cmd.name)
        bot.private(", ".join(names))

class Help(__command__):

    rule = r' +([A-Za-z]+)'
    example = '%(nick)s: help list'

    def run(self, bot, data):
        """Shows a command's documentation, and possibly an example."""

        name = data.group(1).lower()
        bot.log.debug("Help %s" % name)

        for cmd in self.modules:
            if name == cmd.name:
                if cmd.__doc__:
                    bot.private(cmd.__doc__)
                if not cmd.__doc__ == cmd.example:
                    bot.private(cmd.example)
