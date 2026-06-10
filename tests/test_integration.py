import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
pygame.display.init()
pygame.display.set_mode((160, 160))

from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.scoring import ScoringSystem
from spacewar.systems.movement import MovementSystem
from spacewar.systems.collision import CollisionSystem
from spacewar.systems.combat import CombatSystem
from spacewar.systems.ai import AISystem
from spacewar.systems.teleportation import TeleportationSystem
from spacewar.systems.cloaking import CloakingSystem
from spacewar.systems.regeneration import RegenerationSystem
from spacewar.systems.death import DeathSystem
from spacewar.systems.turn_resolution import TurnResolver
from spacewar.systems.visibility import VisibilitySystem
from spacewar.systems.map_effects import MapEffectsSystem
from spacewar.systems.weapons import WeaponType, get_weapon_damage
from spacewar.components.race_configs import build_race_loadout, RACE_COMPONENT_OVERRIDES
from spacewar.components.base import ComponentSlot
from spacewar.entities.map_object import Asteroid, NebulaTile
from spacewar.entities.mine import Mine
from spacewar.rendering.viewport import Viewport
from spacewar.config.constants import GRID_ROWS, GRID_COLS_ODD, max_col


class _DummyAssetLoader:
    def play_sound(self, name): pass
    def load_image(self, name, colorkey=None):
        return pygame.Surface((9, 9))


class _DummyThemeLoader:
    active_races = ('test',)
    def get_phaser_color(self, race): return (255, 0, 0)
    def get_torpedo_color(self, race): return (0, 255, 0)


def _make_ship(race, row, col, human=False):
    loadout = build_race_loadout(race)
    ship = Ship(race, HexGrid.hex_to_coords(row, col), 180,
                'cadet', 'C', 'S', 100, 10, 5,
                loadout=loadout, human=human, pixel_perfect=False)
    ship.image = pygame.Surface((9, 9))
    return ship


class TestFullBattleTurn:
    def test_run_multiple_turns(self):
        asset_loader = _DummyAssetLoader()
        theme_loader = _DummyThemeLoader()
        mov = MovementSystem()
        col = CollisionSystem()
        combat = CombatSystem(asset_loader, theme_loader)
        ai = AISystem()
        tp = TeleportationSystem()
        cloak = CloakingSystem()
        regen = RegenerationSystem()
        death = DeathSystem()
        scoring = ScoringSystem()
        resolver = TurnResolver(mov, col, combat, ai, tp, cloak, regen,
                                death, scoring, asset_loader)

        class Battle:
            ships = []
            dead_ships = []
            torpedoes = []
            mines = []
            wrecks = []
            match_stats = {}
            team_game = False
            player = None

        b = Battle()
        player = _make_ship('federation', 5, 5, human=True)
        enemy = _make_ship('klingon', 10, 10)
        b.ships = [player, enemy]
        b.player = player
        b.match_stats[player] = ScoringSystem.init_player_stats(
            player, ('test',), False)
        b.match_stats[enemy] = ScoringSystem.init_ai_stats()

        sprites = {'federation': pygame.Surface((9, 9)),
                   'klingon': pygame.Surface((9, 9)),
                   'cloaked-klingon': pygame.Surface((9, 9))}

        for turn in range(5):
            player.movement = (6, 5)
            player.action = "weapon_1"
            player.target = (10, 10)
            resolver.begin_turn(b, sprites)
            while resolver.is_active:
                resolver.tick(b)

        assert len(b.ships) >= 1


class TestAllRacesInBattle:
    def test_each_race_can_fight(self):
        for race in RACE_COMPONENT_OVERRIDES:
            if race == "sentry":
                continue
            ship = _make_ship(race, 7, 5, human=True)
            assert ship.max_shields == 100
            assert ship.max_hull == 50
            assert ship.weapon_power == 10
            assert not ship.is_dead()

            loadout = ship.loadout
            assert loadout.is_valid()
            assert loadout.get_weapon(1) is not None
            assert loadout.get_weapon(2) is not None


class TestVisibilityIntegration:
    def test_sensor_cone_directional(self):
        vis = VisibilitySystem()
        ship = _make_ship('federation', 14, 11)
        visible = vis.compute_visible_hexes(ship)
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        assert ship_hex in visible
        assert len(visible) > 10

    def test_cloaked_ship_invisible(self):
        vis = VisibilitySystem()
        observer = _make_ship('federation', 14, 11)
        target = _make_ship('klingon', 15, 11)
        target.cloaked = True
        target.shot_recently = 0
        assert not vis.can_see(observer, target)


class TestMapObjectIntegration:
    def test_asteroid_blocks_movement(self):
        ast = Asteroid((7, 5))
        assert ast.hull == 100
        ast.apply_damage(50)
        assert ast.hull == 50
        assert not ast.is_dead()
        ast.apply_damage(51)
        assert ast.is_dead()

    def test_nebula_effects_in_sequence(self):
        effects = MapEffectsSystem()
        ship = _make_ship('federation', 7, 5)
        ship.shields = 50

        green_neb = NebulaTile((7, 5), NebulaTile.GREEN)
        nebulae = {(7, 5): green_neb}
        effects.apply_movement_effects(ship, [(7, 5)], nebulae)
        assert ship.shields > 50

        ship.shields = 100
        red_neb = NebulaTile((8, 5), NebulaTile.RED)
        nebulae[(8, 5)] = red_neb
        effects.apply_movement_effects(ship, [(8, 5)], nebulae)
        total = ship.shields + ship.hull
        assert total < 150


class TestViewportIntegration:
    def test_viewport_tracks_player(self):
        vp = Viewport()
        ship = _make_ship('federation', 14, 11)
        vp.update(ship.pos)
        rect = vp.get_view_rect()
        assert rect.width == 160
        assert rect.height == 160
        ship_screen = vp.world_to_screen(ship.pos)
        assert 0 <= ship_screen[0] < 160
        assert 0 <= ship_screen[1] < 160

    def test_viewport_roundtrip(self):
        vp = Viewport()
        ship = _make_ship('federation', 14, 11)
        vp.update(ship.pos)
        screen = vp.world_to_screen(ship.pos)
        world = vp.screen_to_world(screen)
        assert abs(world[0] - ship.pos[0]) < 1
        assert abs(world[1] - ship.pos[1]) < 1


class TestWeaponDamageIntegration:
    def test_all_weapons_deal_positive_damage(self):
        for wtype in WeaponType:
            dmg = get_weapon_damage(wtype, 10)
            assert dmg > 0, f"{wtype} deals 0 damage at wp=10"

    def test_mine_placement_and_trigger(self):
        mine = Mine((50, 50), None, 16)
        assert mine.active
        mine.detonate()
        assert not mine.active
