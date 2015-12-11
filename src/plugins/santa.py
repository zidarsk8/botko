from base import BotPlugin
from datetime import timedelta
from os import popen
import os.path
import pickle
from collections import defaultdict

import time


class Santa(BotPlugin):

    def __init__(self, bot):
        super(Santa, self).__init__(bot)
        self.pickle_file = "secret_santa_stash.pkl"
        self.store = self._load_object()
        if self.store is None:
            self.store = defaultdict(list)
            self._save_store()

    def _save_store(self):
        self._save_object(self.store)

    def _save_object(self, obj):
        with open(self.pickle_file, "w") as output:
            pickle.dump(obj, output)

    def _load_object(self):
        if not os.path.isfile(self.pickle_file):
            return None
        with open(self.pickle_file, "r") as output:
            return pickle.load(output)


    def say_help(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        self.bot.say("echo: {}".format(msg), channel)


    def show(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        if not self.store[nick]:
            self.bot.say("Nothing has been said yet.", nick)
        else:
            self.bot.say("Your secret santa message is:", nick)
        for line in self.store[nick]:
            time.sleep(0.5)
            self.bot.say(line, nick)

    def handle_message(self, channel, nick, msg, line=None):
        self.record_messae = False
        if not channel:
            channel = nick
            self.record_messae = True

        self.handle_tokens(msg, ('help',), self.say_help,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('show',), self.show,
                           nick, channel, msg, line)

        if self.record_messae:
            self._append_user_message(nick, msg)


    def _append_user_message(self, nick, msg):
        self.store[nick].append(msg)
        self._save_store()
