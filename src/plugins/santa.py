import base
import os.path
import pickle
import random
import time
from collections import defaultdict


class Santa(base.BotPlugin):

    admins = ("smotko", "zidar")

    ponies = set([
        "Rainbow Dash",
        "Pinkie Pie",
        "Misty Fly",
        "Lyra Heartstrings",
        "Bon Bon",
        "Vinyl Scratch",
        "Octavia Melody",
        "Rarity",
        "Fluttershy",
        "Twilight Sparkle",
        "Apple Bloom",
        "Scootaloo",
        "Applejack",
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
        "Dr. Hooves",
        "Frederick Horseshoepin",
        "Fuzzy Slippers",
        "Harry Trotter",
    ])

    def __init__(self, bot):
        super(Santa, self).__init__(bot)
        self.debug = True
        self.pickle_file = "secret_santa_stash.pkl"
        self.store = self._load_object()
        if self.store is None:
            self.store = {
                "wishes": defaultdict(list),
                "nicks": {},
                "mappings": {},
            }
            self._save_store()

    def _save_store(self, force=False):
        if not self.store.get("freeze", False) or force:
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
            time.sleep(1)
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
            "@shuffle - Assign one gift to each santa. ",
            "@show_mappings - Show who would give a gift to whom. This will",
            "    be hidden when the real santa starts.",
            "@to_whom - Show the fake nick of the person you will gift,",
            "    and their secret santa message. The debug version will also",
            "    display the real nick",
            "@freeze - Freeze the current wishes and mappings.",
            "    Can be done only by admin users.",
            "@unfreeze - Unfreeze the current wishes and mappings.",
            "    Can be done only by admin users.",
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

    def shuffle_users(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        if not self.store["wishes"]:
            self.bot.say("Can't shuffle 0 wishes", channel)
            return

        nicks = self.store["wishes"].keys()

        random.shuffle(nicks)
        self.store["nicks"] = {}
        self.store["mappings"] = {}
        for i, nick in enumerate(nicks):
            self.get_pony_name(nick)
            self.store["mappings"][nick] = nicks[(i + 1) % len(nicks)]

        self._save_store()
        self.bot.say("{} wishes were assigned".format(len(nicks)), channel)

    def show_mappings(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        if not self.debug:
            self.bot.say("This only works in debug mode, sorry.", channel)
            return

        if not self.store["mappings"]:
            self.bot.say("Wishes have not yet been assigned.", channel)
            return

        self.bot.say("These are the actual nicks that will be used", channel)
        self.bot.say("The follwing gifts will be given (fake nicks):", channel)
        for giver, reciever in sorted(self.store["mappings"].items()):
            p_from = "{} ({})".format(self.get_pony_name(giver), giver)
            p_to = "{} ({})".format(self.get_pony_name(reciever), reciever)
            self.bot.say("from: {} - to: {}".format(p_from, p_to), channel)
            time.sleep(1)

    def freeze(self, tokens, nick, channel, msg, line):
        if nick not in self.admins:
            self.bot.say("I can't let you do that dave", channel)
            return
        if self.store.get("freeze", False):
            self.bot.say("Already frozen, nothing to do here.", channel)
        else:
            self.store["freeze"] = True
            self._save_store(force=True)
            self.bot.say("The hell has frozen.", channel)


    def unfreeze(self, tokens, nick, channel, msg, line):
        if nick not in self.admins:
            self.bot.say("I can't let you do that dave", channel)
            return
        if self.store.get("freeze", False):
            self.store["freeze"] = False
            self._save_store(force=True)
            self.bot.say("Global warming did its thing.", channel)
        else:
            self.bot.say("Nothing was frozen to begin with.", channel)

    def to_whom(self, tokens, nick, channel, msg, line):
        self.record_messae = False
        if not self.store["mappings"]:
            self.bot.say("Wishes have not yet been assigned.", nick)
            return

        if nick not in self.store["mappings"]:
            self.bot.say("You do not have an assigned wish, "
                         "If you are participating, then this is "
                         "a bad error.", nick)
            return

        to = self.store["mappings"][nick]
        if self.debug:
            pony_name = "{} ({})".format(self.get_pony_name(to), to)

        self.bot.say("You will make {} really happy.".format(pony_name), nick)
        self.bot.say("Their message is:", nick)
        self._say_lines(self.store["wishes"][to], nick)

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

        self.handle_tokens(msg, ('shuffle',), self.shuffle_users,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('freeze',), self.freeze,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('unfreeze',), self.unfreeze,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('to_whom',), self.to_whom,
                           nick, channel, msg, line)

        self.handle_tokens(msg, ('show_mappings',), self.show_mappings,
                           nick, channel, msg, line)

        if self.record_messae and "PRIVMSG" in line:
            self.append_wish(nick, msg)

        if self.debug and "debug" in msg:
            print "#"*80
            import json
            print json.dumps(self.store, indent=4, sort_keys=True)
            print "#"*80

    def get_pony_name(self, nick):
        if nick not in self.store["nicks"]:
            taken_nicks = set(self.store["nicks"].values())
            possible_nicks = self.ponies.difference(taken_nicks)
            self.store["nicks"][nick] = random.sample(possible_nicks, 1)[0]
            self._save_store()
        return self.store["nicks"][nick]

    def append_wish(self, nick, msg):
        self.store["wishes"][nick].append(msg)
        self._save_store()
