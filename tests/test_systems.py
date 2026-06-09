import pytest
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.regeneration import RegenerationSystem
from spacewar.systems.cloaking import CloakingSystem
from spacewar.systems.collision import CollisionSystem
from spacewar.systems.death import DeathSystem
from spacewar.systems.scoring import ScoringSystem


class TestRegenerationSystem:
    def test_passive_regen_applied(self, teleport_ship):
        regen = RegenerationSystem()
        teleport_ship.shields = 50
        regen.setup_regen_flag(teleport_ship)
        assert teleport_ship.regen == 10
        regen.apply_end_of_turn([teleport_ship])
        assert teleport_ship.shields == 60

    def test_regen_capped_at_max(self, teleport_ship):
        regen = RegenerationSystem()
        teleport_ship.shields = 95
        regen.setup_regen_flag(teleport_ship)
        regen.apply_end_of_turn([teleport_ship])
        assert teleport_ship.shields == 100

    def test_dead_ship_no_regen(self, teleport_ship):
        regen = RegenerationSystem()
        teleport_ship.hull = -1
        regen.setup_regen_flag(teleport_ship)
        regen.apply_end_of_turn([teleport_ship])

    def test_default_ship_has_passive_regen(self, default_ship):
        regen = RegenerationSystem()
        default_ship.shields = 90
        regen.setup_regen_flag(default_ship)
        assert default_ship.regen == 5
        regen.apply_end_of_turn([default_ship])
        assert default_ship.shields == 95


class TestCloakingSystem:
    def test_cloak_when_no_action(self, cloaking_ship):
        cloak = CloakingSystem()
        cloaking_ship.action = None
        cloak.apply([cloaking_ship], _make_sprites(cloaking_ship))
        assert cloaking_ship.cloaked is True

    def test_uncloak_when_attacking(self, cloaking_ship):
        cloak = CloakingSystem()
        cloaking_ship.action = "phaser"
        cloak.apply([cloaking_ship], _make_sprites(cloaking_ship))
        assert cloaking_ship.cloaked is False

    def test_non_cloak_ship_unaffected(self, default_ship):
        cloak = CloakingSystem()
        default_ship.action = None
        cloak.apply([default_ship], _make_sprites(default_ship))
        assert default_ship.cloaked is False


class TestCollisionSystem:
    def test_collision_deals_damage(self):
        col = CollisionSystem()
        ship1 = _make_ship_at(7, 5)
        ship2 = _make_ship_at(7, 5)
        stats = {
            ship1: ScoringSystem.init_ai_stats(),
            ship2: ScoringSystem.init_ai_stats(),
        }
        col.update([ship1, ship2], stats, False, None, _DummyAssetLoader())
        assert ship1.shields < 100 or ship1.hull < 50
        assert ship2.shields < 100 or ship2.hull < 50

    def test_collision_damage_uses_ship_stat(self):
        col = CollisionSystem()
        ship1 = _make_ship_at(7, 5)
        ship2 = _make_ship_at(7, 5)
        stats = {
            ship1: ScoringSystem.init_ai_stats(),
            ship2: ScoringSystem.init_ai_stats(),
        }
        col.update([ship1, ship2], stats, False, None, _DummyAssetLoader())
        assert ship1.shields == 75  # 25 damage from ship2.collision_damage


class TestDeathSystem:
    def test_detect_dead_ship(self):
        death = DeathSystem()
        ship = _make_ship_at(7, 5)
        ship.hull = -1
        stats = {ship: ScoringSystem.init_ai_stats()}
        dying = death.detect_and_cascade([ship], stats, False)
        assert ship in dying

    def test_alive_ship_not_dying(self):
        death = DeathSystem()
        ship = _make_ship_at(7, 5)
        stats = {ship: ScoringSystem.init_ai_stats()}
        dying = death.detect_and_cascade([ship], stats, False)
        assert len(dying) == 0

    def test_explosion_cascade(self):
        death = DeathSystem()
        ship1 = _make_ship_at(7, 5)
        ship2 = _make_ship_at(7, 5)  # same position = adjacent
        ship1.hull = -1
        stats = {
            ship1: ScoringSystem.init_ai_stats(),
            ship2: ScoringSystem.init_ai_stats(),
        }
        dying = death.detect_and_cascade([ship1, ship2], stats, False)
        assert ship1 in dying
        # ship2 should take 30 explosion damage but may survive
        assert ship2.shields < 100


# --- helpers ---

def _make_ship_at(row, col):
    ship = Ship('test', HexGrid.hex_to_coords(row, col), 0,
                'cadet', 'C', 'S', 100, 10, 5,
                specials=[], pixel_perfect=False)
    import pygame
    ship.image = pygame.Surface((9, 9))
    return ship


def _make_sprites(ship):
    import pygame
    img = pygame.Surface((9, 9))
    sprites = {ship.type: img}
    if ship.active_cloak:
        sprites["cloaked-" + ship.type] = img
    return sprites


class _DummyAssetLoader:
    def play_sound(self, name):
        pass
