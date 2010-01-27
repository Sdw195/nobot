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

        self.test_structure()

    def create_db_location(self):
        if not os.path.isdir(self.bot.config.datadir):
            os.mkdir(self.bot.config.datadir)

    def create_structure(self):
        pass

    def test_structure(self):
        pass


def timedelta_to_string(delta):

    def calc(amount, dividend):
        return (amount/dividend, amount%dividend)

    def pluralize(singular, plural, count):
        return singular if count == 1 else plural

    years, days = calc(delta.days, 365)
    months, days = calc(days, 12)
    weeks, days = calc(days, 7)
    hours, seconds = calc(delta.seconds, 3600)
    minutes, seconds = calc(seconds, 60)

    date = []
    if years > 0:
        date.append("%s %s" % (years, pluralize("Year", "Years", years)))
    if months > 0:
        date.append("%s %s" % (months, pluralize("Month", "Months", months)))
    if weeks > 0:
        date.append("%s %s" % (weeks, pluralize("Week", "Weeks", weeks)))
    if days > 0:
        date.append("%s %s" % (days, pluralize("Day", "Days", days)))
    if hours > 0:
        date.append("%s %s" % (hours, pluralize("Hour", "Hours", hours)))
    if minutes > 0:
        date.append("%s %s" % (minutes, pluralize("Minute", "Minutes", minutes)))
    return ", ".join(date)
