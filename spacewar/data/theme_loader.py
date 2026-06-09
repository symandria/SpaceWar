import os
import glob
from collections import OrderedDict

import yaml

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import yaml_modifier  # noqa: E402, F401


class ThemeLoader:
    def __init__(self, settings, asset_loader):
        self._settings = settings
        self._asset_loader = asset_loader
        self.themes = OrderedDict()
        self.active_theme = None
        self.active_races = ()
        self.ships = {}

    def load_all_themes(self):
        for name in glob.glob(os.path.join(self._settings.theme_folder, "*", "theme")):
            with open(name, "r") as f:
                data = yaml.safe_load(f)
            for race in data["Races"]:
                file = os.path.join(os.path.split(name)[0], data["Races"][race])
                with open(file, "r") as f:
                    racedat = yaml.safe_load(f)
                if "phasers" not in racedat:
                    racedat["phasers"] = data["phasers"]
                if "torpedo" not in racedat:
                    racedat["torpedo"] = data["torpedo"]
                racedat["folder"] = os.path.split(file)[0]
                data["Races"][race] = racedat
            sentry = data["Special"].get("sentry", None)
            if sentry:
                file = os.path.join(os.path.split(name)[0], sentry)
                with open(file, "r") as f:
                    sentry = yaml.safe_load(f)
                if "phasers" not in sentry:
                    sentry["phasers"] = data["phasers"]
                if "torpedo" not in sentry:
                    sentry["torpedo"] = data["torpedo"]
                sentry["folder"] = os.path.split(file)[0]
                data["Special"]["sentry"] = sentry
            self.themes[os.path.basename(os.path.split(name)[0])] = data

    def activate_theme(self, theme_name):
        self.active_theme = theme_name
        self.active_races = tuple(self.themes[theme_name]["Races"])
        self._load_ship_graphics()

    def _load_ship_graphics(self):
        for race in self.active_races:
            data = self.themes[self.active_theme]["Races"][race]
            image, folder, colorkey = data["image"], data["folder"], data["colorkey"]
            self.ships[race] = self._asset_loader.load_image(
                os.path.join(folder, image), colorkey)
            if "cloaked" in data:
                self.ships["cloaked-" + race] = self._asset_loader.load_image(
                    os.path.join(folder, data["cloaked"]), colorkey)
        data = self.themes[self.active_theme]["Special"].get("sentry", None)
        if data:
            image, folder, colorkey = data["image"], data["folder"], data["colorkey"]
            self.ships["sentry"] = self._asset_loader.load_image(
                os.path.join(folder, image), colorkey)

    def get_race_data(self, race):
        if race == "sentry":
            return self.themes[self.active_theme]["Special"]["sentry"]
        return self.themes[self.active_theme]["Races"][race]

    def get_specials(self, race):
        data = self.get_race_data(race)
        return list(data.get("specials", []))

    def get_phaser_color(self, race):
        data = self.get_race_data(race)
        return data["phasers"]

    def get_torpedo_color(self, race):
        data = self.get_race_data(race)
        return data["torpedo"]

    def has_sentry(self):
        return "sentry" in self.themes[self.active_theme]["Special"]

    def get_special_options(self):
        return self.themes[self.active_theme]["Special"]
