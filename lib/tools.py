#!/usr/bin/env python
"""
"""

import os, sqlite3

class Database(object):

    def __init__(self, bot):
        self.bot = bot
        self.filename = "%s.db" % os.path.join(bot.config.datadir, bot.config.configname)
        created = False

        if not os.path.exists(self.filename):
            self.create_db_location()
            created = True

        self.con = sqlite3.connect(self.filename)

        if created:
            self.create_structure()

    def create_db_location(self):
        if not os.path.isdir(self.bot.config.datadir):
            os.mkdir(self.bot.config.datadir)

    def create_structure(self):
        pass

