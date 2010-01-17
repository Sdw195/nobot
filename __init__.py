#!/usr/bin/env python
"""
"""

import sys, os, time, threading, signal
import lib.bot as bot

class Watcher(object):
    # Cf. http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496735
    def __init__(self):
        self.child = os.fork()
        if self.child != 0:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            self.kill()
            sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass

def run_oracus(obj):
    if hasattr(obj.config, 'delay'):
        delay = obj.config.delay
    else:
        delay = 20

    def connect(obj):
        p = bot.Oracus(obj)
        p.run(obj.config.server, obj.config.port)

    try:
        Watcher()
    except Exception, e:
        obj.log.warning(e)

    while True:
        try: connect(obj)
        except KeyboardInterrupt:
            sys.exit()

        if not isinstance(delay, int):
            break

        obj.log.warning('Disconnected. Reconnecting in %s seconds...' % delay)
        time.sleep(delay)

def run(obj):
    t = threading.Thread(target=run_oracus, args=(obj,))
    if hasattr(t, 'run'):
        t.run()
    else:
        t.start()

if __name__ == '__main__':
    print __doc__
