from lib.bot import command
from lib.tools import Database

class TracDB(Database):

    def create_structure(self):
        c = self.con.cursor()
        c.execute("""
            CREATE TABLE trac (
                  id INTEGER PRIMARY KEY,
                  ticket INTEGER UNIQUE,
                  summary TEXT,
                  component TEXT,
                  version TEXT,
                  milestone TEXT,
                  type TEXT,
                  owner TEXT,
                  status TEXT,
                  created TIMESTAMP,
                  updated TIMESTAMP,
                  description TEXT,
                  reporter TEXT
            )""")
        self.con.commit()

class TicketId(command):

    regex = r".*(?:%(cmd)s\s+\d+|(t#\d+)).*"
    triggers = [r"(?=t#\d+)"]
    syntax = 'ticketid id | t#id'
    example = "Please see t#320"
    doc = " ".join(
        [ "Print an url to the id of the ticket specified"
        ])

    def run(self, bot, data):
        tid = data.group(1)
        if tid:
            ## cut off t#
            tid = tid[2:]
            tracker = "http://wiki.neurohack.com/transcendence/trac/ticket/%s" % tid
            bot.say("Tracker ticket #%s: %s" % (tid, tracker))
