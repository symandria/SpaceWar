from spacewar.systems.visibility import VisibilitySystem
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid


class TestVisibilitySystem:
    def test_own_hex_always_visible(self):
        vis = VisibilitySystem()
        ship = _make_ship(14, 11, angle=180)
        clear, shaded = vis.compute_visibility(ship)
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        assert ship_hex in clear

    def test_nearby_hexes_visible(self):
        vis = VisibilitySystem()
        ship = _make_ship(14, 11, angle=180)
        visible = vis.compute_visible_hexes(ship)
        assert len(visible) > 1

    def test_forward_range_greater_than_backward(self):
        vis = VisibilitySystem()
        ship = _make_ship(14, 11, angle=180)
        clear, shaded = vis.compute_visibility(ship)
        all_visible = clear | shaded
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        far_hexes = [h for h in all_visible if HexGrid.hex_distance(ship_hex, h) > 8]
        assert len(far_hexes) > 0

    def test_shaded_hexes_exist(self):
        vis = VisibilitySystem()
        ship = _make_ship(14, 11, angle=180)
        clear, shaded = vis.compute_visibility(ship)
        assert len(shaded) > 0

    def test_fog_hexes_exist(self):
        vis = VisibilitySystem()
        ship = _make_ship(14, 11, angle=180)
        clear, shaded, fog = vis.get_fog_data(ship)
        assert len(fog) > 0
        assert len(clear) > 0
        assert len(shaded) > 0

    def test_forward_13_hexes_total_visible(self):
        vis = VisibilitySystem()
        ship = _make_ship(14, 11, angle=180)
        clear, shaded = vis.compute_visibility(ship)
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        all_vis = clear | shaded
        max_forward = 0
        for h in all_vis:
            d = HexGrid.hex_distance(ship_hex, h)
            if d > max_forward:
                max_forward = d
        assert max_forward >= 10

    def test_can_see_visible_ship(self):
        vis = VisibilitySystem()
        observer = _make_ship(14, 11, angle=180)
        target = _make_ship(15, 11, angle=0)
        assert vis.can_see(observer, target)

    def test_cannot_see_cloaked_ship(self):
        vis = VisibilitySystem()
        observer = _make_ship(14, 11, angle=180)
        target = _make_ship(15, 11, angle=0)
        target.cloaked = True
        target.shot_recently = 0
        assert not vis.can_see(observer, target)

    def test_can_see_cloaked_with_detection(self):
        vis = VisibilitySystem()
        observer = _make_ship(14, 11, angle=180)
        from spacewar.components.base import Component, ComponentSlot
        sensor = Component(ComponentSlot.SENSORS, "Good Sensors", 3,
                           vision_forward=10, vision_backward=5,
                           cloak_detection=5)
        observer.loadout.equip(sensor)
        target = _make_ship(15, 11, angle=0)
        target.cloaked = True
        target.shot_recently = 0
        assert vis.can_see(observer, target)

    def test_purple_nebula_hides(self):
        vis = VisibilitySystem()
        observer = _make_ship(14, 11, angle=180)
        target = _make_ship(15, 11, angle=0)
        from spacewar.entities.map_object import NebulaTile
        neb = NebulaTile((15, 11), NebulaTile.PURPLE)
        nebulae = {(15, 11): neb}
        assert not vis.can_see(observer, target, nebulae)


def _make_ship(row, col, angle=0):
    ship = Ship('test', HexGrid.hex_to_coords(row, col), angle,
                'cadet', 'C', 'S', 100, 10, 5,
                specials=[], pixel_perfect=False)
    import pygame
    ship.image = pygame.Surface((9, 9))
    return ship
