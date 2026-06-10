from spacewar.components.base import ComponentSlot
from spacewar.rendering.hex_grid import HexGrid


class TeleportationSystem:
    def setup(self, ships, sprite_lookup):
        for ship in ships:
            if ship.movement is None:
                ship.move_target = None
                ship.speed = 0
                continue
            special = ship.loadout.get_special("teleportation")
            has_teleport = special is not None
            if has_teleport and ship.teleport_cooldown > 0:
                has_teleport = False

            dest_valid = ship.get_valid_destination(
                ship.movement[0], ship.movement[1], bool(ship.action))

            if has_teleport and special.get("blink") and not dest_valid:
                # Blink drive: a short hop spliced into the move - jump
                # up to teleport_range hexes, then fly the remainder.
                blink_point = self._find_blink_point(ship, ships, special)
                if blink_point is not None:
                    ship.pos = HexGrid.hex_to_coords(*blink_point)
                    ship.blinked = True
                    ship.teleport_cooldown = special.get("recharge", 3)
                    if ship.active_cloak:
                        ship.cloak(False, sprite_lookup)
                ship.move_target = HexGrid.hex_to_coords(*ship.movement)
                ship.speed = HexGrid.hex_distance(
                    HexGrid.coords_to_hex(ship.pos), ship.movement)
                continue

            teleport_range = 999
            if has_teleport:
                teleport_range = special.get("teleport_range", 999)

            should_teleport = (has_teleport and
                               not special.get("blink") and not dest_valid)
            if should_teleport:
                ship_hex = HexGrid.coords_to_hex(ship.pos)
                dist = HexGrid.hex_distance(ship_hex, ship.movement)
                if dist > teleport_range:
                    should_teleport = False

            if should_teleport:
                ship.teleport_target = HexGrid.hex_to_coords(*ship.movement)
                ship.speed = 0
                if ship.active_cloak:
                    ship.cloak(False, sprite_lookup)
                recharge = special.get("recharge", 3) if special else 3
                ship.teleport_cooldown = recharge
            else:
                ship.move_target = HexGrid.hex_to_coords(*ship.movement)
                ship.speed = HexGrid.hex_distance(
                    HexGrid.coords_to_hex(ship.pos), ship.movement)

    @staticmethod
    def _find_blink_point(ship, ships, special):
        """Best hex within blink range to hop to: minimizes the flight
        remaining to the destination, which must then be flyable."""
        from spacewar.config import constants
        from spacewar.config.constants import max_col
        cur = HexGrid.coords_to_hex(ship.pos)
        target = ship.movement
        if cur is None or target is None:
            return None
        rng = special.get("teleport_range", 3)
        occupied = {HexGrid.coords_to_hex(s.pos) for s in ships if s != ship}
        best = None
        best_rem = None
        for dr in range(-rng, rng + 1):
            for dc in range(-rng, rng + 1):
                cand = (cur[0] + dr, cur[1] + dc)
                if cand == cur or cand in occupied:
                    continue
                if cand[0] < 1 or cand[0] > constants.GRID_ROWS or \
                        cand[1] < 1 or cand[1] > max_col(cand[0]):
                    continue
                if HexGrid.hex_distance(cur, cand) > rng:
                    continue
                rem = HexGrid.hex_distance(cand, target)
                flyable = (rem >= ship.speed - ship.acceleration and
                           rem <= ship.speed + ship.acceleration and
                           rem <= ship.engine)
                if not flyable:
                    continue
                if best_rem is None or rem < best_rem:
                    best_rem = rem
                    best = cand
        return best

    def play_sound_if_needed(self, ships, asset_loader):
        if any(ship.teleport_target or getattr(ship, 'blinked', False)
               for ship in ships):
            asset_loader.play_sound("teleport")

    def snap_positions(self, ships):
        for ship in ships:
            if ship.teleport_target:
                ship.pos = ship.teleport_target

    def clear_flags(self, ships):
        for ship in ships:
            if ship.teleport_target:
                ship.teleport_target = None
            if getattr(ship, 'blinked', False):
                ship.blinked = False

    def tick_cooldowns(self, ships):
        for ship in ships:
            if ship.teleport_cooldown > 0:
                ship.teleport_cooldown -= 1
