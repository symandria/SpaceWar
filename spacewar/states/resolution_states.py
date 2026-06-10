import pygame

from spacewar.rendering.hex_grid import HexGrid
from spacewar.states.state_machine import GameState, StateID


class TurnResolutionState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.draw_phasers = []

    def handle_event(self, event):
        return None

    def update(self):
        g = self.game
        tr = g.turn_resolver
        self.draw_phasers = tr.tick(g.battle)
        if not tr.is_active:
            result_text, game_over = g.scoring_system.calculate_results(
                g.battle.ships, g.battle.dead_ships, g.battle.match_stats,
                g.battle.team_game, g.battle.home_player,
                g.instant_action, g.player_character, g.text_manager)
            if game_over:
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    result_text, g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
                return StateID.GAME_OVER
            elif g.battle.player is None:
                return StateID.SPECTATING
            else:
                return StateID.BATTLE_IDLE
        return None

    def render(self):
        self.game.render_battle(draw_phasers=self.draw_phasers)


class SpectatingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.rapid_end = False

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP:
            return None
        g = self.game
        if g.message_box:
            g.message_box = None
            return None
        if g.selection_list:
            for button in g.selection_list:
                if button.rect.collidepoint(event.pos):
                    g.selection_list = button.callback()
                    return None
            return None
        pos = event.pos[0] // g.settings.window_multiplier, \
            event.pos[1] // g.settings.window_multiplier
        thex = HexGrid.coords_to_hex(pos)
        if thex:
            for ship in g.battle.ships:
                if thex == HexGrid.coords_to_hex(ship.pos) and not ship.cloaked:
                    if g.battle.selected == ship:
                        g.battle.selected = None
                        g.battle.info_target = None
                    else:
                        g.battle.selected = ship
                        g.battle.info_target = ship
                    return None

        def rapid_end_callback():
            self.rapid_end = True

        def start_turn_action():
            g.turn_resolver.begin_turn(g.battle, g.theme_loader.ships)
            return None

        g.selection_list = g.make_selection_list(
            g.text_manager.load("after-death-menu"),
            (g.text_manager.load("process-turn"), start_turn_action),
            (g.text_manager.load("fast-forward"), rapid_end_callback),
            (g.text_manager.load("return-to-board"), lambda: None),
        )
        return None

    def update(self):
        g = self.game
        if g.turn_resolver.is_active:
            draw_phasers = g.turn_resolver.tick(g.battle)
            result_text, game_over = g.scoring_system.calculate_results(
                g.battle.ships, g.battle.dead_ships, g.battle.match_stats,
                g.battle.team_game, g.battle.home_player,
                g.instant_action, g.player_character, g.text_manager)
            if game_over:
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    result_text, g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
                return StateID.GAME_OVER
            return None
        if self.rapid_end and not g.message_box and not g.selection_list:
            g.turn_resolver.begin_turn(g.battle, g.theme_loader.ships)
        return None

    def render(self):
        self.game.render_battle()


class GameOverState(GameState):
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP:
            return None
        g = self.game
        if g.message_box:
            g.message_box = None
            return None

        if g.active_run:
            run = g.active_run
            player_won = any(s == g.battle.home_player for s in g.battle.ships)
            enemies_killed = sum(
                1 for s in g.battle.dead_ships
                if s != g.battle.home_player and s.type != "sentry")
            player_hull = g.battle.home_player.hull if g.battle.home_player else 0
            player_shields = g.battle.home_player.shields if g.battle.home_player else 0

            loot = run.apply_battle_results(
                player_won, enemies_killed, player_hull, player_shields)

            g.battle = None
            if not run.alive:
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    f"DEFEAT\n\nYour ship was destroyed.\n\n"
                    f"Battles won: {run.battles_won}\n"
                    f"Total kills: {run.total_kills}\n"
                    f"Scrap collected: {run.inventory.scrap}",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
                g.active_run = None
                from spacewar.menus.main_menu import MainMenu
                g.selection_list = MainMenu(g)()
                return StateID.MAIN_MENU
            elif loot:
                from spacewar.roguelike.loot import format_loot
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    f"Battle Complete!\n\n{format_loot(loot)}",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
            return StateID.ROGUELIKE_MAP

        g.battle = None
        if g.instant_action:
            from spacewar.menus.main_menu import MainMenu
            g.selection_list = MainMenu(g)()
        else:
            from spacewar.menus.campaign_menu import CampaignMenu
            g.selection_list = CampaignMenu(g)()
        return StateID.MAIN_MENU

    def update(self):
        return None

    def render(self):
        self.game.render_battle()
