from lib.bot import command

import lib.irc as irc
import random 
import datetime

class LMGTFY(command):

    ##rule = r"(.*)"
    rule = r"\s+(.*)"	
    syntax = "LMGTFY [search term]"
    doc = "let me gogole that for you"

    def run(self, bot, data):
        text = 'http://lmgtfy.com/?q='+data.group(1)	
	#text =  'http://vanillaresults.com/?q='+data.group(1)
        if not text:
            text = "Error nothing to search"
        bot.say(text.strip())

class GIFY(command):

    ##rule = r"(.*)"
    rule = r"\s+(.*)"	
    syntax = "GIFY [search term]"
    doc = "Google It For Yourself"

    def run(self, bot, data):
        #text = 'http://lmgtfy.com/?q='+data.group(1)	
	text =  'http://vanillaresults.com/?q='+data.group(1)
        if not text:
            text = "Error nothing to search"
        bot.say(text.strip())
