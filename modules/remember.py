from lib.bot import command
from lib.tools import Database, timedelta_to_string
import datetime

class Seen(command):
    rule = " +(\S+)"
    doc = "Display info on when `nick' was last logged in"
    syntax = "seen `nick'"
    def run(self, bot, data):
        nick = data.group(1)
        if not nick:
            return bot.say("You must specify a nick to query")
        if nick.lower() == data.origin.nick.lower():
            return bot.say("What! Really? That is a weird thing to ask for...")
        if nick.lower() == "george":
            return bot.say("Hah. Yeah right!")
        db = RememberDB(bot)
        try:
            seen = db.seen(nick)
        except RuntimeError:
            bot.say("I do not remember seeing %s come or go" % nick)
        else:
            if seen == 'now':
                bot.say("%s is here now" % nick)
            else:
                then = datetime.datetime.strptime(seen, "%Y-%m-%d %H:%M:%S")
                now = datetime.datetime.utcnow()
                delta = now - then
                ago = timedelta_to_string(delta)
                if not ago:
                    return bot.say("%s just left" % nick)
                bot.say("%s was last seen %s ago" % (nick, ago))


class Tell(command):
    rule = " +(\w+) +(.*)"
    doc = "Tell `nick' message when he is seen next time"
    syntax = "tell `nick' I wanted you to read this"
    def run(self, bot, data):
        nick = data.group(1)
        if not nick:
            return bot.say("You must specify a nick to tell")
        msg = data.group(2)
        if not msg:
            return bot.say("You must specify a message to send to nick")
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
    event = ["PART", "JOIN", "QUIT"]
    action = False
    def run(self, bot, data):
        if data.nick:
            db = RememberDB(bot)
            if data.event in ["PART", "QUIT"]:
                if data.nick == bot.nick:
                    return False
                db.parted(data.nick)
            elif data.event == "JOIN":
                tells = db.joined(data.nick)
                if tells:
                    for tell in tells:
                        then = datetime.datetime.strptime(tell[4], "%Y-%m-%d %H:%M:%S")
                        now = datetime.datetime.utcnow()
                        delta = now - then
                        ago = timedelta_to_string(delta)
                        bot.private("%s: %s said: \"%s\" %s ago" % \
                                (tell[1], tell[3], tell[2], ago))


class HandleNick(command):
    regex = r'(.*)'
    event = ["NICK"]
    action = False
    def run(self, bot, data):
        oldnick = data.nick
        newnick = data.group(1)
        if oldnick.lower() == newnick.lower():
            return False
        ## log out oldnick, and join new nick
        db = RememberDB(bot)
        db.parted(oldnick)
        db.joined(newnick)


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
        c.execute("SELECT nick, date FROM seen WHERE lower(nick) = ?", [nick.lower()])
        res = c.fetchone()
        if not res:
            raise RuntimeError
        else:
            return res[1]

    def parted(self, nick):
        c = self.con.cursor()
        ## check if nick is already in db
        c.execute("SELECT nick FROM seen WHERE lower(nick) = ?", [nick.lower()])
        res = c.fetchone()
        if not res:
            c.execute("INSERT INTO seen (nick, date) VALUES(?, datetime('now'))", [nick])
        else:
            c.execute("UPDATE seen SET date = datetime('now') WHERE lower(nick) = ?", [nick.lower()])
        self.con.commit()

    def joined(self, nick):
        c = self.con.cursor()
        ## check if nick is already in db
        c.execute("SELECT nick FROM seen WHERE lower(nick) = ?", [nick.lower()])
        res = c.fetchone()
        if not res:
            c.execute("INSERT INTO seen (nick, date) VALUES(?, 'now')", [nick])
        else:
            c.execute("UPDATE seen SET date = 'now' WHERE lower(nick) = ?", [nick.lower()])
        self.con.commit()
        ## get any tells for this nick
        c.execute("SELECT * FROM tell WHERE lower(nick) = ?", [nick.lower()])
        res = c.fetchall()
        if res:
            ## delete them, so we don't tell them twice
            c.execute("DELETE FROM tell WHERE lower(nick) = ?", [nick.lower()])
            self.con.commit()
        return res

    def tell(self, nick, msg, by):
        c = self.con.cursor()
        c.execute("INSERT INTO tell (nick, what, by, added) VALUES (?, ?, ?, datetime('now'))", (nick, msg, by))
        self.con.commit()
