#!/usr/bin/env python
"""
"""

import sys, os, re, threading, imp
import lib.irc as irc

home = os.getcwd()

class __metamodule__(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'modules'):
            cls.modules = []
        else:
            cls.modules.append(cls)

class command():

    name = None
    example = None
    event = "PRIVMSG"
    thread = True
    rule = r"( +(.*))?"
    regex = None
    action = True
    limit = []

    # main method
    def run(self, bot, data): pass

    ############################################################
    # Internal
    __metaclass__ = __metamodule__

    def __call__(self, cmd, bot, data):
        """Call the run method of specified command"""
        instance = cmd()
        instance.run(bot, data)

def decode(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

class Oracus(irc.Bot):

    def __init__(self, obj):
        irc.Bot.__init__(self, obj)
        self.obj = obj
        self.config = obj.config
        self.log = obj.log
        self.doc = {}
        self.stats = {}
        self.setup()

    def setup(self, _reload=False):

        if _reload:
            command.modules = []

        modules = []
        ## load only enabled
        if hasattr(self.config, 'enable') and self.config.enable:
            for module in self.config.enable:
                modules.append(module)
        ## load all
        else:
            for fn in os.listdir(self.config.moduledir):
                if fn.endswith('.py') and not fn.startswith('_'):
                    modules.append(fn[:-3])

        ## exclude modules
        if hasattr(self.config, "exclude") and self.config.exclude:
            for module in self.config.exclude:
                modules.remove(module)

        ## load modules
        for module in modules:
            self.load_module(module, _reload=_reload)

        # if modules:
        if modules:
            self.log.info("Registered modules: %s" % ", ".join(modules))
            self.modules = modules
        else:
            self.log.warning("Couldn't find any commands")

        self.bind_commands()

    def bind_commands(self):

        def replace(pattern, values):
            return pattern % values

        for cmd in command.modules:

            if not cmd.name:
                cmd.name = cmd.__name__.lower()

            values = {"nick": self.nick, "prefix": self.config.prefix, "cmd": cmd.name}

            if not cmd.example:
                if cmd.__doc__:
                    cmd.example = replace(cmd.__doc__, values)
            else:
                cmd.example = replace(cmd.example, values)

            cmd.event = cmd.event.upper()

            if cmd.regex:
                cmd.matcher = cmd.regex
            else:
                cmd.matcher = r"^ *(?:%(nick)s:|%(prefix)s) *(?:%(cmd)s)" + cmd.rule + "$"

            cmd.matcher = re.compile(replace(cmd.matcher, values))


    def wrapped(self, origin, text, match):
        class BotWrapper(object):
            def __init__(self, bot):
                self.bot = bot

            def __getattr__(self, attr):
                sender = origin.sender or text
                if attr == 'reply':
                    return (lambda msg:
                        self.bot.msg(sender, origin.nick + ': ' + msg))
                elif attr == 'say':
                    return lambda msg: self.bot.msg(sender, msg)
                elif attr == 'private':
                    ## XXX: implement a setting where we can control
                    ## whether to send in a query or notice
                    return lambda msg: self.bot.notice(sender, msg)
                return getattr(self.bot, attr)

        return BotWrapper(self)

    def data(self, origin, text, bytes, match, event, args):
        class CommandInput(unicode):
            def __new__(cls, text, origin, bytes, match, event, args):
                s = unicode.__new__(cls, text)
                s.sender = origin.sender
                s.nick = origin.nick
                s.event = event
                s.bytes = bytes
                s.match = match
                s.group = match.group
                s.groups = match.groups
                s.args = args
                s.admin = origin.nick in self.config.admins
                s.owner = origin.nick == self.config.owner
                return s

        return CommandInput(text, origin, bytes, match, event, args)

    def limit(self, origin, cmd):
        if origin.sender and origin.sender.startswith('#'):
            if hasattr(self.config, 'limit'):
                limits = self.config.limit.get(origin.sender)
                if limits and (cmd.__module__ not in limits):
                    return True
        return False

    def dispatch(self, origin, args):
        bytes, event, args = args[0], args[1], args[2:]
        text = decode(bytes)

        self.log.info("DISPATCH %s %s %s" % (origin.sender, event, text))

        for cmd in command.modules:
            if event != cmd.event:
                continue

            self.log.debug("TESTING COMMAND %s %s %s" % (cmd.name, cmd.event, cmd.matcher.pattern))

            match = cmd.matcher.match(text)
            if match:

                self.log.debug("MATCHED COMMAND %s" % cmd.name)

                if self.limit(origin, cmd):
                    continue

                bot = self.wrapped(origin, text, match)
                data = self.data(origin, text, bytes, match, event, args)

                try:
                    targs = (cmd, bot, data)
                    dispatch = command()
                    if False:#cmd.thread:
                        t = threading.Thread(target=dispatch, args=targs)
                        t.start()
                    else:
                        dispatch(*targs)
                except Exception, e:
                    self.error(origin, e)

                break

    def load_module(self, module, filename=None, _reload=False):
        ## this exists for easy access from modules
        if filename:
            return imp.load_source(module, filename)

        try:
            mod = getattr(__import__('modules.%s' % module), module)
        except ImportError, e:
            self.log.error("Error loading %s: %s" % (module, e))
        if _reload:
            self.log.debug("Reloading %s" % mod)
            reload(mod)
        # except:
        return mod

    def permission(self, limits, data):
        if not limits:
            return True;
        for limit in limits:
            if not getattr(data, limit):
                return False
        return True

