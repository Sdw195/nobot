from lib.bot import command

class Help(command):

    rule = r' *([A-Za-z]+)?'
    syntax = 'help [command]'
    example = "help help"
    doc = " ".join(
        [ "List all commands or help on an individual command. Commands can"
        , "be prefixed with '%(prefix)s', eg.: `%(prefix)shelp help' or placed"
        , "immediately after the bot's nick, eg.: `%(nick)s: help'"
        ])

    def run(self, bot, data):

        name = data.group(1)
        if name:
            ## show individual help
            name = name.lower()
            for cmd in self.modules:
                if name == cmd._name_:
                    if bot.access(data.origin, cmd):
                        if not hasattr(cmd, '_syntax_') and cmd.syntax:
                            cmd._syntax_ = bot.interpolate(cmd.syntax, cmd)
                        if hasattr(cmd, '_syntax_'):
                            bot.private("Syntax: %s" % cmd._syntax_)
                        if not hasattr(cmd, '_example_') and cmd.example:
                            cmd._example_ = bot.interpolate(cmd.example, cmd)
                        if hasattr(cmd, '_example_'):
                            bot.private("Example: %s" % cmd._example_)
                        if not hasattr(cmd, '_doc_') and cmd.doc:
                            cmd._doc_ = bot.interpolate(cmd.doc, cmd)
                        if hasattr(cmd, '_doc_'):
                            bot.private(cmd._doc_)
                    else:
                        bot.private("Unknown command")
        else:
            ## show all commands
            names = []
            for cmd in self.modules:
                if cmd.action and bot.access(data.origin, cmd):
                    names.append(cmd._name_)
            bot.private("Commands: %s" % ", ".join(names))
