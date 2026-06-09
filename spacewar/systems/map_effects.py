from spacewar.entities.map_object import NebulaTile
from spacewar.rendering.hex_grid import HexGrid


class MapEffectsSystem:
    def apply_movement_effects(self, ship, hexes_traversed, nebulae_by_hex):
        for hx in hexes_traversed:
            neb = nebulae_by_hex.get(hx)
            if neb is None:
                continue
            if neb.nebula_type == NebulaTile.RED:
                dmg = int((ship.max_hull + ship.max_shields) * 0.10)
                ship.apply_damage(dmg)
            elif neb.nebula_type == NebulaTile.GREEN:
                heal = int(ship.max_shields * 0.05)
                ship.shields = min(ship.shields + heal, ship.max_shields)

    def apply_end_of_turn_effects(self, ship, nebulae_by_hex):
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        if ship_hex is None:
            return
        neb = nebulae_by_hex.get(ship_hex)
        if neb is None:
            return
        if neb.nebula_type == NebulaTile.GREEN:
            heal = int(ship.max_shields * 0.05)
            ship.shields = min(ship.shields + heal, ship.max_shields)
        elif neb.nebula_type == NebulaTile.PURPLE:
            ship.shields = 0

    def is_in_purple_nebula(self, ship, nebulae_by_hex):
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        if ship_hex is None:
            return False
        neb = nebulae_by_hex.get(ship_hex)
        return neb is not None and neb.nebula_type == NebulaTile.PURPLE
