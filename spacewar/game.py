import random

import pygame
import pygame.gfxdraw

from spacewar.config.constants import RANKS, STATS, SCREEN_SIZE, GRID_ROWS, max_col
from spacewar.config.settings import GameSettings
from spacewar.data.asset_loader import AssetLoader
from spacewar.data.localization import TextManager
from spacewar.data.theme_loader import ThemeLoader
from spacewar.data.character import CharacterManager
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.rendering.renderer import GameRenderer
from spacewar.systems.movement import MovementSystem
from spacewar.systems.collision import CollisionSystem
from spacewar.systems.combat import CombatSystem
from spacewar.systems.ai import AISystem
from spacewar.systems.teleportation import TeleportationSystem
from spacewar.systems.cloaking import CloakingSystem
from spacewar.systems.regeneration import RegenerationSystem
from spacewar.systems.death import DeathSystem
from spacewar.systems.scoring import ScoringSystem
from spacewar.systems.turn_resolution import TurnResolver
from spacewar.states.state_machine import StateMachine, StateID
from spacewar.states.menu_states import MenuState
from spacewar.states.battle_states import (
    BattleIdleState, CommandEntryState, DestinationSelectState, TargetSelectState,
)
from spacewar.states.resolution_states import (
    TurnResolutionState, SpectatingState, GameOverState,
)
from spacewar.ui.selection_list import SelectionList
from spacewar.ui.infobox import Infobox
from spacewar.ui.command_box import CommandBox


class BattleState:
    def __init__(self):
        self.ships = []
        self.dead_ships = []
        self.torpedoes = []
        self.match_stats = {}
        self.team_game = False
        self.player = None
        self.home_player = None
        self.selected = None
        self.info_target = None


class Game:
    def __init__(self):
        pygame.display.init()
        self.settings = GameSettings()

        try:
            pygame.mixer.init(44100, buffer=1024)
        except pygame.error:
            self.settings.sound_enabled = False

        if self.settings.fullscreen:
            self.display = pygame.display.set_mode(
                self.settings.window_size, pygame.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode(self.settings.window_size)

        self.asset_loader = AssetLoader(self.settings)
        pygame.display.set_icon(self.asset_loader.load_image(self.settings.icon_file))
        pygame.display.set_caption(self.settings.window_caption)

        self.text_manager = TextManager(self.settings)
        self.theme_loader = ThemeLoader(self.settings, self.asset_loader)
        self.theme_loader.load_all_themes()
        self.character_manager = CharacterManager(self.settings)

        self.hex_grid = HexGrid(self.settings.foreground, self.settings.background)
        self.renderer = GameRenderer(self.settings, self.hex_grid)

        self.screen = pygame.Surface(SCREEN_SIZE)
        self.background = self.hex_grid.build_background()

        pygame.font.init()
        self.small_font = pygame.font.SysFont("Courier New,Liberation Mono", 12)
        self.infofont = pygame.font.SysFont(
            "Courier New,Liberation Mono", self.settings.font_size, bold=True)

        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(300, 30)

        self.movement_system = MovementSystem()
        self.collision_system = CollisionSystem()
        self.combat_system = CombatSystem(self.asset_loader, self.theme_loader)
        self.ai_system = AISystem()
        self.teleportation_system = TeleportationSystem()
        self.cloaking_system = CloakingSystem()
        self.regeneration_system = RegenerationSystem()
        self.death_system = DeathSystem()
        self.scoring_system = ScoringSystem()
        self.turn_resolver = TurnResolver(
            self.movement_system, self.collision_system, self.combat_system,
            self.ai_system, self.teleportation_system, self.cloaking_system,
            self.regeneration_system, self.death_system, self.scoring_system,
            self.asset_loader,
        )

        self.battle = None
        self.player_character = None
        self.instant_action = False
        self.just_saved = False
        self.battle_settings = [False, (RANKS[0], "random"), None, None]
        self.num_enemies = 1
        self.quit = False

        self.selection_list = None
        self.message_box = None
        self.text_entry = None
        self.command_box = None
        self.infobox = None

        self.state_machine = StateMachine()
        self._register_states()

        from spacewar.menus.main_menu import MainMenu
        self.selection_list = MainMenu(self)()
        self.state_machine.transition_to(StateID.MAIN_MENU)

    def _register_states(self):
        sm = self.state_machine
        sm.register(StateID.MAIN_MENU, MenuState(self))
        sm.register(StateID.CAMPAIGN_MENU, MenuState(self))
        sm.register(StateID.BATTLE_IDLE, BattleIdleState(self))
        sm.register(StateID.COMMAND_ENTRY, CommandEntryState(self))
        sm.register(StateID.DESTINATION_SELECT, DestinationSelectState(self))
        sm.register(StateID.TARGET_SELECT, TargetSelectState(self))
        sm.register(StateID.TURN_RESOLUTION, TurnResolutionState(self))
        sm.register(StateID.SPECTATING, SpectatingState(self))
        sm.register(StateID.GAME_OVER, GameOverState(self))

    def make_selection_list(self, title, *buttons):
        return SelectionList(
            title, self.infofont,
            self.settings.foreground, self.settings.background,
            self.display.get_width(), *buttons,
        )

    def init_battle(self):
        self.battle = BattleState()

    def start_campaign_battle(self):
        self.init_battle()
        b = self.battle
        pc = self.player_character
        races = self.theme_loader.active_races
        race = pc["race"]
        specials_map = self.theme_loader.get_special_options()
        if race in specials_map and isinstance(specials_map[race], (list, tuple)):
            race = random.choice(specials_map[race])

        specials = self.theme_loader.get_specials(race)
        player = Ship(
            race, HexGrid.hex_to_coords(1, 1), 180,
            pc["rank"], pc["name"], pc["ship"],
            pc["shields"], pc["weapon power"],
            pc["engine"], specials=specials, human=True,
            pixel_perfect=self.settings.pixel_perfect,
        )
        player.rotate(180, self.theme_loader.ships)
        b.player = player
        b.home_player = player
        b.ships.append(player)
        b.match_stats[player] = ScoringSystem.init_player_stats(
            player, races, self.theme_loader.has_sentry())

        self.command_box = CommandBox(
            self.display, self.infofont,
            self.settings.foreground, self.settings.background, self.text_manager)

        for i, slot in enumerate(self.battle_settings[1:]):
            if slot and slot != "sentry":
                rank, slot_race = slot
                if slot_race in specials_map and isinstance(specials_map[slot_race], (list, tuple)):
                    slot_race = random.choice(specials_map[slot_race])
                if rank == "random":
                    rank = RANKS[random.randint(0, 10)]
                points = RANKS.index(rank) * 5
                stats = {}
                for stat, data in STATS.items():
                    stats[stat] = data["min"]
                while points:
                    available = [s for s, d in STATS.items() if stats[s] < d["max"]]
                    upgrade = random.choice(available)
                    stats[upgrade] += STATS[upgrade]["step"]
                    points -= 1

                captain_names = self.text_manager.load("captain-names-" + slot_race).split("\n")
                ship_names = self.text_manager.load("ship-names-" + slot_race).split("\n")
                valid_captains = captain_names[:]
                valid_ships = ship_names[:]
                for ship in b.ships:
                    if ship.captain in valid_captains:
                        valid_captains.remove(ship.captain)
                    if ship.name in valid_ships:
                        valid_ships.remove(ship.name)
                if not valid_captains:
                    valid_captains = captain_names
                if not valid_ships:
                    valid_ships = ship_names

                e_specials = self.theme_loader.get_specials(slot_race)
                positions = ((14, 10), (1, 11), (14, 1))
                angle = 180 if i == 1 else 0
                enemy = Ship(
                    slot_race, HexGrid.hex_to_coords(*positions[i]), angle,
                    rank, random.choice(valid_captains), random.choice(valid_ships),
                    stats["shields"], stats["weapon power"],
                    stats["engine"], specials=e_specials,
                    pixel_perfect=self.settings.pixel_perfect,
                )
                enemy.rotate(angle, self.theme_loader.ships)
                b.ships.append(enemy)
                b.match_stats[enemy] = ScoringSystem.init_ai_stats()
            elif slot == "sentry":
                e_specials = self.theme_loader.get_specials("sentry")
                positions = ((14, 10), (1, 11), (14, 1))
                enemy = Ship(
                    "sentry", HexGrid.hex_to_coords(*positions[i]), 0,
                    RANKS[0], "", self.text_manager.load("sentry"),
                    200, 10, 0, specials=e_specials,
                    pixel_perfect=self.settings.pixel_perfect,
                )
                enemy.rotate(0, self.theme_loader.ships)
                b.ships.append(enemy)
                b.match_stats[enemy] = ScoringSystem.init_ai_stats()

        b.team_game = self.battle_settings[0]
        if b.team_game and not any(
                s.type != "sentry" and s.type != b.ships[0].type for s in b.ships):
            b.team_game = False
            from spacewar.ui.messagebox import Messagebox
            self.message_box = Messagebox(
                self.text_manager.load("cancel-team-game"), self.infofont,
                self.display.get_width(), self.settings.foreground,
                self.settings.background)
        self.just_saved = False
        self.selection_list = None

    def render_battle(self, draw_phasers=None, show_invalid_destinations=False):
        if draw_phasers is None:
            draw_phasers = []
        b = self.battle
        if not b:
            return

        move_time = self.turn_resolver.move_time
        if move_time == 0 and not draw_phasers:
            self.screen.fill(self.settings.background)
        else:
            self.screen.blit(self.background, (0, 0))

        if show_invalid_destinations and b.player:
            for row in range(1, GRID_ROWS + 1):
                for column in range(1, max_col(row) + 1):
                    if not b.player.get_valid_destination(
                            row, column, bool(b.player.action)):
                        x, y = HexGrid.hex_to_coords(row, column)
                        self.screen.blit(self.hex_grid.invalid_surface, (x - 1, y - 1))

        if b.selected:
            self.screen.blit(
                self.hex_grid.select_surface,
                (int(b.selected.pos[0]) - 1, int(b.selected.pos[1]) - 1))

        for torp in b.torpedoes:
            torp.render(self.screen)

        for phaser in draw_phasers:
            pygame.draw.line(self.screen, *phaser)

        for ship in b.ships:
            if ship == b.player:
                continue
            visible = (not ship.cloaked or ship.shot_recently or
                       ship.explode or not b.player or
                       (b.team_game and ship.type == b.player.type))
            if visible:
                ship.render(self.screen)

        if b.player:
            b.player.render(self.screen)

        for ship in b.ships:
            if ship.teleport_target:
                if move_time > 80:
                    radius = move_time - 80
                else:
                    radius = 80 - move_time
                if radius > 0:
                    pygame.gfxdraw.filled_circle(
                        self.screen, int(ship.pos[0]) + 4, int(ship.pos[1]) + 4,
                        radius, (0, 255, 0))

        if b.player:
            titlebar = self.text_manager.load("titlebar").format(
                shields=b.player.shields, speed=b.player.speed)
        else:
            titlebar = self.text_manager.load("titlebar-no-player")
        self.screen.blit(self.small_font.render(
            titlebar, True, self.settings.foreground, self.settings.background), (0, 0))

        pygame.transform.scale(self.screen, self.settings.window_size, self.display)

        if b.info_target:
            if self.infobox and self.infobox.target == b.info_target:
                self.infobox.update()
            else:
                self.infobox = Infobox(
                    b.info_target, self.infofont,
                    self.settings.foreground, self.settings.background,
                    self.text_manager)
            ib = self.infobox
            ib.rect.left *= self.settings.window_multiplier
            ib.rect.top *= self.settings.window_multiplier
            if ib.rect.right > self.settings.window_size[0]:
                ib.rect.right = (int(b.info_target.pos[0]) - 1) * self.settings.window_multiplier
            if ib.rect.bottom > self.settings.window_size[1]:
                ib.rect.bottom = self.settings.window_size[1]
            ib.render(self.display)

        if self.selection_list:
            self.selection_list.render(self.display)
        if self.text_entry:
            self.text_entry.update(self.display.get_width(), self.display.get_height())
            self.text_entry.render(self.display)
        if self.message_box:
            self.message_box.render(self.display)

    def run(self):
        take_screenshot = False
        while not self.quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F4 and event.mod & pygame.KMOD_ALT:
                        self.quit = True
                        break
                    elif event.key == pygame.K_F12:
                        take_screenshot = True
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        if not self.text_entry:
                            self.quit = True
                            break
                self.state_machine.handle_event(event)

            if self.quit:
                break

            self.state_machine.update()
            self.state_machine.render()

            pygame.display.flip()
            if take_screenshot:
                GameRenderer.take_screenshot(self.display)
                take_screenshot = False
            self.clock.tick(30)

        pygame.quit()
