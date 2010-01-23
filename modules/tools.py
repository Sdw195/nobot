from lib.bot import command

class Ping(command):

    rule = ".*"
    doc = "Pong yourself"

    def run(self, bot, data):
        bot.reply("pong")
