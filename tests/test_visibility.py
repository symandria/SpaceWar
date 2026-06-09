from spacewar.systems.visibility import VisibilitySystem
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid


class TestVisibilitySystem:
    def test_own_hex_always_visible(self):
        vis = VisibilitySystem()
        ship = _make_ship(7, 5, angle=180)
        visible = vis.compute_visible_hexes(ship)
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        assert ship_hex in visible

    def test_nearby_hexes_visible(self):
        vis = VisibilitySystem()
        ship = _make_ship(7, 5, angle=180)
        visible = vis.compute_visible_hexes(ship)
        assert len(visible) > 1

    def test_forward_range_greater_than_backward(self):
        vis = VisibilitySystem()
        ship = _make_ship(7, 5, angle=180)
        visible = vis.compute_visible_hexes(ship)
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        forward_count = sum(1 for h in visible
                           if HexGrid.hex_distance(ship_hex, h) > 5)
        assert forward_count > 0

    def test_can_see_visible_ship(self):
        vis = VisibilitySystem()
        observer = _make_ship(7, 5, angle=180)
        target = _make_ship(8, 5, angle=0)
        assert vis.can_see(observer, target)

    def test_cannot_see_cloaked_ship(self):
        vis = VisibilitySystem()
        observer = _make_ship(7, 5, angle=180)
        target = _make_ship(8, 5, angle=0)
        target.cloaked = True
        target.shot_recently = 0
        assert not vis.can_see(observer, target)

    def test_can_see_cloaked_with_detection(self):
        vis = VisibilitySystem()
        observer = _make_ship(7, 5, angle=180)
        from spacewar.components.base import Component, ComponentSlot
        sensor = Component(ComponentSlot.SENSORS, "Good Sensors", 3,
                           vision_forward=10, vision_backward=5,
                           cloak_detection=5)
        observer.loadout.equip(sensor)
        target = _make_ship(8, 5, angle=0)
        target.cloaked = True
        target.shot_recently = 0
        assert vis.can_see(observer, target)

    def test_fog_overlay_exists(self):
        vis = VisibilitySystem()
        ship = _make_ship(7, 5, angle=180)
        fog = vis.get_fog_overlay(ship)
        assert len(fog) > 0

    def test_purple_nebula_hides(self):
        vis = VisibilitySystem()
        observer = _make_ship(7, 5, angle=180)
        target = _make_ship(8, 5, angle=0)
        from spacewar.entities.map_object import NebulaTile
        neb = NebulaTile((8, 5), NebulaTile.PURPLE)
        nebulae = {(8, 5): neb}
        assert not vis.can_see(observer, target, nebulae)


def _make_ship(row, col, angle=0):
    ship = Ship('test', HexGrid.hex_to_coords(row, col), angle,
                'cadet', 'C', 'S', 100, 10, 5,
                specials=[], pixel_perfect=False)
    import pygame
    ship.image = pygame.Surface((9, 9))
    return ship
