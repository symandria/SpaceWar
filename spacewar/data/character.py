import os
from collections import OrderedDict

import yaml

from spacewar.config.constants import RANKS, RANK_XP, RANK_PROMOTE, STATS


class InvalidCharacterError(Exception):
    pass


class CharacterManager:
    def __init__(self, settings):
        self._settings = settings

    def create_new(self, theme, races, has_sentry):
        char = OrderedDict((
            ("name", "Captain"),
            ("ship", "Ship"),
            ("theme", theme),
            ("race", "random"),
            ("rank", RANKS[0]),
            ("xp", 0),
            ("bonus", 0),
            ("shields", 100),
            ("weapon power", 5),
            ("engine", 5),
            ("games played", 0),
            ("phasers shot", 0),
            ("phasers hit", 0),
            ("torpedoes shot", 0),
            ("torpedoes hit", 0),
            ("average points", 0),
            ("average shields", 0),
        ))
        for race in races:
            char["kills-" + race] = 0
        if has_sentry:
            char["kills-sentry"] = 0
        return char

    def load(self, filepath, theme_races, has_sentry, strict_stats):
        with open(filepath, "r") as f:
            char = yaml.safe_load(f)
        char = OrderedDict(char) if not isinstance(char, OrderedDict) else char
        char["bonus"] = 0
        char["rank"] = RANKS[0]
        while char["rank"] in RANK_XP and char["xp"] > RANK_XP[char["rank"]]:
            char["rank"] = RANK_PROMOTE[char["rank"]]
            char["bonus"] += 5
        for stat, data in STATS.items():
            if char[stat] < data["min"] or char[stat] > data["max"] or \
                    (char[stat] - data["min"]) % data["step"]:
                raise InvalidCharacterError(
                    "invalid {0} value: {1!r}".format(stat, char[stat]))
            elif char[stat] > data["min"]:
                char["bonus"] -= (char[stat] - data["min"]) // data["step"]
        if char["bonus"] < 0:
            raise InvalidCharacterError(
                "can't have {0!r} bonus points".format(char["bonus"]))
        if strict_stats:
            for stat in list(char):
                if not stat.startswith("kills-") or stat == "kills-sentry":
                    continue
                race = stat[6:]
                if race not in theme_races:
                    del char[stat]
        for race in theme_races:
            if "kills-" + race not in char:
                char["kills-" + race] = 0
        if has_sentry:
            if "kills-sentry" not in char:
                char["kills-sentry"] = 0
        elif strict_stats:
            if "kills-sentry" in char:
                del char["kills-sentry"]
        char["savefile"] = os.path.splitext(os.path.basename(filepath))[0]
        return char

    def save(self, char, filename):
        save_char = dict(**char)
        if "battle-settings" not in save_char:
            save_char["battle-settings"] = [False, (RANKS[0], "random"), None, None]
        del save_char["rank"]
        del save_char["bonus"]
        if "savefile" in save_char:
            del save_char["savefile"]
        filepath = os.path.join(self._settings.save_folder, filename + ".chr")
        if not os.path.exists(self._settings.save_folder):
            os.mkdir(self._settings.save_folder)
        with open(filepath, "w") as f:
            yaml.safe_dump(save_char, f, indent=4)
        return filepath

    @staticmethod
    def calculate_rank(xp):
        rank = RANKS[0]
        bonus = 0
        while rank in RANK_XP and xp > RANK_XP[rank]:
            rank = RANK_PROMOTE[rank]
            bonus += 5
        return rank, bonus
