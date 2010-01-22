from lib.bot import command

class Ping(command):

    rule = ".*"

    def run(self, bot, data):

        bot.reply("ping")
