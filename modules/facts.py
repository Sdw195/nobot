from lib.bot import command
from lib.tools import Database

import re

class Fact(command):

    regex = r".*?(?:%(cmd)s\s+(.*)|\?\[([^\[\]]+)\]\s*(\[\d+\])?)"
    triggers = [r"(?=\?\[[^\[\]]+\])"]

    syntax = "fact subcommand or term [args]"
    doc = " ".join(
        [ "Interface with a term database. Using different commands it is"
        , "possible to add, retrieve, search, update and delete a list of"
        , "arbitrary terms and their associated values. If no "
        ])

    def run(self, bot, data):
        self.bot = bot
        self.data = data
        self.url = "http://oracus.dotright.net"

        # self.commands = ["lookup", "search", "learn", "update", "forget", "help"]
        self.commands = ["lookup", "learn", "help", "update", "updateterm", "forget", "details", "list"]

        self.factdb = FactsDB(bot)
        ## if we have a match in group 1, it is a regular call
        ## if we have it in group2, then it is a shorthand lookup
        if data.group(2):
            term = data.group(2).strip()
            if data.group(3):
                term = "%s%s" % (term, data.group(3))
            return self.lookup(term)

        text = data.group(1)
        ## run a regex on the command to see where we want to dispatch too
        regex = re.compile(r'\s*(\S+)(.*)')
        match = regex.match(text)

        if match:
            key = match.group(1)

            if hasattr(self, key):
                ## if we have an method that matches key, then we call a sub action
                getattr(self, key)(match.group(2))
            else:
                ## we have no method with the given name, pass the data on to lookup
                self.lookup(text)
        else:
            bot.say("Error: You must provide a subcommand or term to lookup. Try `fact help'")


    def list(self, text):
        self.bot.say("View all facts and terms at: %s" % self.url)

    list.doc = "View all terms and facts"

    def learn(self, text):
        regex = re.compile(r"\s*\[\s*([^\[\]]+)\s*\]\s+(.*)")
        match = regex.match(text)
        try:
            author = self.data.nick
            key, fact = match.groups("")
            if not key or not fact:
                raise SyntaxError
            self.factdb.learn(key, fact, author)
            self.bot.say("Learned fact")

        except (SyntaxError, AttributeError):
            self.bot.say("Syntax Error. See `fact help learn' for more info")
        except RuntimeError, e:
            self.bot.say(str(e))

    learn.syntax = "fact learn [term (spaces allowed)] fact"
    learn.example = "fact learn [2001: A Space Oddysey] A movie by Stanley Kubrick"
    learn.doc = " ".join(
        [ "Learn a new fact for a term. If term already exists, a new"
        , "fact will be added to its list. If not, a new term will be created"
        ])


    def forget(self, text):
        regex = re.compile(r"\s*([^\[\]]+)(?:\[(\d+)\])?")
        match = regex.match(text)
        try:
            term, index = match.groups()
            if not term:
                raise SyntaxError

            self.factdb.forget(term.strip(), self.data.nick, index)
            if index:
                self.bot.say("Forgot fact")
            else:
                self.bot.say("Forgot term and all it's facts")

        except (SyntaxError, AttributeError):
            self.bot.say("Syntax Error. See `fact help forget' for more info")
        except RuntimeError, e:
            self.bot.say(str(e))

    forget.syntax = "fact forget term [index]"
    forget.example = "fact forget A Space Oddysey [2]. Forget the 2nd. fact of the term"
    forget.doc =  " ".join(
        [ "Forget a specific fact, or all facts for a term."
        , "If no index is given, all facts and the term itself will be forgotten."
        ])


    def lookup(self, text):
        regex = re.compile(r"\s*([^\[\]]+)(?:\[(\d+)\])?")
        match = regex.match(text)
        try:
            term, index = match.groups()

            if not term:
                raise SyntaxError
            fact = self.factdb.lookup(term.strip(), index)
            self.bot.say(fact)

        except (SyntaxError, AttributeError):
            self.bot.say("Syntax Error. See `fact help lookup' for more info")
        except RuntimeError, e:
            self.bot.say(str(e))

    lookup.syntax = "fact lookup term [index] or ?[term][index]"
    lookup.example = "fact lookup A Space Oddysey [2] or ?[Space Oddysey][2]"
    lookup.doc =  " ".join(
        [ "Lookup a specific term. A search for a partial match will be performed."
        , "If there are multiple matches, a list of matches will be returned."
        , "An optional index, eg.: [2] can be supplied if there are many 'pages'"
        , "for the given term. Also see syntax for shorthand"
        ])


    def details(self, text):
        regex = re.compile(r"\s*([^\[\]]+)(?:\[(\d+)\])?")
        match = regex.match(text)
        try:
            term, index = match.groups()

            if not term:
                raise SyntaxError
            fact = self.factdb.details(term.strip(), index)
            self.bot.say(fact)

        except (SyntaxError, AttributeError):
            self.bot.say("Syntax Error. See `fact help details' for more info")
        except RuntimeError, e:
            self.bot.say(str(e))

    details.syntax = "fact details term [index]"
    details.example = "fact details A Space Oddysey [2]"
    details.doc =  " ".join(
        [ "Show details about a fact."])


    def update(self, text):
        regex = re.compile(r"\s*(.*?)(?:\s*\[(\d+)\])\s*(.*)")
        match = regex.match(text)
        try:
            author = self.data.nick
            term, index, fact = match.groups()
            if not (term or index or fact):
                raise SyntaxError
            self.factdb.update(term, fact, author, index)
            self.bot.say("Updated fact")
        except (SyntaxError, AttributeError):
            self.bot.say("Syntax Error. See `fact help update' for more info")
        except RuntimeError, e:
            self.bot.say(str(e))

    update.syntax = "fact update term [index] newfact"
    update.example = "fact update A Space Oddysey [1] A movie by Stanley Kubrick. It portrays a fictional future"
    update.doc =  "Update a given fact for a specific term"


    def updateterm(self, text):
        regex = re.compile(r"\s*\[\s*([^\[\]]+)\s*\]\s+([^\[\]]+)")
        match = regex.match(text)
        try:
            term, newterm = match.groups()
            if not (term or newterm):
                raise SyntaxError
            self.factdb.updateterm(term, newterm)
            self.bot.say("Updated term")
        except (SyntaxError, AttributeError):
            self.bot.say("Syntax Error. See `fact help lookup' for more info")
        except RuntimeError, e:
            self.bot.say(str(e))

    updateterm.syntax = "fact updateterm [term] newterm"
    updateterm.example = "fact updateterm [A Space Oddysey] A Space Oddity"
    updateterm.doc =  "Update the text of a term."


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
            if not key in self.commands:
                return self.bot.private("`%s' is not a command" % key)
            if hasattr(getattr(self, key), 'syntax'):
                self.bot.private("Syntax: %s" % getattr(self, key).syntax)
            if hasattr(getattr(self, key), 'example'):
                self.bot.private("Example: %s" % getattr(self, key).example)
            if hasattr(getattr(self, key), 'doc'):
                self.bot.private("%s: %s" % (key, getattr(self, key).doc))
        else:
            self.bot.private("Subcommands: %s" % ", ".join(self.commands))

    help.syntax = "fact help [subcommand]"
    help.doc = "Provide help on a subcommand or show list of available subcommands"

class FactsDB(Database):

    def create_structure(self):
        c = self.con.cursor()
        c.execute("""
            CREATE TABLE terms (
                id INTEGER PRIMARY KEY,
                term TEXT,
                count INTEGER
            )""")
        c.execute("""
            CREATE TABLE facts (
                id INTEGER PRIMARY KEY,
                tid INTEGER,
                position INTEGER DEFAULT 1,
                fact TEXT,
                deleted INTEGER DEFAULT 0,
                created_at DATETIME,
                created_by TEXT,
                updated_at DATETIME DEFAULT NULL,
                updated_by TEXT DEFAULT NULL,
                deleted_at DATETIME DEFAULT NULL,
                deleted_by TEXT DEFAULT NULL
            )""")

        self.con.commit()

    def learn(self, term, fact, author):
        c = self.con.cursor()
        ## see if we already have a matching term
        c.execute("SELECT id, count FROM terms WHERE term = ?", [term])
        res = c.fetchone()
        if res:
            tid, pos = res
            self.check_duplicate(tid, fact)
        else:
            ## we found none, add a new row
            c.execute("INSERT INTO terms (term, count) VALUES (?, 0)", [term])
            self.con.commit()
            tid, pos = c.lastrowid, 0

        ## now we have a term id, insert a new row
        c.execute("""INSERT INTO
            facts (tid, position, fact, created_at, created_by) VALUES (?, ?, ?, datetime('now'), ?)
            """, (tid, pos+1, fact, author))

        ## add one to term count
        c.execute("""UPDATE terms SET count = count + 1 WHERE id = ?""", [tid])
        self.con.commit()

    def updateterm(self, term, newterm):
        c = self.con.cursor()
        tid = self.get_tid(term)

        c.execute("UPDATE terms SET term = ? WHERE id = ?", (newterm, tid))
        self.con.commit()

    def update(self, term, fact, author, index):
        c = self.con.cursor()
        tid = self.get_tid(term)
        self.check_duplicate(tid, fact)

        ## check if we have a fact with that position
        c.execute("SELECT id FROM facts WHERE position = ? AND tid = ? AND deleted = 0", (index, tid))
        if not c.fetchone():
            raise RuntimeError("No fact to update")

        ## update fact
        c.execute("""UPDATE facts SET fact = ?, updated_by = ?, updated_at = datetime('now') 
                  WHERE tid = ? AND position = ? AND deleted = 0""", (fact, author, tid, index))
        self.con.commit()

    def lookup(self, term, index=None):
        term = "%%%s%%" % term
        index = index or 1
        c = self.con.cursor()
        c.execute("""SELECT terms.id, terms.term, terms.count, facts.tid, facts.position, facts.fact
                  FROM terms, facts WHERE terms.term LIKE ?  AND facts.tid = terms.id 
                  AND facts.position = ? AND facts.deleted = 0""", (term, index))
        res = c.fetchone()

        if not res:
            raise RuntimeError("No results found")

        return "%s[%s/%s]: %s" % (res[1], index, res[2], res[5])

    def details(self, term, index=None):
        term = "%%%s%%" % term
        index = index or 1
        c = self.con.cursor()
        c.execute("""SELECT terms.id, terms.term, terms.count, facts.tid, facts.fact,
                  facts.created_by, strftime("%H:%M %d/%m/%Y", facts.created_at),
                  facts.updated_by, strftime("%H:%M %d/%m/%Y", facts.updated_at)
                  FROM terms, facts WHERE terms.term LIKE ? AND facts.tid = terms.id 
                  AND facts.position = ? AND facts.deleted = 0""", (term, index))
        res = c.fetchone()

        if not res:
            raise RuntimeError("No results found")

        print res

        details = "%s - Term: %s, Index: %s, Total: %s, Created By: %s, Created At: %s" % (
            res[4], res[1], index, res[2], res[5], res[6])
        if res[6] and res[7]:
            details = "%s, Updated By: %s, Updated At: %s" % (details, res[7], res[6])

        return details

    def forget(self, term, nick, index=None):
        c = self.con.cursor()
        tid = self.get_tid(term)

        c.execute("SELECT count FROM terms where id = ?", [tid])
        count = c.fetchone()[0]
        if index and int(index) <= int(count):
            facts = [index]
        elif index is None:
            facts = [r+1 for r in range(count)]
        else:
            raise SyntaxError

        for pos in facts:
            ## mark the row as deleted
            c.execute("""UPDATE facts SET deleted = 1, deleted_at = datetime('now'), deleted_by = ?
                    WHERE tid = ? AND position = ?""", (nick, tid, pos))
            ## decrement the term counter
            c.execute("UPDATE terms SET count = count - 1 WHERE id = ?", [tid])
            self.con.commit()
        for pos in facts:
            ## change position of all facts
            c.execute("UPDATE facts SET position = position - 1 WHERE tid = ? AND position > ?", (tid, pos))
            self.con.commit()

    def get_tid(self, term):
        c = self.con.cursor()
        ## check if term exists
        c.execute("SELECT id FROM terms WHERE term = ?", [term])
        tid = c.fetchone()
        if tid:
            tid = tid[0]
        else:
            ## we found none, raise error
            raise RuntimeError("No matching term found")
        return tid

    def check_duplicate(self, tid, fact):
        c = self.con.cursor()
        ## check for duplicates
        c.execute("SELECT * FROM facts WHERE tid = ? AND fact = ? AND deleted = 0", (tid, fact))
        if c.fetchone():
            raise RuntimeError("Duplicate fact for term")
