from spacewar.rendering.hex_grid import HexGrid


class TeleportationSystem:
    def setup(self, ships, sprite_lookup):
        for ship in ships:
            has_teleport = ship.loadout.has_special("teleportation")
            should_teleport = (
                has_teleport and
                not ship.get_valid_destination(
                    ship.movement[0], ship.movement[1], bool(ship.action))
            )
            if should_teleport:
                ship.teleport_target = HexGrid.hex_to_coords(*ship.movement)
                ship.speed = 0
                if ship.active_cloak:
                    ship.cloak(False, sprite_lookup)
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
