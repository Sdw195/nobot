from lib.bot import command
from lib.tools import Database

class Seen(command):

    rule = " +(\w+)"
    doc = "Display info on when `nick' was last logged in"
    syntax = "seen `nick'"

    def run(self, bot, data):
        nick = None
        try:
            nick = data.group(1)
            if not nick:
                raise AttributeError
        except AttributeError:
            bot.say("You must specify a nick to query")

        db = RememberDB(bot)

        try:
            seen = db.seen(nick)
        except (RuntimeError, TypeError):
            bot.say("I do not remember seeing %s come or go", nick)
        else:
            if seen == 'now':
                bot.say("%s is here now" % nick)
            else:
                bot.say("%s was last seen %s" % (nick, seen))


class Tell(command):

    rule = " +(\w+) +(.*)"
    doc = "Tell `nick' message when he is seen next time"
    syntax = "tell `nick' I wanted you to read this"

    def run(self, bot, data):
        nick = None
        try:
            nick = data.group(1)
            if not nick:
                raise AttributeError
        except AttributeError:
            bot.say("You must specify a nick to tell")
        msg = None
        try:
            msg = data.group(2)
            if not msg:
                raise AttributeError
        except AttributeError:
            bot.say("You must specify a message to send to nick")

        db = RememberDB(bot)

        try:
            by = data.origin.nick
            tell = db.tell(nick, msg, by)
        except Exception:
            bot.say("Something went wrong. I wont be telling anyone anything")
        else:
            bot.say("Stored message")


class HandleSeen(command):

    regex = r'.*'
    event = ["PART", "JOIN"]
    action = False

    def run(self, bot, data):

        if data.nick:
            db = RememberDB(bot)
            if data.event == "PART":
                db.parted(data.nick)
            elif data.event == "JOIN":
                tells = db.joined(data.nick)
                if tells:
                    for tell in tells:
                        bot.say("%s: %s said: %s on %s" % (tell[1], tell[3], tell[2], tell[4]))


class RememberDB(Database):

    def create_structure(self):
        c = self.con.cursor()
        try:
            c.execute("""
                CREATE TABLE seen (
                    id INTEGER PRIMARY KEY,
                    nick TEXT,
                    date DATETIME
                )""")
            c.execute("""
                CREATE TABLE tell (
                    id INTEGER PRIMARY KEY,
                    nick INTEGER,
                    what TEXT,
                    by TEXT,
                    added DATETIME
                )""")

            self.con.commit()
        except Exception:
            pass

    def test_structure(self):
        c = self.con.cursor()
        try:
            c.execute("SELECT * FROM seen LIMIT 1")
            c.execute("SELECT * FROM tell LIMIT 1")
        except Exception:
            self.create_structure()

    def seen(self, nick):
        c = self.con.cursor()
        c.execute("SELECT nick, date FROM seen WHERE nick = ?", [nick])
        res = c.fetchone()
        if not res:
            raise RuntimeError
        else:
            return res[1]

    def parted(self, nick):
        c = self.con.cursor()
        ## check if nick is already in db
        c.execute("SELECT nick FROM seen WHERE nick = ?", [nick])
        res = c.fetchone()
        if not res:
            c.execute("INSERT INTO seen (nick, date) VALUES(?, datetime('now'))", [nick])
        else:
            c.execute("UPDATE seen SET date = datetime('now') WHERE nick = ?", [nick])
        self.con.commit()

    def joined(self, nick):
        c = self.con.cursor()
        ## check if nick is already in db
        c.execute("SELECT nick FROM seen WHERE nick = ?", [nick])
        res = c.fetchone()
        if not res:
            c.execute("INSERT INTO seen (nick, date) VALUES(?, 'now')", [nick])
        else:
            c.execute("UPDATE seen SET date = 'now' WHERE nick = ?", [nick])
        self.con.commit()
        ## get any tells for this nick
        c.execute("SELECT * FROM tell WHERE nick = ?", [nick])
        res = c.fetchall()
        if res:
            ## delete them, so we don't tell them twice
            c.execute("DELETE FROM tell WHERE nick = ?", [nick])
            self.con.commit()
        return res

    def tell(self, nick, msg, by):
        c = self.con.cursor()
        c.execute("INSERT INTO tell (nick, what, by, added) VALUES (?, ?, ?, datetime('now'))", (nick, msg, by))
        self.con.commit()
