from spacewar.config.constants import SCREEN_SIZE, GRID_MARGIN_X, PLAY_AREA_TOP
from spacewar.rendering.hex_grid import HexGrid


class MovementSystem:
    def __init__(self):
        self._wall_damage_applied = set()

    def update(self, ships, remaining_frames):
        for ship in ships:
            if ship.move_target:
                ship.interpolate_toward(ship.move_target, remaining_frames)
                if remaining_frames <= 2:
                    self._check_wall_collision(ship)

    def _check_wall_collision(self, ship):
        if id(ship) in self._wall_damage_applied:
            return
        x, y = ship.pos
        margin = 2
        hit_wall = False
        if x < GRID_MARGIN_X - margin or x > SCREEN_SIZE[0] - 10:
            hit_wall = True
        if y < PLAY_AREA_TOP - margin or y > SCREEN_SIZE[1] - 10:
            hit_wall = True

        if hit_wall:
            damage = int(ship.speed * 0.05 * (ship.max_hull + ship.max_shields))
            if damage > 0:
                ship.apply_damage(damage)
            ship.speed = 0
            x = max(GRID_MARGIN_X, min(x, SCREEN_SIZE[0] - 12))
            y = max(PLAY_AREA_TOP, min(y, SCREEN_SIZE[1] - 12))
            ship.pos = (x, y)
            self._wall_damage_applied.add(id(ship))

    def reset(self):
        self._wall_damage_applied.clear()

    def get_hexes_traversed(self, ship, start_hex, end_hex):
        if start_hex is None or end_hex is None:
            return []
        if start_hex == end_hex:
            return [start_hex]
        hexes = [start_hex]
        start_pos = HexGrid.hex_to_coords(*start_hex)
        end_pos = HexGrid.hex_to_coords(*end_hex)
        dist = HexGrid.hex_distance(start_hex, end_hex)
        for i in range(1, dist + 1):
            t = i / dist
            mid_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            mid_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            mid_hex = HexGrid.coords_to_hex((mid_x + 4, mid_y + 4))
            if mid_hex and mid_hex != hexes[-1]:
                hexes.append(mid_hex)
        if end_hex not in hexes:
            hexes.append(end_hex)
        return hexes
