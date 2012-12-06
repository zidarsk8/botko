#!/usr/bin/python

from urllib import urlopen, urlencode
from datetime import datetime
from collections import defaultdict
import random
import pickle
import random
import settings
import signal
import socket
import asyncore
import asynchat
import os
import time


 
class Bot( asynchat.async_chat ):
    
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
        time.sleep(5)
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
        if len(l) < 3:
            return
        msg = ":".join(l[2:])
        sender, recipient = [i.strip() for i in l[1].split(' PRIVMSG ')]
        
        if recipient == settings.BOT_NICK:
            self.handle_pm(sender,msg)
        else:
            self.handle_public(sender,msg)

    def handle_public(self, sender, msg):
        nick = sender.split('!')[0]
        messages = pickle.load(open(self.pickle))
        if self.debug:
            print 'public'
            print nick
            print msg

        if msg.replace(':','') == '_santa_ show':
            print 'santa show now !!',self.channel
            self.say(self.channel,"People who want stuff:")
            self.say(self.channel, ", ".join(messages.keys()))
        if msg.replace(':','') == '_santa_ magic word':
            self.calcMapping(messages)
            pickle.dump(messages,open(self.pickle,'w'))
        if msg.replace(':','') == '_santa_ help':
            self.writeHelp()
        if msg.replace(':','') == '_santa_ mapping':
            self.say(self.channel,"Previos mapping was:" )
            for i,j in messages.items():
                self.say(self.channel,"#%4d -> #%4d" % (j['id'], j['to']) )
            self.calcMapping(messages)
            pickle.dump(messages,open(self.pickle,'w'))

    def calcMapping(self, messages):
        for i,j in messages.items():
            messages[i]['id'] = self.getNewId(messages)
        an = [a['id'] for a in messages.values()]
        sn = list(an)

        while sum([an[i]==sn[i] for i in range(len(an))]) > 0 and len(an) > 1:
            random.shuffle(sn)
        idmap = {an[i]:sn[i] for i in range(len(an))}
        for ni, val in messages.items():
            messages[ni]['to'] = idmap[messages[ni]['id']]
        
        pickle.dump(messages,open(self.pickle,'w'))
        print messages

        [self.sendMessageTo(messages, nick) for nick in messages.keys()]
       
    def sendMessageTo(self, messages, nick ):
        toid = messages[nick]['to']
        self.say(nick, "Your task is to make %s happy! See hint below:" % toid)
        tonick = {j['id']:i for i,j in messages.items()}[toid]

        [self.say(nick,'> '+m) for m in messages[tonick]['msg'].split("\n")]

    def getNewId(self, messages):
        used = set([a['id'] for a in messages.values() if 'id' in a])
        d = int(random.random()*1000)
        m = 1000
        while d in used:
            d = int(random.random()*m)
            m += 1
        return d
        
    def handle_pm(self, sender, msg):
        nick = sender.split('!')[0]
        messages = pickle.load(open(self.pickle))
        if self.debug:
            print "DEBUG PM - ", msg
            print messages

        if nick not in messages:
            messages[nick] = {'id':0,'msg':'','to':0}
        
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
            self.writeHelp()
        elif msg == 'to whom':
            self.say(nick,"you will deliver your package to subject #%d" % \
                    messages[nick]['to'])
        else:
            messages[nick]['msg'] += "\n"+msg
            pickle.dump(messages,open(self.pickle,'w'))


    def writeHelp(self):
        h = '''
            Global commands in the form of "_santa_ <command>":
            .    help - you're looking at it, why would you need to know what this command does!
            .    mapping - show current id mapping
            .    show - lists all users participating in this secret santa thingy
            .    magic word - gives users an id and does the mappig
            . 
            PM commands:
            .    show - shows you your current secret santa message
            .    clear - clears your current message
            .    help - shows this text
            .    to whom - shows you an id if your recipient
            .    <anything else> - will get appended to your secret santa message
        '''
        [self.say(self.channel,m.strip()) for m in h.split("\n")]




    def run(self, host, port):
        self.debug = True    
        self.pickle = settings.PICKLE
        if not os.path.isfile(self.pickle):
            a = defaultdict(dict)
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

