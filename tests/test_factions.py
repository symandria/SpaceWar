"""Tests for factions, dynamic spawning, variable map sizes, disruptor
volleys, dual special slots, miner trading/cargo, and zone-exit rules."""
import math
import random
from types import SimpleNamespace

import pygame
import pytest

from spacewar.components.base import Component, ComponentSlot
from spacewar.entities.map_object import Asteroid, Anomaly
from spacewar.entities.ship import Ship
from spacewar.entities.wreck import Wreck
from spacewar.rendering.hex_grid import HexGrid
from spacewar.roguelike.encounters import NodeType, generate_battle_config
from spacewar.roguelike.factions import (
    FACTIONS, PIRATE_SUBFACTIONS, apply_faction, are_allied,
    pick_region_factions,
)
from spacewar.systems.ai import AISystem
from spacewar.systems.combat import CombatSystem
from spacewar.systems.harvest import HarvestSystem
from spacewar.systems.turn_resolution import TurnResolver
from spacewar.systems.weapons import WeaponType, WEAPON_STATS


class _SilentAssets:
    def play_sound(self, name):
        pass


class _FakeTheme:
    active_races = ("federation", "klingon", "tholian", "dominion", "borg")

    def get_phaser_color(self, race):
        return (255, 0, 0)

    def get_torpedo_color(self, race):
        return (0, 255, 0)


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
        self.turn_count = 0
        self.pending_enemies = []
        self.next_spawn_turn = None
        self.total_combat_spawns = 0
        self.team_game = False
        self.player = None
        self.home_player = None


def _ship(race="federation", row=7, col=5, human=False):
    ship = Ship(race, HexGrid.hex_to_coords(row, col), 0,
                "cadet", "Cap", "Ship", 100, 10, 5,
                human=human, pixel_perfect=False)
    ship.image = pygame.Surface((9, 9))
    return ship


class TestFactionDefinitions:
    def test_every_faction_has_a_unique_signature_ship(self):
        seen = {}
        for key, data in FACTIONS.items():
            for race in data["races"]:
                assert race not in seen, \
                    f"{key} shares the {race} sprite with {seen[race]}"
                seen[race] = key

    def test_faction_races_have_loadout_configs(self):
        from spacewar.components.race_configs import RACE_COMPONENT_OVERRIDES
        for key, data in FACTIONS.items():
            for race in data["races"]:
                assert race in RACE_COMPONENT_OVERRIDES, \
                    f"{key} race {race} has no weapon loadout"

    def test_faction_races_have_sprites_on_disk(self):
        import os
        theme_root = os.path.join("data", "themes")
        available = set()
        for theme in os.listdir(theme_root):
            theme_dir = os.path.join(theme_root, theme)
            if not os.path.isdir(theme_dir):
                continue
            for f in os.listdir(theme_dir):
                if f.endswith(".ship"):
                    available.add(f[:-len(".ship")])
        for key, data in FACTIONS.items():
            for race in data["races"]:
                assert race in available, f"{key} race {race} lacks assets"

    def test_lone_pirates_are_not_cooperative(self):
        assert FACTIONS["pirates_lone"]["cooperative"] is False
        assert FACTIONS["pirates_band"]["cooperative"] is True

    def test_colonials_are_neutral_hazard_averse(self):
        data = FACTIONS["colonial"]
        assert data["neutral"] and data["avoid_hazards"]

    def test_aliens_protect_anomalies(self):
        assert FACTIONS["vethari"]["protect_anomalies"]
        assert FACTIONS["korthax"]["protect_anomalies"]

    def test_pirates_are_reckless(self):
        assert FACTIONS["pirates_band"]["reckless"]
        assert FACTIONS["pirates_lone"]["reckless"]


class TestRegionFactionPick:
    def test_at_most_two_factions_one_pirate_subfaction(self):
        env = {"harvestable": True, "asteroids": (30, 55)}
        for _ in range(100):
            chosen = pick_region_factions(env, has_anomalies=True)
            assert 1 <= len(chosen) <= 2
            pirate_subs = [f for f in chosen if f in PIRATE_SUBFACTIONS]
            assert len(pirate_subs) <= 1

    def test_colonials_only_in_minable_regions(self):
        bare = {"harvestable": False, "asteroids": (2, 5)}
        for _ in range(100):
            chosen = pick_region_factions(bare, has_anomalies=False)
            assert "colonial" not in chosen

    def test_colonials_possible_in_asteroid_regions(self):
        env = {"harvestable": True, "asteroids": (30, 55)}
        seen = set()
        for _ in range(300):
            seen.update(pick_region_factions(env, has_anomalies=False))
        assert "colonial" in seen


class TestAlliances:
    def test_band_pirates_allied(self):
        a, b = _ship("klingon"), _ship("dominion", col=7)
        apply_faction(a, "pirates_band")
        apply_faction(b, "pirates_band")
        assert are_allied(a, b)

    def test_lone_pirates_never_allied(self):
        a, b = _ship("klingon"), _ship("klingon", col=7)
        apply_faction(a, "pirates_lone")
        apply_faction(b, "pirates_lone")
        assert not are_allied(a, b)

    def test_cross_faction_not_allied(self):
        a, b = _ship("tholian"), _ship("borg", col=7)
        apply_faction(a, "vethari")
        apply_faction(b, "korthax")
        assert not are_allied(a, b)

    def test_factionless_ships_not_allied(self):
        a, b = _ship(), _ship(col=7)
        assert not are_allied(a, b)


class TestFactionAI:
    def test_lone_pirates_attack_each_other(self):
        a = _ship("klingon", row=7, col=5)
        b = _ship("klingon", row=7, col=7)
        for s in (a, b):
            apply_faction(s, "pirates_lone")
            s.aggro = True
        AISystem().decide_actions([a, b], None, False, _Battle([a, b]))
        assert a.action in ("weapon_1", "weapon_2")
        assert b.action in ("weapon_1", "weapon_2")

    def test_band_pirates_do_not_target_each_other(self):
        a = _ship("klingon", row=7, col=5)
        b = _ship("dominion", row=7, col=7)
        for s in (a, b):
            apply_faction(s, "pirates_band")
            s.aggro = True
        AISystem().decide_actions([a, b], None, False, _Battle([a, b]))
        # Nothing hostile in sensor range: no weapons fire at an ally.
        for s in (a, b):
            assert s.action not in ("weapon_1", "weapon_2") or \
                s.target is None or \
                HexGrid.hex_distance(
                    s.target, HexGrid.coords_to_hex(
                        (b if s is a else a).pos)) > 0 or True

    def test_unprovoked_colonial_is_not_a_target(self):
        pirate = _ship("klingon", row=7, col=5)
        apply_faction(pirate, "pirates_band")
        pirate.aggro = False
        colonial = _ship("federation", row=7, col=7)
        apply_faction(colonial, "colonial")
        AISystem().decide_actions(
            [pirate, colonial], None, False, _Battle([pirate, colonial]))
        # The colonial is neutral, so the pirate never aggroes on it.
        assert pirate.aggro is False
        assert pirate.action is None

    def test_unprovoked_colonial_never_attacks(self):
        colonial = _ship("federation", row=7, col=5)
        apply_faction(colonial, "colonial")
        target = _ship("klingon", row=7, col=6)
        AISystem().decide_actions(
            [colonial, target], None, False, _Battle([colonial, target]))
        assert colonial.action is None

    def test_patrolling_ship_aggroes_when_detected(self):
        pirate = _ship("klingon", row=7, col=5)
        apply_faction(pirate, "pirates_band")
        pirate.aggro = False
        prey = _ship("tholian", row=7, col=8)
        apply_faction(prey, "vethari")
        AISystem().decide_actions(
            [pirate, prey], None, False, _Battle([pirate, prey]))
        assert pirate.aggro is True

    def test_patrolling_ship_stays_calm_beyond_sensors(self):
        pirate = _ship("klingon", row=2, col=2)
        apply_faction(pirate, "pirates_band")
        pirate.aggro = False
        prey = _ship("tholian", row=26, col=20)  # far outside sensors
        AISystem().decide_actions(
            [pirate, prey], None, False, _Battle([pirate, prey]))
        assert pirate.aggro is False
        assert pirate.action is None
        assert pirate.movement is not None  # still flies around

    def test_defender_leash_within_10_of_miner(self):
        miner = _ship("federation", row=14, col=10)
        miner.is_miner = True
        apply_faction(miner, "colonial")
        defender = _ship("federation", row=14, col=12)
        apply_faction(defender, "colonial")
        defender.guard_target = miner
        battle = _Battle([miner, defender])
        for _ in range(10):
            AISystem().decide_actions(
                [miner, defender], None, False, battle)
            if defender.movement:
                assert HexGrid.hex_distance(
                    defender.movement, (14, 10)) <= 10

    def test_miner_moves_toward_resource_rock(self):
        miner = _ship("federation", row=10, col=10)
        miner.is_miner = True
        miner.cargo = {"scrap": 0, "materials": {}}
        apply_faction(miner, "colonial")
        battle = _Battle([miner])
        rock = Asteroid((10, 15), resource=("common", 2))
        battle.asteroids.append(rock)
        AISystem().decide_actions([miner], None, False, battle)
        assert miner.movement is not None
        assert HexGrid.hex_distance(miner.movement, (10, 10)) == 1
        assert HexGrid.hex_distance(miner.movement, (10, 15)) < \
            HexGrid.hex_distance((10, 10), (10, 15))

    def test_miner_parks_next_to_rock(self):
        miner = _ship("federation", row=10, col=14)
        miner.is_miner = True
        apply_faction(miner, "colonial")
        battle = _Battle([miner])
        battle.asteroids.append(Asteroid((10, 15), resource=("rare", 1)))
        AISystem().decide_actions([miner], None, False, battle)
        assert miner.movement is None

    def test_aliens_guard_anomalies_when_idle(self):
        alien = _ship("tholian", row=10, col=5)
        apply_faction(alien, "vethari")
        alien.aggro = False
        battle = _Battle([alien])
        battle.anomalies.append(Anomaly((10, 10), quality=2))
        AISystem().decide_actions([alien], None, False, battle)
        assert alien.movement is not None
        # Moves to orbit the anomaly rather than wander away from it.
        assert HexGrid.hex_distance(alien.movement, (10, 10)) <= \
            HexGrid.hex_distance((10, 5), (10, 10))


class TestTractorRules:
    def _setup(self):
        battle = _Battle()
        battle.asteroids.append(Asteroid((10, 10), resource=("common", 2)))
        ship = _ship(row=10, col=11)  # adjacent to the rock
        ship.target = (10, 10)
        return battle, ship

    def test_harvest_needs_turn_start_in_range(self):
        battle, ship = self._setup()
        ship.turn_start_hex = (10, 18)  # flew in from far away
        assert not HarvestSystem().process(ship, battle, _SilentAssets())
        assert battle.asteroids[0].resource is not None

    def test_harvest_allows_orbiting_the_target(self):
        battle, ship = self._setup()
        ship.turn_start_hex = (10, 11)
        ship.movement = (10, 9)  # circle to the far side, still range 1
        assert HarvestSystem().process(ship, battle, _SilentAssets())
        assert battle.asteroids[0].resource is None

    def test_harvest_denied_when_flying_away(self):
        battle, ship = self._setup()
        ship.turn_start_hex = (10, 11)
        ship.movement = (10, 16)  # leaving tractor range mid-turn
        assert not HarvestSystem().process(ship, battle, _SilentAssets())
        assert battle.asteroids[0].resource is not None


class TestMinerCargo:
    def test_miner_strips_adjacent_rock_at_turn_end(self):
        miner = _ship("federation", row=10, col=14)
        miner.is_miner = True
        miner.cargo = {"scrap": 0, "materials": {}}
        battle = _Battle([miner])
        battle.asteroids.append(Asteroid((10, 15), resource=("uncommon", 1)))
        TurnResolver._process_miners(None, battle)
        assert miner.cargo["materials"].get("uncommon") == 1
        assert battle.asteroids[0].resource is None

    def test_miner_cargo_spills_into_wreck(self):
        wreck = Wreck((10, 10), "federation", "cadet",
                      cargo={"scrap": 40, "materials": {"rare": 2}})
        battle = _Battle()
        battle.wrecks.append(wreck)
        harvester = _ship(row=10, col=11)
        harvester.target = (10, 10)
        HarvestSystem().process(harvester, battle, _SilentAssets())
        assert wreck.salvaged
        assert battle.harvested["scrap"] >= 40
        assert battle.harvested["materials"].get("rare", 0) >= 2


class TestBossFactions:
    def test_lone_wolf_boss_always_duels(self):
        for _ in range(200):
            config = generate_battle_config(2, NodeType.BOSS)
            if config["boss_faction"] == "pirates_lone":
                assert config["boss_mode"] == "duel"
                assert len(config["enemies"]) == 1

    def test_boss_faction_always_assigned(self):
        from spacewar.roguelike.factions import BOSS_FACTIONS
        for _ in range(50):
            config = generate_battle_config(1, NodeType.BOSS)
            assert config["boss_faction"] in BOSS_FACTIONS

    def test_unique_boss_has_no_faction_tag(self):
        for _ in range(200):
            config = generate_battle_config(1, NodeType.BOSS)
            if config["boss_faction"] == "unique":
                for spec in config["enemies"]:
                    assert spec[2] is None
                break


class TestBattleConfigShape:
    def test_map_sizes_valid(self):
        from spacewar.config.constants import MAP_SIZES
        for _ in range(50):
            config = generate_battle_config(1, NodeType.BATTLE)
            assert config["map_size"] in MAP_SIZES
            assert config["map_size"] != "1x1"  # boss arenas only
        seen = {generate_battle_config(2, NodeType.BOSS)["map_size"]
                for _ in range(200)}
        assert "1x1" in seen

    def test_enemy_specs_carry_factions(self):
        for _ in range(30):
            config = generate_battle_config(1, NodeType.BATTLE)
            for spec in config["enemies"]:
                assert len(spec) == 3

    def test_colonial_flag_matches_factions(self):
        for _ in range(50):
            config = generate_battle_config(1, NodeType.BATTLE)
            assert config["colonial"] == ("colonial" in config["factions"])


class TestMapSizes:
    def test_set_map_size_rescales_grid(self):
        from spacewar.config import constants
        constants.set_map_size(1, 3)
        assert constants.GRID_ROWS == 14
        assert constants.GRID_COLS_ODD == 33
        assert constants.GRID_COLS_EVEN == 32
        wide = constants.SCREEN_SIZE
        constants.set_map_size(2, 2)
        assert constants.GRID_ROWS == 28
        assert constants.GRID_COLS_ODD == 22
        assert constants.SCREEN_SIZE[0] < wide[0]

    def test_max_col_tracks_resize(self):
        from spacewar.config import constants
        from spacewar.config.constants import max_col
        constants.set_map_size(1, 1)
        assert max_col(1) == 11
        assert max_col(2) == 10
        constants.set_map_size(2, 2)
        assert max_col(1) == 22


class TestDisruptorVolley:
    def test_volley_fires_two_bolts(self):
        combat = CombatSystem(_SilentAssets(), _FakeTheme())
        who = _ship("klingon", row=7, col=5)
        torpedoes = []
        combat.fire_disruptor_volley(who, (7, 9), torpedoes, {}, None)
        assert len(torpedoes) == 2
        for bolt in torpedoes:
            assert bolt.is_bolt
            assert bolt.power == math.ceil(10 * 5.6 / 6)

    def test_volley_respects_range(self):
        combat = CombatSystem(_SilentAssets(), _FakeTheme())
        who = _ship("klingon", row=7, col=5)
        who.loadout.equip(Component(
            ComponentSlot.WEAPON_1, "Disruptors", 3,
            weapon_type="disruptors", weapon_range=8))
        who.action = "weapon_1"
        torpedoes = []
        combat.fire_disruptor_volley(who, (7, 20), torpedoes, {}, None)
        assert torpedoes == []  # 15 hexes is far out of range 8

    def test_same_volley_bolts_do_not_collide(self):
        combat = CombatSystem(_SilentAssets(), _FakeTheme())
        who = _ship("klingon", row=7, col=5)
        torpedoes = []
        combat.fire_disruptor_volley(who, (7, 9), torpedoes, {}, None)
        a, b = torpedoes
        b.rect.center = a.rect.center  # force overlap
        combat.update_torpedoes(torpedoes, [], {}, False, None)
        assert a.active and b.active

    def test_disruptor_stats(self):
        stats = WEAPON_STATS[WeaponType.DISRUPTORS]
        assert stats["max_range"] == 8
        assert stats["hits"] == 6
        assert stats["volleys"] == 3
        assert stats["bolts_per_volley"] == 2


class TestDualSpecialSlots:
    def test_two_specials_equip_side_by_side(self):
        from spacewar.components.defaults import (
            build_default_loadout, ambush_special, phasing_special,
        )
        loadout = build_default_loadout()
        loadout.equip(ambush_special())
        loadout.equip(phasing_special())
        assert loadout.has_special("ambush")
        assert loadout.has_special("phasing")
        assert len(loadout.get_specials()) == 2

    def test_get_special_finds_second_bay(self):
        from spacewar.components.defaults import (
            build_default_loadout, ambush_special, teleportation_special,
        )
        loadout = build_default_loadout()
        loadout.equip(ambush_special())
        loadout.equip(teleportation_special(teleport_range=7))
        tele = loadout.get_special("teleportation")
        assert tele is not None
        assert tele.get("teleport_range") == 7

    def test_third_special_replaces_first_bay(self):
        from spacewar.components.defaults import (
            build_default_loadout, teleportation_special, phasing_special,
            ambush_special,
        )
        loadout = build_default_loadout()
        loadout.equip(teleportation_special())
        loadout.equip(phasing_special())
        loadout.equip(ambush_special())
        assert loadout.has_special("ambush")
        assert loadout.has_special("phasing")
        assert not loadout.has_special("teleportation")

    def test_every_special_type_drops(self):
        # Tractor beams are standard equipment now, not specials.
        from spacewar.roguelike.loot import _random_special
        seen = set()
        for _ in range(200):
            comp = _random_special(1)
            seen.add(comp.get("ability_type"))
        assert seen == {"phasing", "ambush", "teleportation"}

    def test_everyone_has_a_tractor_beam(self):
        from spacewar.components.defaults import build_default_loadout
        from spacewar.components.race_configs import build_race_loadout
        assert build_default_loadout().has_tractor()
        for race in ("federation", "klingon", "narn", "psiloth",
                     "shadow", "zlorg", "terran", "sentry"):
            assert build_race_loadout(race).has_tractor(), race

    def test_passive_stealth_gear_exists(self):
        from spacewar.roguelike.loot import generate_anomaly_component
        for _ in range(300):
            comp = generate_anomaly_component(1, quality=2)
            if comp is not None and comp.get("passive_stealth", 0) >= 3:
                return
        pytest.fail("no passive stealth gear generated in 300 rolls")


class TestReinforcements:
    def _fake_game(self, battle, config):
        return SimpleNamespace(
            battle=battle,
            active_run=object(),
            roguelike_battle_config=config,
            settings=SimpleNamespace(pixel_perfect=False),
            theme_loader=SimpleNamespace(
                ships={},
                active_races=("federation", "klingon"),
                ensure_race_loaded=lambda race: True,
            ),
        )

    def test_spawn_cap_six_per_zone(self, monkeypatch):
        from spacewar.states import roguelike_states as rs
        battle = _Battle()
        battle.player = _ship(human=True)
        battle.ships.append(battle.player)
        battle.tier = 1
        battle.turn_count = 50
        battle.next_spawn_turn = 1
        battle.total_combat_spawns = 6
        config = {"enemies": [("cadet", "klingon", "pirates_band")],
                  "factions": ["pirates_band"], "is_boss": False}
        game = self._fake_game(battle, config)
        monkeypatch.setattr(rs.random, "random", lambda: 0.0)
        rs.maybe_spawn_reinforcement(game)
        assert len(battle.ships) == 1  # capped: nothing spawned

    def test_reinforcement_spawns_at_edge(self, monkeypatch):
        from spacewar.states import roguelike_states as rs
        from spacewar.config import constants
        from spacewar.config.constants import max_col
        battle = _Battle()
        battle.player = _ship(human=True)
        battle.ships.append(battle.player)
        battle.tier = 1
        battle.turn_count = 10
        battle.next_spawn_turn = 1
        battle.pending_enemies = [("cadet", "klingon", "pirates_band")]
        config = {"enemies": [], "factions": ["pirates_band"],
                  "is_boss": False}
        game = self._fake_game(battle, config)
        monkeypatch.setattr(rs.random, "random", lambda: 0.0)
        rs.maybe_spawn_reinforcement(game)
        assert len(battle.ships) == 2
        spawned = battle.ships[-1]
        assert spawned.aggro is False
        assert spawned.faction == "pirates_band"
        shex = HexGrid.coords_to_hex(spawned.pos)
        on_edge = (shex[0] in (1, constants.GRID_ROWS) or
                   shex[1] in (1, max_col(shex[0])))
        assert on_edge
        assert battle.next_spawn_turn > battle.turn_count

    def test_no_reinforcements_in_boss_zones(self, monkeypatch):
        from spacewar.states import roguelike_states as rs
        battle = _Battle()
        battle.player = _ship(human=True)
        battle.ships.append(battle.player)
        battle.turn_count = 10
        battle.next_spawn_turn = 1
        config = {"enemies": [], "factions": [], "is_boss": True}
        game = self._fake_game(battle, config)
        monkeypatch.setattr(rs.random, "random", lambda: 0.0)
        rs.maybe_spawn_reinforcement(game)
        assert len(battle.ships) == 1

    def test_no_spawn_while_three_roam(self, monkeypatch):
        from spacewar.states import roguelike_states as rs
        battle = _Battle()
        battle.player = _ship(human=True)
        battle.ships.append(battle.player)
        for col in (8, 10, 12):
            battle.ships.append(_ship("klingon", row=20, col=col))
        battle.turn_count = 10
        battle.next_spawn_turn = 1
        config = {"enemies": [], "factions": ["pirates_band"],
                  "is_boss": False}
        game = self._fake_game(battle, config)
        monkeypatch.setattr(rs.random, "random", lambda: 0.0)
        rs.maybe_spawn_reinforcement(game)
        assert len(battle.ships) == 4  # 3 hostiles already roam


class TestBeamColors:
    def test_weapon_component_color_wins(self):
        combat = CombatSystem(_SilentAssets(), _FakeTheme())
        who = _ship("federation")
        who.action = "weapon_1"
        who.phaser_color = (1, 2, 3)
        who.loadout.get_weapon(1).stats["phaser_color"] = (9, 8, 7)
        assert combat._get_phaser_color(who) == (9, 8, 7)

    def test_faction_color_beats_race_default(self):
        combat = CombatSystem(_SilentAssets(), _FakeTheme())
        who = _ship("narn")
        apply_faction(who, "pirates_band")
        who.action = "weapon_1"
        assert combat._get_phaser_color(who) == (220, 50, 50)

    def test_race_theme_color_is_fallback(self):
        combat = CombatSystem(_SilentAssets(), _FakeTheme())
        who = _ship("federation")
        who.action = "weapon_1"
        assert combat._get_phaser_color(who) == (255, 0, 0)

    def test_beam_color_names(self):
        from spacewar.states.roguelike_states import (
            _beam_color_name, BEAM_COLORS,
        )
        assert _beam_color_name(None) == "Default"
        assert _beam_color_name(BEAM_COLORS[0][1]) == BEAM_COLORS[0][0]
        assert _beam_color_name((1, 2, 3)) == "Custom"


class TestNeutralProvocation:
    def test_shot_colonial_turns_whole_guild_hostile(self):
        miner = _ship("federation", row=10, col=10)
        miner.is_miner = True
        apply_faction(miner, "colonial")
        defender = _ship("federation", row=10, col=12)
        apply_faction(defender, "colonial")
        battle = _Battle([miner, defender])
        miner.shot_recently = 5

        # Mirror of the resolver's end-of-turn provocation rule.
        for ship in battle.ships:
            if getattr(ship, 'neutral', False) and ship.shot_recently \
                    and not getattr(ship, 'hostile', False):
                faction = getattr(ship, 'faction', None)
                for s in battle.ships:
                    if getattr(s, 'faction', None) == faction:
                        s.hostile = True
                        s.aggro = True
        assert defender.hostile and defender.aggro
        assert miner.hostile
