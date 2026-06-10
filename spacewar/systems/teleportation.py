from spacewar.components.base import ComponentSlot
from spacewar.rendering.hex_grid import HexGrid


class TeleportationSystem:
    def setup(self, ships, sprite_lookup):
        for ship in ships:
            if ship.movement is None:
                ship.move_target = None
                ship.speed = 0
                continue
            has_teleport = ship.loadout.has_special("teleportation")
            if has_teleport and ship.teleport_cooldown > 0:
                has_teleport = False

            teleport_range = 999
            if has_teleport:
                special = ship.loadout.get_special("teleportation")
                if special:
                    teleport_range = special.get("teleport_range", 999)

            should_teleport = (
                has_teleport and
                not ship.get_valid_destination(
                    ship.movement[0], ship.movement[1], bool(ship.action))
            )
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
                special = ship.loadout.get_special("teleportation")
                recharge = special.get("recharge", 3) if special else 3
                ship.teleport_cooldown = recharge
            else:
                ship.move_target = HexGrid.hex_to_coords(*ship.movement)
                ship.speed = HexGrid.hex_distance(
                    HexGrid.coords_to_hex(ship.pos), ship.movement)

    def play_sound_if_needed(self, ships, asset_loader):
        if any(ship.teleport_target for ship in ships):
            asset_loader.play_sound("teleport")

    def snap_positions(self, ships):
        for ship in ships:
            if ship.teleport_target:
                ship.pos = ship.teleport_target

    def clear_flags(self, ships):
        for ship in ships:
            if ship.teleport_target:
                ship.teleport_target = None

    def tick_cooldowns(self, ships):
        for ship in ships:
            if ship.teleport_cooldown > 0:
                ship.teleport_cooldown -= 1
