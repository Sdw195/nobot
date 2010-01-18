from lib.bot import command
from lib.tools import Database

import os, re, datetime, time, sqlite3

class FactsDB(Database):

    def create_structure(self):
        c = self.con.cursor()
        c.execute("""
            CREATE TABLE fact_index (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE ON CONFLICT IGNORE
            )""")
        c.execute("""
            CREATE TABLE facts (
                id INTEGER PRIMARY KEY,
                key_id INTEGER,
                fact TEXT,
                created_at TIMESTAMP,
                created_by TEXT
            )""")
        self.con.commit()

    def lookup(self, key, index=None):
        pass

    ## TODO: implement handling of `index'
    def learn(self, key, fact, author, index=None):
        c = self.con.cursor()
        ## see if we already have a matching key
        c.execute("SELECT id FROM fact_index WHERE key = ?", (key,))
        kid = c.fetchone()
        if kid:
            kid = kid[0]
        ## if we found none, add a new row
        if not kid:
            c.execute("INSERT INTO fact_index (key) VALUES (?)", (key,))
            self.con.commit()
            kid = c.lastrowid
        ## now we have id key id
        ## check if it would be a duplicate row
        c.execute("SELECT * FROM facts WHERE key_id = ? AND fact = ?", (kid, fact))
        found = c.fetchone()

        if found:
            raise RuntimeError("Duplicate fact for key")
        else:
            c.execute("""INSERT INTO
                facts (key_id, fact, created_at, created_by) VALUES (?, ?, ?, ?)
                """, (kid, fact, time.time(), author))
            self.con.commit()

    def lookup(self, key, index):
        self.bot.log.debug("Lookup: %s %s" % (key, type(index)))
        key = "%%%s%%" % key
        c = self.con.cursor()
        c.execute("""SELECT * FROM facts, fact_index WHERE fact_index.key LIKE ?
                  AND facts.key_id = fact_index.id""", [key])
        res = c.fetchall()
        self.bot.log.debug(res)

        if not res:
            raise RuntimeError("No results found")

        if index is None:
            index = 1

        try:
            fact = res[int(index) - 1]
        except IndexError:
            raise RuntimeError("Index out of range")

        count = len(res)
        created = fact[3]
        fact = "%s[%s/%s]: %s" % (fact[6], index, count, fact[2])
        return (fact, created)


class Fact(command):

    rule = r"(.*)"

    def run(self, bot, data):
        self.bot = bot
        self.data = data

        # self.commands = ["lookup", "search", "learn", "forget", "help"]
        self.commands = ["lookup", "learn", "help"]

        self.factdb = FactsDB(bot)
        text = data.group(1)

        ## run a regex on the command to see where we 
        ## want to dispatch too
        regex = re.compile(r' +(\S+)(.*)')
        match = regex.match(text)

        if match:
            key = match.group(1)

            if hasattr(self, key):
                ## if we have an method that matches key,
                ## then we call a sub action
                getattr(self, key)(match.group(2))
            else:
                ## we have no method with the given name,
                ## pass the data on to lookup
                self.lookup(text)
        else:
            self.help("")

    def learn(self, text):
        """Learn a new keyword. Key and value are separated by a full stop"""

        regex = re.compile(r" *(.*?)\.(?:\[(\d+)\])?(?: +(.*))")
        match = regex.match(text)
        try:
            if match:
                author = self.data.nick
                key = match.group(1)
                index = match.group(2)
                fact = match.group(3)
                if not key or not fact:
                    raise SyntaxError("Key or Value is missing")
                key = key.strip()
                fact = fact.strip()
                self.factdb.learn(key, fact, author, index)
                self.bot.reply("Learned fact")
            else:
                raise SyntaxError("Failed to parse. See help for example")

        except SyntaxError, e:
            self.bot.say("Syntax Error: %s" % e)
        except RuntimeError, e:
            self.bot.say(str(e))

    learn.example = 'learn 2001: A Space Oddysey. A space movie by Stanley Kubrick.'

    def forget(self, text):
        """Forget a keyword. Only argument is the key to forget"""
        pass
    forget.example = "forget 2001"

    def lookup(self, text):
        """Lookup a specific keyword. Only argument is the key to lookup"""
        regex = re.compile(r" *([^\[\]\..]*) *(?:\[(\d+)\])?")
        match = regex.match(text)
        try:
            if match:
                key = match.group(1)
                index = match.group(2)

                if not key:
                    raise SyntaxError("Invalid Key. Try Again")
                key = key.strip()
                fact = self.factdb.lookup(key, index)[0]
                self.bot.say(fact)

                # date = datetime.datetime.fromtimestamp(fact[3])
                # date = "%s:%s %s/%s/%s" % (date.hour, date.minute, date.day,
                                        # date.month, date.year)
                # return ("%s[%s/%s]: %s", (%s, %s))" % (fact[6], index, count, fact[2], nick, date)

        except SyntaxError, e:
            self.bot.say("Syntax Error: %s" % e)
        except RuntimeError, e:
            self.bot.say(str(e))

    lookup.example = "lookup A Space Oddysey"

    def search(self, text):
        """Search for matching fact in all stored facts"""
        pass
    search.example = "search Kubric"

    def help(self, text):
        """List all available commands or help for a command"""

        ## we use a regex to see if we have additional args
        regex = re.compile(r' *(\S+)')
        match = regex.match(text)
        ## if we have a match, display docstring for that command
        if match:
            key = match.group(1)
            self.bot.private("%s: %s" % (key, getattr(self, key).__doc__))
            self.bot.private("Example: %s" % getattr(self, key).example)
        else:
            self.bot.private("Available commands: %s" % ", ".join(self.commands))
    help.example = "help lookup or just help"


        #key = data.group(1)
        #value = data.group(2)
        #now = datetime.datetime.now()
        #who = data.nick

        #bot.log.debug("%s %s %s %s" % (key, value, now, who))
