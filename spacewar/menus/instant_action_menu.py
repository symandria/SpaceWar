import random

from spacewar.config.constants import RANKS
from spacewar.entities.ship import Ship
from spacewar.menus.menu_actions import MenuAction
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.scoring import ScoringSystem
from spacewar.ui.command_box import CommandBox


class IAChooseTheme(MenuAction):
    def __init__(self, game, theme):
        super().__init__(game)
        self.theme = theme

    def __call__(self):
        g = self.game
        g.theme_loader.activate_theme(self.theme)
        g.text_manager.active_theme = self.theme
        races = g.theme_loader.active_races
        buttons = [
            (self._text(race), IAMakePlayer(g, race))
            for race in races
        ]
        specials = g.theme_loader.get_special_options()
        for key, value in specials.items():
            if isinstance(value, (list, tuple)):
                buttons.append((
                    self._text("special-option-" + key),
                    IAMakePlayer(g, random.choice(value)),
                ))
        return self._make_list(self._text("instant-action-race select"), *buttons)


class IAMakePlayer(MenuAction):
    def __init__(self, game, race):
        super().__init__(game)
        self.race = race

    def __call__(self):
        g = self.game
        g.init_battle()
        specials = g.theme_loader.get_specials(self.race)
        player = Ship(
            self.race, HexGrid.hex_to_coords(1, 1), 180,
            RANKS[0], self._text("default-captain"), self._text("default-ship"),
            100, 10, 5, specials=specials, human=True,
            pixel_perfect=g.settings.pixel_perfect,
        )
        player.rotate(180, g.theme_loader.ships)
        b = g.battle
        b.player = player
        b.home_player = player
        b.ships.append(player)
        b.match_stats[player] = ScoringSystem.init_player_stats(
            player, g.theme_loader.active_races, g.theme_loader.has_sentry())
        g.command_box = CommandBox(
            g.display, g.infofont,
            g.settings.foreground, g.settings.background, g.text_manager)
        return self._make_list(
            self._text("instant-action-team game"),
            (self._text("menu-yes"), IAChooseTeamGame(g, True)),
            (self._text("menu-no"), IAChooseTeamGame(g, False)),
        )


class IAChooseTeamGame(MenuAction):
    def __init__(self, game, choice):
        super().__init__(game)
        self.choice = choice

    def __call__(self):
        self.game.battle.team_game = self.choice
        return self._make_list(
            self._text("instant-action-num opponents"),
            (self._text("menu-one"), IAChooseOpponents(self.game, 1)),
            (self._text("menu-two"), IAChooseOpponents(self.game, 2)),
            (self._text("menu-three"), IAChooseOpponents(self.game, 3)),
        )


class IAChooseOpponents(MenuAction):
    def __init__(self, game, num):
        super().__init__(game)
        self.num = num

    def __call__(self):
        g = self.game
        g.num_enemies = self.num
        return _build_enemy_select(g)


class IAMakeEnemy(MenuAction):
    def __init__(self, game, race):
        super().__init__(game)
        self.race = race

    def __call__(self):
        g = self.game
        b = g.battle
        if self.race == "sentry":
            e_captain = ""
            e_name = self._text("sentry")
        else:
            captain_names = self._text("captain-names-" + self.race).split("\n")
            ship_names = self._text("ship-names-" + self.race).split("\n")
            valid_captain_names = captain_names[:]
            valid_ship_names = ship_names[:]
            for ship in b.ships:
                if ship.captain in valid_captain_names:
                    valid_captain_names.remove(ship.captain)
                if ship.name in valid_ship_names:
                    valid_ship_names.remove(ship.name)
            if not valid_captain_names:
                valid_captain_names = captain_names
            if not valid_ship_names:
                valid_ship_names = ship_names
            e_captain = random.choice(valid_captain_names)
            e_name = random.choice(valid_ship_names)

        from spacewar.config.constants import GRID_ROWS, GRID_COLS_ODD, GRID_COLS_EVEN
        positions = ((GRID_ROWS, GRID_COLS_EVEN), (1, GRID_COLS_ODD), (GRID_ROWS, 1))
        pos_idx = len(b.ships) - 1
        angle = 180 if len(b.ships) == 2 and self.race != "sentry" else 0
        specials = g.theme_loader.get_specials(self.race)
        enemy = Ship(
            self.race, HexGrid.hex_to_coords(*positions[pos_idx]), angle,
            RANKS[0], e_captain, e_name,
            200 if self.race == "sentry" else 100,
            10, 0 if self.race == "sentry" else 5,
            specials=specials, pixel_perfect=g.settings.pixel_perfect,
        )
        enemy.rotate(angle, g.theme_loader.ships)
        b.ships.append(enemy)
        b.match_stats[enemy] = ScoringSystem.init_ai_stats()

        if len(b.ships) <= g.num_enemies:
            return _build_enemy_select(g)
        elif b.team_game and not any(
                s.type != b.ships[0].type for s in b.ships):
            from spacewar.ui.messagebox import Messagebox
            b.team_game = False
            g.message_box = Messagebox(
                self._text("cancel-team-game"), g.infofont,
                g.display.get_width(), g.settings.foreground, g.settings.background)
        return None


def _build_enemy_select(game):
    from spacewar.menus.menu_actions import MenuAction
    text = game.text_manager.load
    buttons = [
        (text(race), IAMakeEnemy(game, race))
        for race in game.theme_loader.active_races
    ]
    specials = game.theme_loader.get_special_options()
    if "sentry" in specials:
        buttons.append((text("special-option-sentry"), IAMakeEnemy(game, "sentry")))
    for key, value in specials.items():
        if isinstance(value, (list, tuple)):
            buttons.append((
                text("special-option-" + key),
                IAMakeEnemy(game, random.choice(value)),
            ))
    return game.make_selection_list(
        text("instant-action-ai race").format(len(game.battle.ships)),
        *buttons,
    )
