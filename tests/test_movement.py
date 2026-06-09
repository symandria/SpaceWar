from spacewar.systems.movement import MovementSystem
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid


class TestWallCollision:
    def test_wall_damage_on_edge(self):
        mov = MovementSystem()
        ship = _make_ship(1, 1)
        ship.speed = 3
        ship.move_target = (-10, ship.pos[1])
        mov.update([ship], 1)
        assert ship.speed == 0

    def test_no_wall_damage_in_center(self):
        mov = MovementSystem()
        ship = _make_ship(7, 5)
        ship.speed = 3
        ship.move_target = HexGrid.hex_to_coords(8, 5)
        initial_hp = ship.shields + ship.hull
        mov.update([ship], 2)
        assert ship.shields + ship.hull == initial_hp

    def test_reset_clears_tracking(self):
        mov = MovementSystem()
        mov._wall_damage_applied.add(123)
        mov.reset()
        assert len(mov._wall_damage_applied) == 0


class TestHexTraversal:
    def test_same_hex(self):
        mov = MovementSystem()
        hexes = mov.get_hexes_traversed(None, (7, 5), (7, 5))
        assert hexes == [(7, 5)]

    def test_adjacent_hexes(self):
        mov = MovementSystem()
        hexes = mov.get_hexes_traversed(None, (7, 5), (8, 5))
        assert len(hexes) >= 2
        assert (7, 5) in hexes
        assert (8, 5) in hexes

    def test_longer_path(self):
        mov = MovementSystem()
        hexes = mov.get_hexes_traversed(None, (1, 1), (5, 5))
        assert len(hexes) >= 2
        assert hexes[0] == (1, 1)
        assert hexes[-1] == (5, 5)


class TestPhasing:
    def test_phasing_prevents_collision(self):
        from spacewar.systems.collision import CollisionSystem
        from spacewar.systems.scoring import ScoringSystem
        col = CollisionSystem()
        ship1 = _make_ship(7, 5)
        ship2 = _make_ship(7, 5)
        ship1.phasing_active = True
        stats = {
            ship1: ScoringSystem.init_ai_stats(),
            ship2: ScoringSystem.init_ai_stats(),
        }

        class DummyAsset:
            def play_sound(self, n): pass

        col.update([ship1, ship2], stats, False, None, DummyAsset())
        assert ship1.shields == 100
        assert ship2.shields == 100


class TestTeleportCooldown:
    def test_cooldown_decrements(self):
        from spacewar.systems.teleportation import TeleportationSystem
        ts = TeleportationSystem()
        ship = _make_ship(7, 5)
        ship.teleport_cooldown = 3
        ts.tick_cooldowns([ship])
        assert ship.teleport_cooldown == 2
        ts.tick_cooldowns([ship])
        assert ship.teleport_cooldown == 1
        ts.tick_cooldowns([ship])
        assert ship.teleport_cooldown == 0


def _make_ship(row, col):
    import pygame
    ship = Ship('test', HexGrid.hex_to_coords(row, col), 0,
                'cadet', 'C', 'S', 100, 10, 5,
                specials=[], pixel_perfect=False)
    ship.image = pygame.Surface((9, 9))
    return ship
