#!/usr/bin/env python
"""
"""

import sys, os, re, threading, imp
import lib.irc as irc

class __metacommand__(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'modules'):
            cls.modules = []
        else:
            cls.modules.append(cls)

        ## set up this command
        cls._name_ = name.lower()
        cls._path_ = "%s.%s" % (cls.__module__.partition('.')[2], cls._name_)
        cls._event_ = [c.upper() for c in cls.event]

class command():

    syntax = None
    example = None
    doc = None
    event = ["PRIVMSG"]
    rule = r"( +(.*))?"
    regex = None
    triggers = []
    thread = True
    action = True

    # main method
    def run(self, bot, data): pass

    ############################################################
    # Internal
    __metaclass__ = __metacommand__

    _regex_ = r""
    _trigger_ = ""

    def __call__(self, cmd, bot, data):
        """Call the run method of specified command"""
        instance = cmd()
        instance.run(bot, data)

class Nobot(irc.Bot):

    def __init__(self, obj):
        irc.Bot.__init__(self, obj)
        self.obj = obj
        self.config = obj.config
        self.log = obj.log
        self.substitutions = {"nick": self.nick, "prefix": self.config.prefix}
        self.triggers = [r"%(nick)s(?:[,:]?\s+(?=\w+))", r"%(prefix)s(?=\w+)"]

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
            self.log.info("Modules: %s" % ", ".join(modules))
            self.log.info("Commands: %s" % ", ".join([cmd._name_ for cmd in command.modules]))
            self.modules = modules
        else:
            self.log.warning("Couldn't find any commands")

        self.bind_commands()

    def interpolate(self, text, cmd=None):
        values = self.substitutions
        if cmd:
            values['cmd'] = cmd._name_
        return text % values

    def bind_commands(self):

        ## build the triggers
        self._triggers_ = []
        for trigger in self.triggers:
            self._triggers_.append(self.interpolate(trigger))

        for cmd in command.modules:

            ## build the regex we will match
            if cmd.regex:
                cmd._regex_ = cmd.regex
            else:
                cmd._regex_ = r"\s*(?:%(cmd)s)" + cmd.rule

            cmd._regex_ = re.compile(self.interpolate(cmd._regex_, cmd))
            self.log.debug("REGEX: %s" % cmd._regex_.pattern)

            ## if this cmd has any triggers and they differ from those
            ## we already have, add them to the triggers
            if cmd.triggers:
                for trigger in cmd.triggers:
                    trigger = self.interpolate(trigger, cmd)
                    if not trigger in self._triggers_:
                        self._triggers_.append(trigger)

        ## at this point we should build a propper regex to match as a trigger
        self._trigger_ = re.compile(r".*(?:%s)(.*)" % "|".join(self._triggers_))
        self.log.info("TRIGGER: %s" % self._trigger_.pattern)


    def wrapped(self, origin, text, match):
        class BotWrapper(object):
            def __init__(self, bot):
                self.bot = bot

            def __getattr__(self, attr):
                sender = origin.sender or text
                if attr == 'reply':
                    return lambda msg: self.bot.msg(sender, origin.nick + ': ' + msg)
                elif attr == 'say':
                    return lambda msg: self.bot.msg(sender, msg)
                elif attr == 'private':
                    return lambda msg: self.bot.msg(origin.nick, msg)
                return getattr(self.bot, attr)

        return BotWrapper(self)


    def data(self, origin, text, bytes, match, event, args):
        class CommandInput(unicode):
            def __new__(cls, text, origin, bytes, match, event, args):
                s = unicode.__new__(cls, text)
                s.origin = origin
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


    def access(self, origin, cmd):
        if origin.nick and hasattr(self.config, 'access'):
            for path, nicks in self.config.access.iteritems():
                if re.match(path, cmd._path_) and not origin.nick in nicks :
                    return False
        return True


    def dispatch(self, origin, args):
        bytes, event, args = args[0], args[1], args[2:]
        text = self.decode(bytes)

        self.log.debug("DISPATCH %s %s %s" % (origin.sender, event, text))

        ## if we didnt match a trigger and are in a channel don't continue
        trigger = self._trigger_.match(text)
        if not trigger and type(origin.sender) is str and origin.sender.startswith('#'):
            return False
        elif trigger:
            ## get the text we triggered on
            _trigger_ = trigger.group(1)
        else:
            _trigger_ = text

        for cmd in command.modules:
            ## if we don't match the event, try next command
            if not event in cmd._event_:
                continue

            self.log.debug("TESTING COMMAND %s %s %s" % (cmd._name_, cmd.event, cmd._regex_.pattern))

            match = cmd._regex_.match(_trigger_)
            if match:

                lockfile = "%s.lock" % os.path.join(self.config.datadir, self.config.configname)
                if os.path.exists(lockfile) and not cmd._name_ == "unlock":
                    self.msg(origin.sender, "Dispatch Locked. No commands will be processed.")
                    continue

                self.log.info("MATCHED COMMAND %s: %s %s %s" % (cmd._name_, origin.sender, event, _trigger_))

                if not self.access(origin, cmd):
                    self.log.info("ACCESS DENIED - %s" % cmd._path_)
                    continue

                bot = self.wrapped(origin, text, match)
                data = self.data(origin, text, bytes, match, event, args)

                try:
                    targs = (cmd, bot, data)
                    dispatch = command()
                    ## TODO: have a deeper look at threading. For now it is disabled here
                    if False:#cmd.thread:
                        t = threading.Thread(target=dispatch, args=targs)
                        t.start()
                    else:
                        dispatch(*targs)
                except Exception, e:
                    self.error(origin)

                ## use group1 from match to try the dispatch again
                if hasattr(trigger, 'group'):
                    ## sub away the matched trigger
                    try:
                        bytes = re.sub(_trigger_, "", text)
                    except Exception:
                        break
                    ## we don't want to keep sending same text over and over, right?
                    if bytes <> text:
                        self.dispatch(origin, (bytes, event, args))

                ## stop looking for matches
                break


    def load_module(self, module, filename=None, folder="modules", _reload=False):
        if filename:
            return imp.load_source(module, filename)
        try:
            mod = getattr(__import__('%s.%s' % (folder, module)), module)
        except ImportError, e:
            self.log.error("Error loading %s: %s" % (module, e))
        if _reload:
            self.log.debug("Reloading %s" % mod)
            reload(mod)
        return mod


    def decode(self, bytes):
        try:
            text = bytes.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = bytes.decode('iso-8859-1')
            except UnicodeDecodeError:
                text = bytes.decode('cp1252')
        return text
