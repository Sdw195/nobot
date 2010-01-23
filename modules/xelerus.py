from lib.bot import command
import lib.web as web

class Func(command):

    regex = r".*(?:%(cmd)s\s+(\w+)|(f#\w+)).*"
    triggers = [r"(?=f#\w+)"]
    syntax = 'func search | f#search'
    example = "Have a look at f#itmSetData"
    doc = " ".join(
        [ "Search xelerus' function list for a matching function,"
        "and return a list if we have multiple results. If there is"
        "an exact match, a short syntax will be printed and an url for more details"
        ])

    def run(self, bot, data):

        ## TODO: handle results that are too long
        fun = None
        if data.group(1):
            fun = data.group(1)
        elif data.group(2):
            fun = data.group(2)[2:]

        bot.log.debug(fun)

        if fun:
            ## if we are searching for too small a string, complain
            if len(fun) < 3:
                return bot.say("Search term too broad, please refine it")

            fun = web.quote(fun.encode('utf-8'))
            res = web.get("http://xelerus.de/doc_function_raw.php?search=%s" % fun)
            rows = res.splitlines()
            if len(rows) > 1:
                funcs = []
                for row in rows:
                    id, name, syntax = row.split("|")
                    funcs.append(name)
                return bot.say(", ".join(funcs))
            elif len(rows) == 1:
                id, name, syntax = rows[0].split("|")
                return bot.say("%s - http://xelerus.de/index.php?s=functions&function=%s" % (syntax, id))
            else:
                return bot.say("No results found")


