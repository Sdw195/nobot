from lib.bot import command

import lib.irc as irc
import random 
import datetime


class when(command):

    rule = r"(.*)"

    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
        text = 'soon' u"\u2122"	
        if not text:
            text = "Error nothing to say"
        bot.say(text.strip())

class fail(command):

    rule = r"(.*)"

    syntax = "fail"
    doc = "fails"

    def run(self, bot, data):
 
        text = "I came, I saw, I failed"
        bot.say(text.strip())
   
class cake(command):

    rule = r"(.*)"
    #triggers = [r"(?=cake\w+)"]
    #triggers = [r"(?=cake)"]
    syntax = "cake"
    doc = "what is cake "

    def run(self, bot, data):
 
        text = 'The cake is a lie' + ' ' + data.origin.nick
        bot.say(text.strip())


class echo(command):

    rule = r"(.*)"

    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
        text = data.group(1)	
        if not text:
            text = "Error nothing to say"
        bot.say(text.strip())

class do(command):

    rule = r"(.*)"

    syntax = "do <action>"
    doc = "Perform text as an action only in channels"

    def run(self, bot, data):
        text = '\x01ACTION %s\x01'%data.group(1)
        if not text:
            text = "Error nothing to do"
        bot.say(text.strip())
    

class node(command):
 
    #rule = r" +(?\S+) (.+)"
    rule = r"\s+(\d+)(?:\s+(\d+))?"

#it basically says "any whitespace, followed by any digits, followed by any whitespace, optionally followed by any digits"
    syntax = "makes link to hedgewars.org forum"
    doc = " node [node#] [page#]"
 
    def run(self, bot, data):
      #  if data.sender.startswith('#'):
       #     return
        a, b, = data.group(1), data.group(2)
        if a and b:
            text = 'http://hedgewars.org/node/' + data.group(1) + "?page=" + data.group(2)
	elif a:
            text = 'http://hedgewars.org/node/' + data.group(1)
	else:
	    text = 'wut?!?'
	bot.say(text.strip())
#http://hedgewars.org/node/1146?page=2#comment-18553   
