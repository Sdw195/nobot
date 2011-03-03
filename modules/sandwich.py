from lib.bot import command

import lib.irc as irc
import random 
import datetime

class sandwich(command):
 
    rule = r"\s+(.*)"
 
    syntax = ""
    doc = ""
 
    def run(self, bot, data):
	

 
 
        topping = random.choice(['avocado','lettuce','tomato','mozzarella cheese','bacon','spam','peanutbutter','bratwurst','cruelty-free PeTA-approved fake guinea-pig','digital','cucumber','tofu','-if slightly burnt-','recursive','banana','ice-cream','ham&jam','tuna','double cheese','olive','..erm.. just','self-made','generic','sand','witch','two-hander'])
 
        ## lets rename `a' to something more legible
        receiver = data.group(1)
 
        ## just because we are curious, lets us see who receiver is
        ##bot.say("Receiver is %s" % receiver)
 
        if receiver == "Sdw195": 
            topping = 'BBBBBBLT'
        if receiver == "sheepluva":
            topping = 'roast lamb'
 
        ## instead of using data.group(1) here again, we might as well use `receiver'
        text = '\x01ACTION gives ' + receiver + ' a ' + topping + ' sandwich\x01'
 	##bot.say("\x01ACTION gives %s a %s\x01" % (receiver, topping))
        bot.say(text.strip())
