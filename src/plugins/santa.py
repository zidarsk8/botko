import base
import os.path
import pickle
import random
import time
from collections import defaultdict
from datetime import timedelta
from os import popen


class Santa(base.BotPlugin):

    ponies = set([
        "Rainbow Dash",
        "Rarity",
        "Twilight Sparkle",
        "Apple Bloom",
        "Scootaloo",
        "Sweetie Belle",
        "Cheerilee",
        "Junebug",
        "Tree Hugger",
        "Big McIntosh",
        "Cheese Sandwich",
        "Double Diamond",
        "Filthy Rich",
        "Cloud Chaser",
        "Daring Do",
        "Derpy",
        "Flash Sentry",
        "Flitter",
        "Night Glider",
        "Spitfire",
        "Fancy Pants",
        "King Sombra",
        "Moon Dancer",
        "Shining Armor",
        "Sunset Shimmer",
        "Princess Cadance",
        "Princess Celestia",
        "Princess Luna",
        "Diamond Tiara",
        "Marble Pie",
        "Limestone Pie",
        "Maud Pie",
    ])

    def __init__(self, bot):
        super(Santa, self).__init__(bot)
        self.pickle_file = "secret_santa_stash.pkl"
        self.store = self._load_object()
        if self.store is None:
            self.store = {
                "wishes": defaultdict(list),
                "nicks": {},
            }
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

    def _say_lines(self, lines, channel):
        for line in lines:
            time.sleep(0.5)
            self.bot.say(line, channel)

    def say_help(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        help_message = [
            "This your personal secret santa",
            "To register for the third anal secret santa, you just have to",
            "tell me your wish in a PM. If you delete your wish with you will",
            "be removed from the secret santa cirle.",
            "-----------------",
            "Possible commands:",
            "@help - You're looking at it.",
            "@show - Show your current wish.",
            "@delete - Delete your current wish.",
            "@list - List of secret santa users. ",
        ]
        self._say_lines(help_message, channel)


    def show_wish(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        if not self.store["wishes"][nick]:
            self.bot.say("Nothing has been said yet.", nick)
        else:
            self.bot.say("Your secret santa message is:", nick)
        self._say_lines(self.store["wishes"][nick], nick)

    def delete_wish(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        if nick in self.store["wishes"]:
            del self.store["wishes"][nick]
            self._save_store()
        self.bot.say("Your secret santa wish has been removed", nick)

    def list_users(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        users = self.store["wishes"].keys()
        if users:
            self.bot.say("Users with a santa wish", channel)
            self.bot.say(", ".join(users), channel)
        else:
            self.bot.say("There aren't any secret santas yet.", channel)


    def handle_message(self, channel, nick, msg, line=None):
        self.record_messae = False
        if not channel:
            channel = nick
            self.record_messae = True

        self.handle_tokens(msg, ('help',), self.say_help,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('show',), self.show_wish,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('delete',), self.delete_wish,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('list',), self.list_users,
                           nick, channel, msg, line)

        if self.record_messae:
            self.append_wish(nick, msg)

    def _add_nick_mapping(self, nick):
        if nick in self.store["nicks"]:
            return
        taken_nicks = set(self.store["nicks"].values())
        possible_nicks = self.ponies.difference(taken_nicks)
        self.store["nicks"][nick]= random.sample(possible_nicks, 1)[0]

    def append_wish(self, nick, msg):
        self.store["wishes"][nick].append(msg)
        self._add_nick_mapping(nick)
        self._save_store()
