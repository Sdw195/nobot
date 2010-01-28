from lib.bot import command
from lib.tools import Database

import re, os, sqlite3

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

        self.commands = ["lookup", "learn", "help", "update", "updateterm", "forget", "details", "list", "move"]

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
        return self.bot.say("View all facts and terms at: %s" % self.url)

    list.doc = "View all terms and facts"

    def learn(self, text):
        regex = re.compile(r"\s*\[\s*([^\[\]]+)\s*\]\s+(.*)")
        match = regex.match(text)
        self.bot.log.debug(match.groups())
        try:
            author = self.data.nick
            key, fact = match.groups("")
            if not key or not fact:
                raise SyntaxError
        except (SyntaxError, AttributeError):
            return self.bot.say("Syntax Error. See `fact help learn' for more info")
        try:
            self.factdb.learn(key, fact, author)
            return self.bot.say("Learned fact")
        except RuntimeError, e:
            return self.bot.say(str(e))

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
        except (SyntaxError, AttributeError):
            return self.bot.say("Syntax Error. See `fact help forget' for more info")

        try:
            self.factdb.forget(term.strip(), self.data.nick, index)
            if index:
                return self.bot.say("Forgot fact")
            else:
                return self.bot.say("Forgot term and all it's facts")
        except RuntimeError, e:
            return self.bot.say(str(e))

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
        except (SyntaxError, AttributeError):
            return self.bot.say("Syntax Error. See `fact help lookup' for more info")
        try:
            fact = self.factdb.lookup(term.strip(), index)
            return self.bot.say(fact)
        except RuntimeError, e:
            return self.bot.say(str(e))

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
        except (SyntaxError, AttributeError):
            return self.bot.say("Syntax Error. See `fact help details' for more info")
        try:
            fact = self.factdb.details(term.strip(), index)
            return self.bot.say(fact)
        except RuntimeError, e:
            self.bot.say(str(e))

    details.syntax = "fact details term [index]"
    details.example = "fact details A Space Oddysey [2]"
    details.doc =  " ".join(
        [ "Show details about a fact."])


    def switch(self, text):
        regex = re.compile(r"\s*(.*?)(?:\s*\[(\d+)\])(?:\s*\[(\d+)\])")
        match = regex.match(text)
        try:
            term, index, newindex = match.groups()
            if not (term or index or newindex):
                raise SyntaxError
        except (SyntaxError, AttributeError):
            return self.bot.say("Syntax Error. See `fact help switch' for more info")
        try:
            self.factdb.switch(term, index, newindex)
            return self.bot.say("Switched facts")
        except RuntimeError, e:
            self.bot.say(str(e))

    switch.syntax = "fact switch term [index] [newindex]"
    switch.example = "fact switch A Space Oddysey [1] [2]"
    switch.doc =  "Exchange positions of two facts."


    def update(self, text):
        regex = re.compile(r"\s*(.*?)(?:\s*\[(\d+)\])\s*(.*)")
        match = regex.match(text)
        try:
            author = self.data.nick
            term, index, fact = match.groups()
            if not (term or index or fact):
                raise SyntaxError
        except (SyntaxError, AttributeError):
            return self.bot.say("Syntax Error. See `fact help update' for more info")
        try:
            self.factdb.update(term, fact, author, index)
            return self.bot.say("Updated fact")
        except RuntimeError, e:
            return self.bot.say(str(e))

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
        except (SyntaxError, AttributeError):
            return self.bot.say("Syntax Error. See `fact help lookup' for more info")
        try:
            self.factdb.updateterm(term, newterm)
            return self.bot.say("Updated term")
        except RuntimeError, e:
            return self.bot.say(str(e))

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
        try:
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
        except Exception:
            pass

        self.con.commit()

    def test_structure(self):
        c = self.con.cursor()
        try:
            c.execute("SELECT * FROM terms LIMIT 1")
            c.execute("SELECT * FROM facts LIMIT 1")
        except Exception:
            self.create_structure()

    def learn(self, term, fact, author):
        c = self.con.cursor()
        ## see if we already have a matching term
        c.execute("SELECT id, count FROM terms WHERE lower(term) = ?", [term.lower()])
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
        self.write_facts()

    def updateterm(self, term, newterm):
        c = self.con.cursor()
        tid = self.get_tid(term)

        c.execute("UPDATE terms SET term = ? WHERE id = ?", (newterm, tid))
        self.con.commit()
        self.write_facts()

    def switch(self, term, index, newindex):
        c = self.con.cursor()
        tid = self.get_tid(term)

        ## check if the indexes are valid
        c.execute("SELECT id FROM facts WHERE position = ? AND tid = ? AND deleted = 0", (index, tid))
        if not c.fetchone():
            raise RuntimeError("No fact at first index's position")
        c.execute("SELECT id FROM facts WHERE position = ? AND tid = ? AND deleted = 0", (newindex, tid))
        if not c.fetchone():
            raise RuntimeError("No fact at second index's position")

        ## update facts
        c.execute("""UPDATE facts SET position = 0 WHERE tid = ? AND position = ? AND deleted = 0""", (tid, index))
        self.con.commit()
        c.execute("""UPDATE facts SET position = ? WHERE tid = ? AND position = ? AND deleted = 0""", (index, tid, newindex))
        self.con.commit()
        c.execute("""UPDATE facts SET position = ? WHERE tid = ? AND position = 0 AND deleted = 0""", (newindex, tid))
        self.con.commit()
        self.write_facts()

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
        self.write_facts()

    def lookup(self, term, index=None):
        term = "%%%s%%" % term.lower()
        index = index or 1
        c = self.con.cursor()
        c.execute("""SELECT terms.id, terms.term, terms.count, facts.tid, facts.position, facts.fact
                  FROM terms, facts WHERE lower(terms.term) LIKE ?  AND facts.tid = terms.id 
                  AND facts.position = ? AND facts.deleted = 0""", (term, index))
        res = c.fetchone()

        if not res:
            raise RuntimeError("No results found")

        return "%s[%s/%s]: %s" % (res[1], index, res[2], res[5])

    def details(self, term, index=None):
        term = "%%%s%%" % term.lower()
        index = index or 1
        c = self.con.cursor()
        c.execute("""SELECT terms.id, terms.term, terms.count, facts.tid, facts.fact,
                  facts.created_by, strftime("%H:%M %d/%m/%Y", facts.created_at),
                  facts.updated_by, strftime("%H:%M %d/%m/%Y", facts.updated_at)
                  FROM terms, facts WHERE lower(terms.term) LIKE ? AND facts.tid = terms.id 
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
        self.write_facts()

    def get_tid(self, term):
        c = self.con.cursor()
        ## check if term exists
        c.execute("SELECT id FROM terms WHERE lower(term) = ?", [term.lower()])
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

    def write_facts(self):
        """Write an html file with all facts"""
        self.con.row_factory = sqlite3.Row
        c = self.con.cursor()
        htmlfile = "%s.facts.html" % os.path.join(self.bot.config.datadir, "html", self.bot.config.configname)

        def escape(s):
            s = re.sub("&", "&amp;", s)
            s = re.sub("<", "&lt;", s)
            s = re.sub(">", "&gt;", s)
            s = re.sub('"', "&quot;", s)
            return s

        res = c.execute("SELECT * from terms, facts WHERE terms.id = facts.tid AND facts.deleted = 0 ORDER BY facts.tid, facts.position")

        html = "<html><head><title>Oracus fact list</title><style type='text/css'>%s</style></head>"

        css = "body{background-color:#333;padding:5px;margin:0;color:#fff;font-size:12px;}"
        css = css + "dl {border:0px dotted #999;padding:10px;margin:10px 10px;}"
        css = css + "dl dt{font-weight:bold;margin-bottom:10px;}"
        css = css + "dl dd{padding:0px;margin:0px 0px 5px;color:#999}"
        css = css + "dl dd .fact{color:#fff}"
        css = css + "dl dd .meta{margin-left:10px;color:#999;font-size:10px;}"
        css = css + "hr{border:0;border-top: 1px dotted #999;}"
        html = html % css

        html = html + "<body>"
        facts = res.fetchall()
        length = len(facts)
        term = None
        for i, fact in zip(range(length), facts):
            if fact['term'] <> term:
                term = fact['term']
                html = html + "<dl><dt>" + fact['term'] + "</dt>"

            #html = html + "<dd>%s. <span class='fact'>%s</span> <span class='meta'>Created by: %s <span class='date'>(%s)</span></span>" % \
            html = html + "<dd>%s. <span class='fact'>%s</span></dd>" % \
                ( fact['position']
                , escape(fact['fact'])
                )

            #if fact['updated_at']:
            #    html = html + "<span class='meta' style='margin-left: 10px;'>Updated by: %s <span class='date'>(%s)</span></span>" % \
            #    ( fact['updated_by'] or ""
            #    , fact['updated_at'] or ""
            #    )
            #html = html + "</dd>"

            if i+1 >= length or facts[i+1]['term'] <> term:
                html = html + "</dl>"
            if not (i+1 >= length) and facts[i+1]['term'] <> term:
                html = html + "<hr />"

        html + "</body></html>"

        with open(htmlfile, "w") as f:
            f.write(html)
