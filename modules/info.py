from lib.bot import command

class Help(command):

    rule = r' *([A-Za-z]+)?'
    example = '%(nick)s: help list or just @help'

    def run(self, bot, data):
        """List commands or show help on individual commands"""

        name = data.group(1)
        ## show individual help
        if name:
            name = name.lower()
            for cmd in self.modules:
                if name == cmd.name and bot.permission(cmd.limit, data):
                    if cmd.__doc__:
                        bot.private(cmd.__doc__)
                    if not cmd.__doc__ == cmd.example:
                        bot.private(cmd.example)
                else:
                    bot.private("No command with that name")
        ## show all commands
        else:
            names = []
            for cmd in self.modules:
                if cmd.action and bot.permission(cmd.limit, data):
                    bot.log.debug("Listing name of %s: %s" % (cmd, cmd.name))
                    names.append(cmd.name)
            bot.private("Available commands %s" % ", ".join(names))
