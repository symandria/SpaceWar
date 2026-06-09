import os
import glob

from spacewar.menus.menu_actions import MenuAction
from spacewar.menus.instant_action_menu import IAChooseTheme


class MainMenu(MenuAction):
    def __call__(self):
        g = self.game
        g.instant_action = False
        g.player_character = None
        g.text_manager.active_theme = None
        g.theme_loader.active_theme = None
        g.theme_loader.active_races = ()
        return self._make_list(
            self._text("main-menu-title"),
            ("Roguelike Run", RoguelikeChooseTheme(g)),
            (self._text("menu-new character"), NewCharacterMenu(g)),
            (self._text("menu-load character"), LoadCharacterMenu(g)),
            (self._text("menu-instant action"), InstantActionMenu(g)),
            (self._text("menu-quit"), QuitAction(g)),
        )


class NewCharacterMenu(MenuAction):
    def __call__(self):
        g = self.game
        buttons = [
            (self._text("theme-" + theme), NewChooseTheme(g, theme))
            for theme in g.theme_loader.themes
        ]
        buttons.append((self._text("menu-cancel"), MainMenu(g)))
        return self._make_list(self._text("new-character-theme"), *buttons)


class NewChooseTheme(MenuAction):
    def __init__(self, game, theme):
        super().__init__(game)
        self.theme = theme

    def __call__(self):
        g = self.game
        g.theme_loader.activate_theme(self.theme)
        g.text_manager.active_theme = self.theme
        from spacewar.menus.campaign_menu import CampaignMenu
        g.player_character = g.character_manager.create_new(
            self.theme, g.theme_loader.active_races,
            g.theme_loader.has_sentry())
        g.player_character["name"] = self._text("default-captain")
        g.player_character["ship"] = self._text("default-ship")
        g.just_saved = False
        return CampaignMenu(g)()


class LoadCharacterMenu(MenuAction):
    def __call__(self):
        g = self.game
        names = glob.glob(os.path.join(g.settings.save_folder, "*.chr"))
        if names:
            buttons = [
                (os.path.splitext(os.path.basename(name))[0], LoadCharacter(g, name))
                for name in names
            ]
            buttons.append((self._text("menu-cancel"), MainMenu(g)))
            return self._make_list(self._text("load-character-title"), *buttons)
        else:
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                self._text("no-characters"), g.infofont,
                g.display.get_width(), g.settings.foreground, g.settings.background)
            return g.selection_list


class LoadCharacter(MenuAction):
    def __init__(self, game, filepath):
        super().__init__(game)
        self.filepath = filepath

    def __call__(self):
        g = self.game
        try:
            theme_name = None
            import yaml
            with open(self.filepath, "r") as f:
                data = yaml.safe_load(f)
            theme_name = data.get("theme")
            if theme_name:
                g.theme_loader.activate_theme(theme_name)
                g.text_manager.active_theme = theme_name
            g.player_character = g.character_manager.load(
                self.filepath, g.theme_loader.active_races,
                g.theme_loader.has_sentry(), g.settings.strict_stats)
            g.battle_settings = list(g.player_character.get("battle-settings",
                                     [False, ("cadet", "random"), None, None]))
            g.just_saved = True
        except Exception as err:
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                self._text("load-error") + "\n{0}: {1}".format(
                    err.__class__.__name__, err),
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
            return g.selection_list
        from spacewar.menus.campaign_menu import CampaignMenu
        return CampaignMenu(g)()


class InstantActionMenu(MenuAction):
    def __call__(self):
        g = self.game
        g.instant_action = True
        buttons = [
            (self._text("theme-" + theme), IAChooseTheme(g, theme))
            for theme in g.theme_loader.themes
        ]
        return self._make_list(
            self._text("instant-action-choose theme"), *buttons)


class RoguelikeChooseTheme(MenuAction):
    def __call__(self):
        g = self.game
        buttons = [
            (self._text("theme-" + theme), RoguelikeChooseRace(g, theme))
            for theme in g.theme_loader.themes
        ]
        buttons.append((self._text("menu-cancel"), MainMenu(g)))
        return self._make_list("Choose Theme", *buttons)


class RoguelikeChooseRace(MenuAction):
    def __init__(self, game, theme):
        super().__init__(game)
        self.theme = theme

    def __call__(self):
        g = self.game
        g.theme_loader.activate_theme(self.theme)
        g.text_manager.active_theme = self.theme
        races = g.theme_loader.active_races
        buttons = [
            (self._text(race), RoguelikeStartRun(g, race))
            for race in races
        ]
        buttons.append((self._text("menu-cancel"), MainMenu(g)))
        return self._make_list("Choose Race", *buttons)


class RoguelikeStartRun(MenuAction):
    def __init__(self, game, race):
        super().__init__(game)
        self.race = race

    def __call__(self):
        from spacewar.roguelike.run import Run
        from spacewar.states.state_machine import StateID
        g = self.game
        g.active_run = Run(self.race)
        g.state_machine.transition_to(StateID.ROGUELIKE_MAP)
        return None


class QuitAction(MenuAction):
    def __call__(self):
        self.game.quit = True
        return None
