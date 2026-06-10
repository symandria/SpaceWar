"""Tests for the Space Race-inspired stellar phenomena: comet tails,
slipstreams, everbright nebulae, micro black holes, solar flares,
debris/graveyard wreck fields, and defense turret zones."""
import pygame

from spacewar.entities.map_object import NebulaTile, NEBULA_DESCRIPTIONS
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.roguelike.encounters import ENVIRONMENTS
from spacewar.systems.map_effects import MapEffectsSystem
from spacewar.systems.turn_resolution import TurnResolver


class _Battle:
    def __init__(self, ships=()):
        self.ships = list(ships)
        self.asteroids = []
        self.nebulae = []
        self.nebulae_by_hex = {}
        self.turn_count = 0
        self.zone_effect = None


def _ship(row=7, col=5):
    ship = Ship("federation", HexGrid.hex_to_coords(row, col), 0,
                "cadet", "Cap", "Ship", 100, 10, 5, pixel_perfect=False)
    ship.image = pygame.Surface((9, 9))
    return ship


class TestNewTileTypes:
    def test_all_new_types_have_colors_and_descriptions(self):
        for ntype in (NebulaTile.COMET, NebulaTile.EVERBRIGHT,
                      NebulaTile.BLACKHOLE, NebulaTile.SLIPSTREAM):
            assert ntype in NebulaTile.COLORS
            assert ntype in NEBULA_DESCRIPTIONS

    def test_comet_tail_scours_and_drags(self):
        fx = MapEffectsSystem()
        ship = _ship()
        nebulae = {(7, 6): NebulaTile((7, 6), NebulaTile.COMET)}
        fx.apply_movement_effects(ship, [(7, 6)], nebulae)
        assert ship.shields < 100  # scoured on the way through
        ship.pos = HexGrid.hex_to_coords(7, 6)
        fx.apply_end_of_turn_effects(ship, nebulae)
        assert ship.comet_drag
        assert ship.engine == 3  # 5 - 2 drag penalty

    def test_comet_drag_clears_next_turn_outside(self):
        fx = MapEffectsSystem()
        ship = _ship()
        ship.comet_drag = True
        fx.apply_end_of_turn_effects(ship, {})
        assert not ship.comet_drag
        assert ship.engine == 5

    def test_slipstream_boosts_engines(self):
        fx = MapEffectsSystem()
        ship = _ship()
        nebulae = {(7, 5): NebulaTile((7, 5), NebulaTile.SLIPSTREAM)}
        fx.apply_end_of_turn_effects(ship, nebulae)
        assert ship.slipstream_boost
        assert ship.engine == 8  # 5 + 3 boost

    def test_everbright_blinds_and_decloaks(self):
        fx = MapEffectsSystem()
        ship = _ship()
        ship.cloaked = True
        nebulae = {(7, 5): NebulaTile((7, 5), NebulaTile.EVERBRIGHT)}
        fx.apply_end_of_turn_effects(ship, nebulae, sprite_lookup={})
        assert ship.sensor_static  # blinded sensors
        assert not ship.cloaked    # glare burns away the cloak

    def test_black_hole_pulls_from_three_hexes(self):
        fx = MapEffectsSystem()
        ship = _ship(row=7, col=8)  # 3 hexes from the hole
        battle = _Battle([ship])
        hole = NebulaTile((7, 5), NebulaTile.BLACKHOLE)
        battle.nebulae_by_hex[(7, 5)] = hole
        fx.apply_gravity(battle)
        new_hex = HexGrid.coords_to_hex(ship.pos)
        assert HexGrid.hex_distance(new_hex, (7, 5)) < 3

    def test_black_hole_crushes_at_point_blank(self):
        fx = MapEffectsSystem()
        ship = _ship(row=7, col=6)  # adjacent to the hole
        battle = _Battle([ship])
        hole = NebulaTile((7, 5), NebulaTile.BLACKHOLE)
        battle.nebulae_by_hex[(7, 5)] = hole
        hull_before = ship.hull
        fx.apply_gravity(battle)
        assert ship.hull < hull_before

    def test_gravity_rift_still_only_reaches_two(self):
        fx = MapEffectsSystem()
        ship = _ship(row=7, col=8)  # 3 hexes from the rift
        battle = _Battle([ship])
        rift = NebulaTile((7, 5), NebulaTile.GRAVITY)
        battle.nebulae_by_hex[(7, 5)] = rift
        fx.apply_gravity(battle)
        assert HexGrid.coords_to_hex(ship.pos) == (7, 8)


class TestSolarFlare:
    def test_flare_erupts_on_odd_turns(self):
        ship = _ship()
        battle = _Battle([ship])
        battle.zone_effect = "solar_flare"
        battle.turn_count = 1
        TurnResolver._apply_zone_effects(None, battle)
        assert ship.shields == 100 - 15

    def test_no_flare_on_even_turns(self):
        ship = _ship()
        battle = _Battle([ship])
        battle.zone_effect = "solar_flare"
        battle.turn_count = 2
        TurnResolver._apply_zone_effects(None, battle)
        assert ship.shields == 100

    def test_flare_burns_unshielded_hull(self):
        ship = _ship()
        ship.shields = 0
        battle = _Battle([ship])
        battle.zone_effect = "solar_flare"
        battle.turn_count = 1
        hull_before = ship.hull
        TurnResolver._apply_zone_effects(None, battle)
        assert ship.hull < hull_before


class TestNewEnvironments:
    NEW = ("solar_flare", "comet_tail", "debris_ring",
           "warship_graveyard", "everbright", "black_hole",
           "turret_zone", "slipstream")

    def test_all_new_environments_registered(self):
        for key in self.NEW:
            assert key in ENVIRONMENTS

    def test_all_new_environments_harvestable(self):
        # Everything except open space has something to harvest.
        for key in self.NEW:
            assert ENVIRONMENTS[key]["harvestable"], key

    def test_environment_schema(self):
        required = ("label", "weight", "asteroids", "harvestable",
                    "extra_enemies", "nebula", "clusters",
                    "anomaly_chance", "anomaly_quality")
        for key, env in ENVIRONMENTS.items():
            for field in required:
                assert field in env, f"{key} missing {field}"

    def test_wreck_fields_define_wrecks(self):
        assert ENVIRONMENTS["debris_ring"]["wrecks"][1] >= 2
        assert ENVIRONMENTS["warship_graveyard"]["wrecks"][1] >= 4

    def test_black_hole_is_a_single_tile(self):
        env = ENVIRONMENTS["black_hole"]
        assert env["cluster_radius"] == 0
        assert env["clusters"] == 1

    def test_turret_zone_defines_turrets(self):
        assert ENVIRONMENTS["turret_zone"]["turrets"][1] >= 1

    def test_nebula_types_resolve(self):
        for key, env in ENVIRONMENTS.items():
            kind = env.get("nebula")
            if kind and kind != "mixed":
                assert kind in NebulaTile.COLORS, f"{key}: {kind}"
