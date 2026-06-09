import random

import pygame
import pygame.gfxdraw

from spacewar.config.constants import (
    RANKS, STATS, SCREEN_SIZE, GRID_ROWS, GRID_COLS_ODD, GRID_COLS_EVEN, max_col,
)
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
from spacewar.states.roguelike_states import RoguelikeMapState, RoguelikeNodeState
from spacewar.ui.selection_list import SelectionList
from spacewar.ui.infobox import Infobox
from spacewar.ui.command_box import CommandBox
from spacewar.ui.minimap import Minimap
from spacewar.rendering.viewport import Viewport, VIEWPORT_SIZE
from spacewar.entities.map_object import Asteroid, NebulaTile
from spacewar.components.race_configs import build_race_loadout
from spacewar.systems.visibility import VisibilitySystem


class BattleState:
    def __init__(self):
        self.ships = []
        self.dead_ships = []
        self.torpedoes = []
        self.mines = []
        self.asteroids = []
        self.nebulae = []
        self.nebulae_by_hex = {}
        self.wrecks = []
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

        self.world_surface = pygame.Surface(SCREEN_SIZE)
        self.screen = pygame.Surface(VIEWPORT_SIZE)
        self.background = self.hex_grid.build_background()
        self.viewport = Viewport()

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
        self.visibility_system = VisibilitySystem()
        self.minimap = Minimap(48, 40)
        self.turn_resolver = TurnResolver(
            self.movement_system, self.collision_system, self.combat_system,
            self.ai_system, self.teleportation_system, self.cloaking_system,
            self.regeneration_system, self.death_system, self.scoring_system,
            self.asset_loader,
        )

        self.battle = None
        self.player_character = None
        self.instant_action = False
        self.active_run = None
        self.roguelike_battle_config = None
        self.roguelike_shop_items = None
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
        sm.register(StateID.ROGUELIKE_MAP, RoguelikeMapState(self))
        sm.register(StateID.ROGUELIKE_NODE, RoguelikeNodeState(self))

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

        loadout = build_race_loadout(race)
        player = Ship(
            race, HexGrid.hex_to_coords(1, 1), 180,
            pc["rank"], pc["name"], pc["ship"],
            pc["shields"], pc["weapon power"],
            pc["engine"], loadout=loadout, human=True,
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

                e_loadout = build_race_loadout(slot_race)
                positions = ((GRID_ROWS, GRID_COLS_EVEN), (1, GRID_COLS_ODD), (GRID_ROWS, 1))
                angle = 180 if i == 1 else 0
                enemy = Ship(
                    slot_race, HexGrid.hex_to_coords(*positions[i]), angle,
                    rank, random.choice(valid_captains), random.choice(valid_ships),
                    stats["shields"], stats["weapon power"],
                    stats["engine"], loadout=e_loadout,
                    pixel_perfect=self.settings.pixel_perfect,
                )
                enemy.rotate(angle, self.theme_loader.ships)
                b.ships.append(enemy)
                b.match_stats[enemy] = ScoringSystem.init_ai_stats()
            elif slot == "sentry":
                sentry_loadout = build_race_loadout("sentry")
                positions = ((GRID_ROWS, GRID_COLS_EVEN), (1, GRID_COLS_ODD), (GRID_ROWS, 1))
                enemy = Ship(
                    "sentry", HexGrid.hex_to_coords(*positions[i]), 0,
                    RANKS[0], "", self.text_manager.load("sentry"),
                    200, 10, 0, loadout=sentry_loadout,
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
        self._spawn_map_objects(b)
        self.just_saved = False
        self.selection_list = None

    def _spawn_map_objects(self, battle):
        occupied = set()
        for ship in battle.ships:
            h = HexGrid.coords_to_hex(ship.pos)
            if h:
                occupied.add(h)

        asteroid_count = random.randint(3, 8)
        for _ in range(asteroid_count):
            for attempt in range(20):
                row = random.randint(3, GRID_ROWS - 2)
                col = random.randint(2, max_col(row) - 1)
                if (row, col) not in occupied:
                    battle.asteroids.append(Asteroid((row, col)))
                    occupied.add((row, col))
                    break

        nebula_types = [NebulaTile.RED, NebulaTile.GREEN, NebulaTile.PURPLE]
        for ntype in nebula_types:
            center_row = random.randint(5, GRID_ROWS - 4)
            center_col = random.randint(3, max_col(center_row) - 2)
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    r, c = center_row + dr, center_col + dc
                    if r < 1 or r > GRID_ROWS or c < 1 or c > max_col(r):
                        continue
                    if (r, c) in occupied:
                        continue
                    neb = NebulaTile((r, c), ntype)
                    battle.nebulae.append(neb)
                    battle.nebulae_by_hex[(r, c)] = neb
                    occupied.add((r, c))

    def _render_fog(self, player, view_rect):
        clear, shaded, fog = self.visibility_system.get_fog_data(player)
        fog_surface = pygame.Surface(VIEWPORT_SIZE, pygame.SRCALPHA)
        for hx in shaded:
            wx, wy = HexGrid.hex_to_coords(*hx)
            sx = wx - view_rect.left
            sy = wy - view_rect.top
            if -10 < sx < VIEWPORT_SIZE[0] + 10 and -10 < sy < VIEWPORT_SIZE[1] + 10:
                fog_surface.fill((0, 0, 0, 100),
                                 (sx - 1, sy - 1, 11, 11))
        for hx in fog:
            wx, wy = HexGrid.hex_to_coords(*hx)
            sx = wx - view_rect.left
            sy = wy - view_rect.top
            if -10 < sx < VIEWPORT_SIZE[0] + 10 and -10 < sy < VIEWPORT_SIZE[1] + 10:
                fog_surface.fill((0, 0, 0, 200),
                                 (sx - 1, sy - 1, 11, 11))
        self.screen.blit(fog_surface, (0, 0))

    def render_battle(self, draw_phasers=None, show_invalid_destinations=False):
        if draw_phasers is None:
            draw_phasers = []
        b = self.battle
        if not b:
            return

        ws = self.world_surface
        move_time = self.turn_resolver.move_time
        if move_time == 0 and not draw_phasers:
            ws.fill(self.settings.background)
        else:
            ws.blit(self.background, (0, 0))

        if show_invalid_destinations and b.player:
            for row in range(1, GRID_ROWS + 1):
                for column in range(1, max_col(row) + 1):
                    if not b.player.get_valid_destination(
                            row, column, bool(b.player.action)):
                        x, y = HexGrid.hex_to_coords(row, column)
                        ws.blit(self.hex_grid.invalid_surface, (x - 1, y - 1))

        for neb in b.nebulae:
            neb.render(ws)
        for ast in b.asteroids:
            ast.render(ws)

        if b.selected:
            ws.blit(
                self.hex_grid.select_surface,
                (int(b.selected.pos[0]) - 1, int(b.selected.pos[1]) - 1))

        for wreck in b.wrecks:
            wreck.render(ws)

        for mine in b.mines:
            mine.render(ws)

        for torp in b.torpedoes:
            torp.render(ws)

        for phaser in draw_phasers:
            pygame.draw.line(ws, *phaser)

        for ship in b.ships:
            if ship == b.player:
                continue
            visible = (not ship.cloaked or ship.shot_recently or
                       ship.explode or not b.player or
                       (b.team_game and ship.type == b.player.type))
            if visible:
                ship.render(ws)

        if b.player:
            b.player.render(ws)
            if b.player.movement and move_time == 0:
                start = (int(b.player.pos[0]) + 4, int(b.player.pos[1]) + 4)
                dest = HexGrid.hex_to_coords(*b.player.movement)
                end = (dest[0] + 4, dest[1] + 4)
                pygame.draw.line(ws, (0, 180, 255), start, end, 1)
                pygame.draw.circle(ws, (0, 180, 255), end, 3, 1)

        for ship in b.ships:
            if ship.teleport_target:
                if move_time > 80:
                    radius = move_time - 80
                else:
                    radius = 80 - move_time
                if radius > 0:
                    pygame.gfxdraw.filled_circle(
                        ws, int(ship.pos[0]) + 4, int(ship.pos[1]) + 4,
                        radius, (0, 255, 0))

        if b.player:
            self.viewport.update(b.player.pos, b.player.vision_forward)
        view_rect = self.viewport.get_view_rect()
        self.screen.blit(ws, (0, 0), view_rect)

        if b.player and move_time == 0:
            self._render_fog(b.player, view_rect)

        if b.player:
            titlebar = f"H:{b.player.hull} S:{b.player.shields} Spd:{b.player.speed}"
        else:
            titlebar = self.text_manager.load("titlebar-no-player")
        self.screen.blit(self.small_font.render(
            titlebar, True, self.settings.foreground, self.settings.background), (0, 0))

        pygame.transform.scale(self.screen, self.settings.window_size, self.display)

        if b.player:
            mm_scale = max(2, self.settings.window_multiplier)
            mm_w = self.minimap.width * mm_scale
            mm_h = self.minimap.height * mm_scale
            mm_x = self.settings.window_size[0] - mm_w - 4
            mm_y = 4
            self.minimap.render(self.display, b, self.viewport.get_view_rect(),
                                mm_x, mm_y)
            scaled = pygame.transform.scale(self.minimap.surface, (mm_w, mm_h))
            self.display.blit(scaled, (mm_x, mm_y))

        if b.info_target:
            if self.infobox and self.infobox.target == b.info_target:
                self.infobox.update()
            else:
                is_ally = (b.info_target == b.player or
                           (b.team_game and b.player and
                            b.info_target.type == b.player.type))
                self.infobox = Infobox(
                    b.info_target, self.infofont,
                    self.settings.foreground, self.settings.background,
                    self.text_manager, is_ally=is_ally)
            ib = self.infobox
            screen_pos = self.viewport.world_to_screen(
                (int(b.info_target.pos[0]) + 10, int(b.info_target.pos[1])))
            ib.rect.left = int(screen_pos[0]) * self.settings.window_multiplier
            ib.rect.top = int(screen_pos[1]) * self.settings.window_multiplier
            if ib.rect.right > self.settings.window_size[0]:
                alt_x = self.viewport.world_to_screen(
                    (int(b.info_target.pos[0]) - 1, 0))[0]
                ib.rect.right = int(alt_x) * self.settings.window_multiplier
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
