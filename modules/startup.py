from lib.bot import __command__

class Startup(__command__):

    regex = r'.*'
    event = '251'
    action = False

    def run(self, bot, data):
        if hasattr(bot.config, 'serverpass'):
            bot.write(('PASS', bot.config.serverpass))

        if hasattr(bot.config, 'password'):
            bot.msg('NickServ', 'IDENTIFY %s' % bot.config.password)
            __import__('time').sleep(5)

        for channel in bot.channels:
            bot.write(('JOIN', channel))
