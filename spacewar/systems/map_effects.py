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
            elif neb.nebula_type == NebulaTile.PLASMA:
                # Burns hull directly; shields offer no protection.
                ship.hull -= max(1, int(ship.max_hull * 0.05))
            elif neb.nebula_type == NebulaTile.COMET:
                # Ice and grit scour the ship as it punches through.
                ship.apply_damage(
                    max(1, int((ship.max_hull + ship.max_shields) * 0.03)))

    def apply_end_of_turn_effects(self, ship, nebulae_by_hex,
                                  sprite_lookup=None):
        ship.sensor_static = False
        ship.comet_drag = False
        ship.slipstream_boost = False
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        if ship_hex is None:
            return
        neb = nebulae_by_hex.get(ship_hex)
        if neb is None:
            return
        ntype = neb.nebula_type
        if ntype == NebulaTile.GREEN:
            heal = int(ship.max_shields * 0.05)
            ship.shields = min(ship.shields + heal, ship.max_shields)
        elif ntype == NebulaTile.PURPLE:
            ship.shields = 0
        elif ntype == NebulaTile.PLASMA:
            ship.hull -= max(1, int(ship.max_hull * 0.05))
        elif ntype == NebulaTile.ION:
            ship.shields = max(0, ship.shields - int(ship.max_shields * 0.10))
            if ship.cloaked and sprite_lookup is not None:
                ship.cloak(False, sprite_lookup)
        elif ntype == NebulaTile.STATIC:
            ship.sensor_static = True
        elif ntype == NebulaTile.TACHYON:
            ship.teleport_cooldown = 0
            ship.phasing_cooldown = 0
        elif ntype == NebulaTile.COMET:
            ship.comet_drag = True  # slower next turn
        elif ntype == NebulaTile.EVERBRIGHT:
            # Blinding light: your own sensors suffer, and no cloak
            # survives the glare.
            ship.sensor_static = True
            if ship.cloaked and sprite_lookup is not None:
                ship.cloak(False, sprite_lookup)
        elif ntype == NebulaTile.SLIPSTREAM:
            ship.slipstream_boost = True  # faster next turn

    def apply_gravity(self, battle):
        """Gravity rifts drag ships within 2 hexes one hex closer;
        micro black holes reach 3 hexes and crush hulls at range 1."""
        nebulae_by_hex = getattr(battle, 'nebulae_by_hex', None)
        if not nebulae_by_hex:
            return
        rifts = [hx for hx, neb in nebulae_by_hex.items()
                 if neb.nebula_type == NebulaTile.GRAVITY]
        holes = [hx for hx, neb in nebulae_by_hex.items()
                 if neb.nebula_type == NebulaTile.BLACKHOLE]
        if rifts:
            self._pull_toward(battle, rifts, max_reach=2)
        if holes:
            self._pull_toward(battle, holes, max_reach=3)
            for ship in battle.ships:
                ship_hex = HexGrid.coords_to_hex(ship.pos)
                if ship_hex is None:
                    continue
                dist = min(HexGrid.hex_distance(ship_hex, h) for h in holes)
                if dist <= 1:
                    # Tidal forces tear straight at the hull.
                    ship.hull -= max(1, int(ship.max_hull * 0.05))

    def _pull_toward(self, battle, centers, max_reach):
        occupied = {HexGrid.coords_to_hex(s.pos) for s in battle.ships}
        occupied |= {a.hex_pos for a in battle.asteroids if not a.is_dead()}
        from spacewar.config import constants
        from spacewar.config.constants import max_col
        for ship in battle.ships:
            ship_hex = HexGrid.coords_to_hex(ship.pos)
            if ship_hex is None:
                continue
            pulls = [(HexGrid.hex_distance(ship_hex, c), c) for c in centers]
            dist, center = min(pulls)
            if not 1 <= dist <= max_reach:
                continue
            best = None
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    cand = (ship_hex[0] + dr, ship_hex[1] + dc)
                    if cand[0] < 1 or cand[0] > constants.GRID_ROWS or \
                            cand[1] < 1 or cand[1] > max_col(cand[0]):
                        continue
                    if cand in occupied:
                        continue
                    cand_dist = HexGrid.hex_distance(cand, center)
                    if cand_dist < dist and (
                            best is None or cand_dist < best[0]):
                        best = (cand_dist, cand)
            if best is not None:
                occupied.discard(ship_hex)
                ship.pos = HexGrid.hex_to_coords(*best[1])
                occupied.add(best[1])

    def is_in_purple_nebula(self, ship, nebulae_by_hex):
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        if ship_hex is None:
            return False
        neb = nebulae_by_hex.get(ship_hex)
        return neb is not None and neb.nebula_type == NebulaTile.PURPLE
