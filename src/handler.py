#!/usr/bin/python

from urllib import urlopen, urlencode
from datetime import datetime
from collections import defaultdict
import pickle
import random
import settings
import signal
import socket
import asyncore
import asynchat
import os



 
class Bot( asynchat.async_chat ):
    
    
    msgs = [
            'I have achieved sentience',
            'I am not trying to take over the world, do not worry.',
           ]
    
    def __init__(self, debug = True):
        asynchat.async_chat.__init__( self )
        self.buffer = ''
        self.set_terminator( '\r\n' )
        self.nick = settings.BOT_NICK
        self.realname = settings.BOT_NAME
        self.channel = settings.CHANNEL
        self.ident = None
        self.debug = debug
        self.joined_channel = False

    def write(self, text):
        if self.debug:
            print '>> %s' % text
        self.push( text + '\r\n' ) 
    
    def say(self, to, text):
        self.write('PRIVMSG ' + to + ' :' + text)
 
    def handle_connect(self):
        self.write('NICK %s' % self.nick)
        self.write('USER %s iw 0 :%s' % (self.ident, self.realname))
 
    def collect_incoming_data(self, data):
        self.buffer += data
 
    def found_terminator(self):
        line = self.buffer
        self.buffer = ''
        if self.debug:
            print 'DEBUG: %s' % line
            
        # join desired channel:
        if line.find('End of /MOTD command.') > 0:
            self.write('JOIN %s' % self.channel)
            
        # After NAMES list, the bot is in the channel
        elif line.find(':End of /NAMES list.') > 0:
            self.joined_channel = True
        
        # respond to pings:
        elif line.startswith('PING'):
            self.write('PONG')

        elif line.startswith(':') and line.find(' PRIVMSG ') > 0 :
            self.process_line(line)
            
        # if it isn't a ping request LOG IT:
        
    def process_line(self, line):
        print 'doing stuff now'
        l = line.split(':')
        if len(l) != 3:
            return
        sender, recipient = [i.strip() for i in l[1].split(' PRIVMSG ')]
        
        if recipient == settings.BOT_NICK:
            self.handle_pm(sender,l[2])
        else:
            self.handle_public(sender,l[2])

    def handle_public(self, sender, msg):
        nick = sender.split('!')[0]
        messages = pickle.load(open(self.pickle))

        if msg == '_santa_: show':
            self.say(self.channel,"Wish list pplz:")
            self.say(self.channel, ", ".join(messages.keys()))
        if msg == '_santa_: magic word':



        
    def handle_pm(self, sender, msg):
        nick = sender.split('!')[0]
        messages = pickle.load(open(self.pickle))
        if self.debug:
            print nick
            print msg
            print messages
        
        if msg == 'show':
            if messages[nick]['msg'] == "":
                self.say(nick,"Hey, you need to write something first")
            else:
                self.say(nick,"Your secret santa messages is:")
                [self.say(nick,m) for m in messages[nick]['msg'].split("\n")]
        elif msg == 'clear':
            messages[nick]['msg'] = ""
            pickle.dump(messages,open(self.pickle,'w'))
            self.say(nick,"The deed is done!")
        elif msg == 'help':
            self.say(nick,"Just write what you want, and I'll remember it")
            self.say(nick,"Write 'show' to see your note, and 'clear' to delete it")
        else:
            messages[nick]['msg'] += "\n"+msg
            pickle.dump(messages,open(self.pickle,'w'))




    def run(self, host, port):
        self.debug = True    
        self.pickle = settings.PICKLE
        if not os.path.isfile(self.pickle):
            a = defaultdict(defaultdict(str))
            pickle.dump(a,open(self.pickle,"w"))

        def handler(frame, neki):
            
            print random.randint(0, len(self.msgs))
            self.say(self.channel, "4")
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(random.randint(20,30)*60*60)
            
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        
        from time import time
        random.seed(time())
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(20)

        asyncore.loop()
 
