#!/usr/local/bin/python
# coding: latin-1



from lib.bot import command
import sys, os, re, threading, imp



class still_alive(command):

    rule = r"(.*)"

    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
	text = 'This was a triumph. Im making a note here: HUGE SUCCESS. It’s hard to overstate my satisfaction. Aperture  Science: We do what we must because we can. For the good of all of us Except the ones who are dead. But theres no sense crying over every mistake You just keep on trying till you run out of cake And the science gets done and you make a neat gun For the people who are still alive. Im not even angry. Im being so sincere right now.'
	text2 = 'Even though you broke my heart and killed me. And tore me to pieces. And threw every piece into a fire. As they burned it hurt because I was so happy for you. Now these points of data make a beautiful line And were out of beta were releasing on time. So Im GLaD I got burned think of all the things we learned For the people who are still alive. Go ahead and leave me. I think I prefer to stay inside. Maybe youll find someone else to help you.'
	text3 = 'Maybe Black Mesa -THAT WAS A JOKE. HA HA, FAT CHANCE. Anyway, this cake is great: It’s so delicious and moist. Look at me still talking when theres science to do. When I look out there it makes me GLaD Im not you. Ive experiments to run there is research to be done On the people who are still alive And believe me I am still alive. Im doing science and Im still alive. I feel FANTASTIC and Im still alive. While youre dying Ill be still alive.'
	text4 = 'And when youre dead I will be still alive.' 
	text5 = 'Still alive'
	text6 = 'Still alive'	
        bot.say(text.strip())
	bot.say(text2.strip())
	bot.say(text3.strip())
	bot.say(text4.strip())
	bot.say(text5.strip())
	bot.say(text6.strip())


class want_you_gone (command):

    rule = r"(.*)"

    syntax = "echo <text>"
    doc = "echos text, only in channels"

    def run(self, bot, data):
	text = 'Well here we are again, It’s always such a pleasure, Remember when you tried to kill me twice? Oh, how we laughed and laughed, Except I wasn’t laughing, Under the circumstances I’ve been shockingly nice.'
	text2 = 'You want your freedom take it, That’s what I’m counting on, I used to want you dead but, Now I only want you gone.'
	text3 = 'She was a lot like you, (Maybe not quite as heavy), Now little Caroline is in here too. One day they woke me up, So I could live forever, It’s such a shame the same will never happen to you.'
	text4 = 'You’ve got your short, sad life left, That’s what I’m counting on, I’ll let you get right to it, Now I only want you gone.' 
	text5 = 'Goodbye, my only friend, Oh, did you think I meant you? That would be funny if it weren’t so sad, Well you have been replaced, I don’t need anyone now, When I delete you maybe I’ll stop feeling so bad.'
	text6 = 'Go make some new disaster, That’s what I’m counting on, You’re someone else’s problem,'	
	text7 = 'Now I only want you gone'
	text8 = 'Now I only want you gone'
	text9 = 'Now I only want you'
	text10 = 'Gone...'
	
	bot.say(text.strip())
	bot.say(text2.strip())
	bot.say(text3.strip())
	bot.say(text4.strip())
	bot.say(text5.strip())
	bot.say(text6.strip())
	bot.say(text7.strip())
	bot.say(text8.strip())
	bot.say(text9.strip())
	bot.say(text10.strip())





