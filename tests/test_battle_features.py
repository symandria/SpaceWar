"""Tests for battle features: mines, map effects, harvesting, shops,
AI sensor limits, and terrain generation."""
import pygame
import pytest

from spacewar.components.base import Component, ComponentSlot
from spacewar.entities.map_object import (
    Asteroid, NebulaTile, Anomaly, NEBULA_DESCRIPTIONS,
)
from spacewar.entities.mine import Mine
from spacewar.entities.ship import Ship
from spacewar.entities.wreck import Wreck
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.ai import AISystem
from spacewar.systems.combat import CombatSystem
from spacewar.systems.harvest import HarvestSystem, roll_asteroid_resource
from spacewar.systems.map_effects import MapEffectsSystem


class _SilentAssets:
    def play_sound(self, name):
        pass


class _Battle:
    def __init__(self, ships=()):
        self.ships = list(ships)
        self.dead_ships = []
        self.torpedoes = []
        self.mines = []
        self.asteroids = []
        self.nebulae = []
        self.nebulae_by_hex = {}
        self.wrecks = []
        self.anomalies = []
        self.match_stats = {}
        self.harvested = {"scrap": 0, "materials": {}, "components": []}
        self.tier = 1
        self.team_game = False
        self.player = None
        self.home_player = None


def _ship(race="federation", row=7, col=5, human=False):
    ship = Ship(race, HexGrid.hex_to_coords(row, col), 0,
                "cadet", "Cap", "Ship", 100, 10, 5,
                human=human, pixel_perfect=False)
    ship.image = pygame.Surface((9, 9))
    return ship


class TestMines:
    def _setup(self, owner_hex=(7, 5), mine_hex=(7, 6)):
        owner = _ship(row=owner_hex[0], col=owner_hex[1])
        mine = Mine(
            (HexGrid.hex_to_coords(*mine_hex)[0] + 4,
             HexGrid.hex_to_coords(*mine_hex)[1] + 4),
            owner, 60)
        return owner, mine

    def test_mine_unarmed_next_to_owner(self):
        owner, mine = self._setup()
        combat = CombatSystem(_SilentAssets(), None)
        combat.update_mines([mine], [owner], {}, False, owner, _SilentAssets())
        assert not mine.armed
        assert mine.active
        assert owner.shields == 100

    def test_mine_arms_when_owner_leaves(self):
        owner, mine = self._setup()
        owner.pos = HexGrid.hex_to_coords(7, 9)
        combat = CombatSystem(_SilentAssets(), None)
        combat.update_mines([mine], [owner], {}, False, owner, _SilentAssets())
        assert mine.armed
        assert mine.active  # owner out of trigger radius

    def test_armed_mine_detonates_on_any_ship_including_owner(self):
        owner, mine = self._setup()
        mine.armed = True  # already armed from a previous turn
        mines = [mine]
        combat = CombatSystem(_SilentAssets(), None)
        combat.update_mines(mines, [owner], {}, False, owner, _SilentAssets())
        assert not mine.active
        assert not mines
        assert owner.shields == 100 - 60

    def test_mine_proximity_triggers_within_one_hex(self):
        owner, mine = self._setup(owner_hex=(20, 5), mine_hex=(7, 6))
        intruder = _ship(race="klingon", row=7, col=7)  # 1 hex from mine
        combat = CombatSystem(_SilentAssets(), None)
        combat.update_mines([mine], [owner, intruder], {}, False, owner,
                            _SilentAssets())
        assert not mine.active
        assert intruder.shields < 100

    def test_mine_can_drop_on_own_square(self):
        owner = _ship(row=7, col=5)
        combat = CombatSystem(_SilentAssets(), None)
        mines = []
        combat.place_mine(owner, (7, 5), mines)
        assert len(mines) == 1
        assert mines[0].hex_pos == (7, 5)
        # Unarmed while owner stands on it; arms after leaving.
        combat.update_mines(mines, [owner], {}, False, owner, _SilentAssets())
        assert not mines[0].armed
        owner.pos = HexGrid.hex_to_coords(7, 9)
        combat.update_mines(mines, [owner], {}, False, owner, _SilentAssets())
        assert mines[0].armed


class TestMapEffects:
    def test_green_nebula_heals_when_traversed(self):
        fx = MapEffectsSystem()
        ship = _ship()
        ship.shields = 50
        nebulae = {(7, 6): NebulaTile((7, 6), NebulaTile.GREEN)}
        fx.apply_movement_effects(ship, [(7, 5), (7, 6), (7, 7)], nebulae)
        assert ship.shields == 50 + int(ship.max_shields * 0.05)

    def test_red_nebula_damages_when_traversed(self):
        fx = MapEffectsSystem()
        ship = _ship()
        nebulae = {(7, 6): NebulaTile((7, 6), NebulaTile.RED)}
        fx.apply_movement_effects(ship, [(7, 6)], nebulae)
        assert ship.shields < 100

    def test_plasma_burns_hull_through_shields(self):
        fx = MapEffectsSystem()
        ship = _ship()
        nebulae = {(7, 6): NebulaTile((7, 6), NebulaTile.PLASMA)}
        fx.apply_movement_effects(ship, [(7, 6)], nebulae)
        assert ship.shields == 100  # untouched
        assert ship.hull < ship.max_hull

    def test_ion_storm_drains_shields_and_decloaks(self):
        fx = MapEffectsSystem()
        ship = _ship(race="klingon")
        ship.cloaked = True
        sprites = {"klingon": pygame.Surface((9, 9)),
                   "cloaked-klingon": pygame.Surface((9, 9))}
        nebulae = {(7, 5): NebulaTile((7, 5), NebulaTile.ION)}
        fx.apply_end_of_turn_effects(ship, nebulae, sprites)
        assert ship.shields == 100 - int(ship.max_shields * 0.10)
        assert not ship.cloaked

    def test_static_cloud_halves_vision(self):
        from spacewar.systems.visibility import VisibilitySystem
        fx = MapEffectsSystem()
        ship = _ship()
        nebulae = {(7, 5): NebulaTile((7, 5), NebulaTile.STATIC)}
        fx.apply_end_of_turn_effects(ship, nebulae)
        assert ship.sensor_static
        vis = VisibilitySystem()
        clear, shaded = vis.compute_visibility(ship)
        ship.sensor_static = False
        full_clear, _ = vis.compute_visibility(ship)
        assert len(clear) < len(full_clear)

    def test_tachyon_stream_resets_cooldowns(self):
        fx = MapEffectsSystem()
        ship = _ship()
        ship.teleport_cooldown = 3
        ship.phasing_cooldown = 2
        nebulae = {(7, 5): NebulaTile((7, 5), NebulaTile.TACHYON)}
        fx.apply_end_of_turn_effects(ship, nebulae)
        assert ship.teleport_cooldown == 0
        assert ship.phasing_cooldown == 0

    def test_gravity_rift_pulls_ships_closer(self):
        fx = MapEffectsSystem()
        ship = _ship(row=7, col=7)
        battle = _Battle([ship])
        rift_hex = (7, 5)
        battle.nebulae_by_hex[rift_hex] = NebulaTile(rift_hex, NebulaTile.GRAVITY)
        before = HexGrid.hex_distance(
            HexGrid.coords_to_hex(ship.pos), rift_hex)
        fx.apply_gravity(battle)
        after = HexGrid.hex_distance(
            HexGrid.coords_to_hex(ship.pos), rift_hex)
        assert after < before

    def test_all_nebula_types_have_descriptions(self):
        for ntype in NebulaTile.COLORS:
            assert ntype in NEBULA_DESCRIPTIONS


class TestHarvest:
    def _player_with_target(self, target):
        ship = _ship(human=True)
        ship.target = target
        return ship

    def test_harvest_asteroid_resource(self):
        hs = HarvestSystem()
        ship = self._player_with_target((7, 6))
        battle = _Battle([ship])
        ast = Asteroid((7, 6), resource=("scrap", 30))
        battle.asteroids.append(ast)
        assert hs.process(ship, battle, _SilentAssets())
        assert battle.harvested["scrap"] == 30
        assert ast.resource is None  # spot disappears

    def test_harvest_out_of_range_fails(self):
        hs = HarvestSystem()
        ship = self._player_with_target((7, 9))  # 4 hexes away
        battle = _Battle([ship])
        battle.asteroids.append(Asteroid((7, 9), resource=("scrap", 30)))
        assert not hs.process(ship, battle, _SilentAssets())
        assert battle.harvested["scrap"] == 0

    def test_harvest_wreck_gives_component_and_materials(self):
        hs = HarvestSystem()
        ship = self._player_with_target((7, 6))
        battle = _Battle([ship])
        wreck = Wreck((7, 6), "klingon", "captain")
        battle.wrecks.append(wreck)
        assert hs.process(ship, battle, _SilentAssets())
        assert wreck.salvaged
        assert battle.harvested["components"]
        assert battle.harvested["materials"].get("common", 0) >= 1

    def test_harvest_anomaly_gives_exotic_gear(self):
        hs = HarvestSystem()
        ship = self._player_with_target((7, 6))
        battle = _Battle([ship])
        anomaly = Anomaly((7, 6), quality=2)
        battle.anomalies.append(anomaly)
        assert hs.process(ship, battle, _SilentAssets())
        assert anomaly.looted
        assert len(battle.harvested["components"]) == 1

    def test_resource_roll_valid(self):
        for _ in range(50):
            kind, amount = roll_asteroid_resource(2)
            assert kind in ("scrap", "common", "uncommon", "rare")
            assert amount >= 1


class TestAnomalyLoot:
    def test_generates_component(self):
        from spacewar.roguelike.loot import generate_anomaly_component
        for _ in range(30):
            comp = generate_anomaly_component(2, quality=2)
            assert comp is not None
            assert "Anomalous" in comp.name


class TestAISensors:
    def test_cannot_target_beyond_sensor_range(self):
        ai = AISystem()
        hunter = _ship(race="klingon", row=7, col=5)
        prey = _ship(row=25, col=5)  # 18 hexes away, vision is 14
        nearest = ai._find_nearest_enemy(hunter, [prey])
        assert nearest is None

    def test_targets_within_sensor_range(self):
        ai = AISystem()
        hunter = _ship(race="klingon", row=7, col=5)
        prey = _ship(row=10, col=5)
        nearest = ai._find_nearest_enemy(hunter, [prey])
        assert nearest is prey

    def test_neutral_shop_ignored_and_idle(self):
        ai = AISystem()
        shop = _ship(race="sentry", row=10, col=10)
        shop.is_shop = True
        shop.hostile = False
        raider = _ship(race="klingon", row=10, col=11)
        ai.decide_actions([shop, raider], None, False)
        assert shop.action is None
        assert shop.movement is None
        # Raider had only the shop nearby -> nothing to shoot at.
        assert raider.action not in ("weapon_1", "weapon_2") or \
            raider.target != HexGrid.coords_to_hex(shop.pos)

    def test_hostile_shop_fights_back(self):
        ai = AISystem()
        shop = _ship(race="sentry", row=10, col=10)
        shop.is_shop = True
        shop.hostile = True
        raider = _ship(race="klingon", row=10, col=11)
        ai.decide_actions([shop, raider], None, False)
        assert shop.action == "weapon_2"
        assert shop.target == HexGrid.coords_to_hex(raider.pos)


class TestTerrainGeneration:
    def test_environments_have_labels_and_weights(self):
        from spacewar.roguelike.encounters import ENVIRONMENTS
        for key, env in ENVIRONMENTS.items():
            assert env.get("label")
            assert env.get("weight", 0) >= 1
            assert "asteroids" in env

    def test_asteroid_field_density(self):
        from spacewar.roguelike.encounters import ENVIRONMENTS
        # ~600 hexes on the board; fields should cover roughly 5-10%.
        assert ENVIRONMENTS["asteroid_field"]["asteroids"][0] >= 30
        assert ENVIRONMENTS["dense_field"]["asteroids"][1] >= 60

    def test_clear_space_not_harvestable_but_more_foes(self):
        from spacewar.roguelike.encounters import ENVIRONMENTS
        clear = ENVIRONMENTS["clear"]
        assert not clear["harvestable"]
        assert clear["extra_enemies"] >= 1
        for key, env in ENVIRONMENTS.items():
            if key != "clear":
                assert env["harvestable"], f"{key} should be harvestable"

    def test_sector_rows_offer_choices(self):
        from spacewar.roguelike.sector_map import SectorMap
        from spacewar.roguelike.encounters import NodeType
        for _ in range(10):
            sm = SectorMap()
            sm.generate(1)
            rows = sm.get_display_data()
            for row_idx, nodes in rows.items():
                if row_idx == 0 or any(
                        n.node_type == NodeType.BOSS for n in nodes):
                    continue
                assert 2 <= len(nodes) <= 3

    def test_combat_nodes_have_environment(self):
        from spacewar.roguelike.sector_map import SectorMap
        from spacewar.roguelike.encounters import NodeType, ENVIRONMENTS
        sm = SectorMap()
        sm.generate(1)
        for node in sm.nodes.values():
            if node.node_type in (NodeType.BATTLE, NodeType.ELITE,
                                  NodeType.BOSS):
                assert node.environment in ENVIRONMENTS
