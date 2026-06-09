import pytest
from spacewar.entities.map_object import Asteroid, NebulaTile
from spacewar.entities.mine import Mine
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.map_effects import MapEffectsSystem


class TestAsteroid:
    def test_creation(self):
        ast = Asteroid((5, 5))
        assert ast.hull == 100
        assert ast.hex_pos == (5, 5)
        assert not ast.is_dead()

    def test_damage(self):
        ast = Asteroid((5, 5))
        ast.apply_damage(60)
        assert ast.hull == 40
        assert not ast.is_dead()

    def test_destruction(self):
        ast = Asteroid((5, 5))
        ast.apply_damage(100)
        assert ast.is_dead()


class TestNebula:
    def test_red_nebula(self):
        neb = NebulaTile((5, 5), NebulaTile.RED)
        assert neb.nebula_type == "red"

    def test_green_nebula(self):
        neb = NebulaTile((5, 5), NebulaTile.GREEN)
        assert neb.nebula_type == "green"

    def test_purple_nebula(self):
        neb = NebulaTile((5, 5), NebulaTile.PURPLE)
        assert neb.nebula_type == "purple"

    def test_colors_defined(self):
        for ntype in (NebulaTile.RED, NebulaTile.GREEN, NebulaTile.PURPLE):
            assert ntype in NebulaTile.COLORS


class TestMapEffects:
    def test_red_nebula_deals_damage(self):
        effects = MapEffectsSystem()
        ship = _make_ship()
        neb = NebulaTile((7, 5), NebulaTile.RED)
        nebulae = {(7, 5): neb}
        effects.apply_movement_effects(ship, [(7, 5)], nebulae)
        expected_dmg = int((ship.max_hull + ship.max_shields) * 0.10)
        total_hp = ship.shields + ship.hull
        assert total_hp < 150 - expected_dmg + 1

    def test_green_nebula_heals(self):
        effects = MapEffectsSystem()
        ship = _make_ship()
        ship.shields = 50
        neb = NebulaTile((7, 5), NebulaTile.GREEN)
        nebulae = {(7, 5): neb}
        effects.apply_movement_effects(ship, [(7, 5)], nebulae)
        assert ship.shields > 50

    def test_green_nebula_end_of_turn_heals(self):
        effects = MapEffectsSystem()
        ship = _make_ship()
        ship.shields = 50
        ship.pos = HexGrid.hex_to_coords(7, 5)
        neb = NebulaTile((7, 5), NebulaTile.GREEN)
        nebulae = {(7, 5): neb}
        effects.apply_end_of_turn_effects(ship, nebulae)
        assert ship.shields > 50

    def test_purple_nebula_disables_shields(self):
        effects = MapEffectsSystem()
        ship = _make_ship()
        ship.pos = HexGrid.hex_to_coords(7, 5)
        neb = NebulaTile((7, 5), NebulaTile.PURPLE)
        nebulae = {(7, 5): neb}
        effects.apply_end_of_turn_effects(ship, nebulae)
        assert ship.shields == 0

    def test_purple_nebula_undetectable(self):
        effects = MapEffectsSystem()
        ship = _make_ship()
        ship.pos = HexGrid.hex_to_coords(7, 5)
        neb = NebulaTile((7, 5), NebulaTile.PURPLE)
        nebulae = {(7, 5): neb}
        assert effects.is_in_purple_nebula(ship, nebulae)

    def test_no_nebula_no_effect(self):
        effects = MapEffectsSystem()
        ship = _make_ship()
        effects.apply_movement_effects(ship, [(7, 5)], {})
        assert ship.shields == 100
        assert ship.hull == 50


class TestMine:
    def test_creation(self):
        mine = Mine((50, 50), None, 16)
        assert mine.active
        assert mine.power == 16

    def test_detonate(self):
        mine = Mine((50, 50), None, 16)
        mine.detonate()
        assert not mine.active


def _make_ship():
    ship = Ship('test', HexGrid.hex_to_coords(7, 5), 0,
                'cadet', 'C', 'S', 100, 10, 5,
                specials=[], pixel_perfect=False)
    import pygame
    ship.image = pygame.Surface((9, 9))
    return ship
