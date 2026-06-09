import math
from spacewar.rendering.hex_grid import HexGrid
from spacewar.config.constants import GRID_ROWS, max_col


class VisibilitySystem:
    def compute_visibility(self, ship):
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        if ship_hex is None:
            return set(), set()

        facing_rad = math.radians(90 - ship.angle)
        forward_clear = ship.vision_forward
        backward_clear = ship.vision_backward
        forward_shaded = forward_clear + 3
        backward_shaded = backward_clear + 3

        clear = set()
        shaded = set()

        for row in range(1, GRID_ROWS + 1):
            for col in range(1, max_col(row) + 1):
                dist = HexGrid.hex_distance(ship_hex, (row, col))
                if dist == 0:
                    clear.add((row, col))
                    continue

                target_pos = HexGrid.hex_to_coords(row, col)
                ship_pos = HexGrid.hex_to_coords(*ship_hex)
                dx = target_pos[0] - ship_pos[0]
                dy = target_pos[1] - ship_pos[1]
                angle_to_target = math.atan2(-dy, dx)
                angle_diff = abs(_angle_diff(facing_rad, angle_to_target))

                t = angle_diff / math.pi
                clear_range = forward_clear + (backward_clear - forward_clear) * _smooth(t)
                shaded_range = forward_shaded + (backward_shaded - forward_shaded) * _smooth(t)

                clear_range = math.ceil(clear_range)
                shaded_range = math.ceil(shaded_range)

                if dist <= clear_range:
                    clear.add((row, col))
                elif dist <= shaded_range:
                    shaded.add((row, col))

        return clear, shaded

    def compute_visible_hexes(self, ship):
        clear, shaded = self.compute_visibility(ship)
        return clear | shaded

    def can_see(self, observer, target, nebulae_by_hex=None):
        target_hex = HexGrid.coords_to_hex(target.pos)
        if target_hex is None:
            return False

        if nebulae_by_hex:
            from spacewar.entities.map_object import NebulaTile
            neb = nebulae_by_hex.get(target_hex)
            if neb and neb.nebula_type == NebulaTile.PURPLE:
                return False

        if target.cloaked and not target.shot_recently:
            obs_hex = HexGrid.coords_to_hex(observer.pos)
            dist = HexGrid.hex_distance(obs_hex, target_hex)
            return dist <= observer.cloak_detection

        clear, shaded = self.compute_visibility(observer)
        stealth_reduction = getattr(target, 'passive_stealth', 0)
        if stealth_reduction > 0:
            obs_hex = HexGrid.coords_to_hex(observer.pos)
            dist = HexGrid.hex_distance(obs_hex, target_hex)
            facing_rad = math.radians(90 - observer.angle)
            ship_pos = HexGrid.hex_to_coords(*obs_hex)
            target_pos = HexGrid.hex_to_coords(*target_hex)
            dx = target_pos[0] - ship_pos[0]
            dy = target_pos[1] - ship_pos[1]
            angle_to_target = math.atan2(-dy, dx)
            angle_diff = abs(_angle_diff(facing_rad, angle_to_target))
            t = angle_diff / math.pi
            forward = observer.vision_forward
            backward = observer.vision_backward
            effective = forward + (backward - forward) * _smooth(t)
            effective -= stealth_reduction
            return dist <= math.ceil(effective)

        return target_hex in (clear | shaded)

    def get_fog_data(self, ship):
        clear, shaded = self.compute_visibility(ship)
        all_hexes = set()
        for row in range(1, GRID_ROWS + 1):
            for col in range(1, max_col(row) + 1):
                all_hexes.add((row, col))
        fog = all_hexes - clear - shaded
        return clear, shaded, fog


def _smooth(t):
    return (1 - math.cos(t * math.pi)) / 2


def _angle_diff(a, b):
    diff = b - a
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff
