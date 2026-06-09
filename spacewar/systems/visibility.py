import math
from spacewar.rendering.hex_grid import HexGrid
from spacewar.config.constants import GRID_ROWS, max_col


class VisibilitySystem:
    def compute_visible_hexes(self, ship):
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        if ship_hex is None:
            return set()

        facing_rad = math.radians(90 - ship.angle)
        forward = ship.vision_forward
        backward = ship.vision_backward
        visible = set()

        for row in range(1, GRID_ROWS + 1):
            for col in range(1, max_col(row) + 1):
                dist = HexGrid.hex_distance(ship_hex, (row, col))
                if dist == 0:
                    visible.add((row, col))
                    continue
                target_pos = HexGrid.hex_to_coords(row, col)
                ship_pos = HexGrid.hex_to_coords(*ship_hex)
                dx = target_pos[0] - ship_pos[0]
                dy = target_pos[1] - ship_pos[1]
                angle_to_target = math.atan2(-dy, dx)
                angle_diff = abs(_angle_diff(facing_rad, angle_to_target))
                t = angle_diff / math.pi
                effective_range = forward + (backward - forward) * t
                if dist <= effective_range:
                    visible.add((row, col))

        return visible

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

        visible = self.compute_visible_hexes(observer)
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
            effective_range = (observer.vision_forward +
                               (observer.vision_backward - observer.vision_forward) * t)
            effective_range -= stealth_reduction
            return dist <= effective_range

        return target_hex in visible

    def get_fog_overlay(self, ship):
        visible = self.compute_visible_hexes(ship)
        all_hexes = set()
        for row in range(1, GRID_ROWS + 1):
            for col in range(1, max_col(row) + 1):
                all_hexes.add((row, col))
        return all_hexes - visible


def _angle_diff(a, b):
    diff = b - a
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff
