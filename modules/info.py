from lib.bot import command

class Help(command):
    """List commands or show help on individual commands"""

    rule = r' *([A-Za-z]+)?'
    example = '%(nick)s: help list or just @help'

    def run(self, bot, data):

        name = data.group(1)
        if name:
            ## show individual help
            name = name.lower()
            for cmd in self.modules:
                if name == cmd._name_:
                    if bot.access(data.origin, cmd):
                        if not hasattr(cmd, '_doc_') and cmd.__doc__:
                            cmd._doc_ = bot.interpolate(cmd.__doc__, cmd)
                        if hasattr(cmd, '_doc_'):
                            bot.private(cmd._doc_)
                        if not hasattr(cmd, '_example_') and cmd.example:
                            cmd._example_ = bot.interpolate(cmd.example, cmd)
                        if hasattr(cmd, '_example_'):
                            bot.private(cmd._example_)
                    else:
                        bot.private("No command with that name")
        else:
            ## show all commands
            names = []
            for cmd in self.modules:
                if cmd.action and bot.access(data.origin, cmd):
                    names.append(cmd._name_)
            bot.private("Available commands: %s" % ", ".join(names))

