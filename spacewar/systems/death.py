from spacewar.rendering.hex_grid import HexGrid
from spacewar.entities.wreck import Wreck


class DeathSystem:
    EXPLOSION_DAMAGE = 30

    def detect_and_cascade(self, ships, match_stats, team_game):
        dying = []
        recheck = True
        while recheck:
            recheck = False
            for ship in ships:
                if ship in dying:
                    continue
                if ship.is_dead():
                    dying.append(ship)
                    for other in ships:
                        if other == ship:
                            continue
                        if HexGrid.hex_distance(
                                HexGrid.coords_to_hex(ship.pos),
                                HexGrid.coords_to_hex(other.pos)) <= 1:
                            if not other.is_dead():
                                other.apply_damage(self.EXPLOSION_DAMAGE)
                                if team_game and ship.type == other.type:
                                    match_stats[ship]["teamdamage"] -= self.EXPLOSION_DAMAGE
                                else:
                                    match_stats[ship]["damage"] += self.EXPLOSION_DAMAGE
                                recheck = True
        return dying

    def create_wrecks(self, dying, wreck_list):
        for ship in dying:
            hex_pos = HexGrid.coords_to_hex(ship.pos)
            if hex_pos:
                wreck = Wreck(hex_pos, ship.type, ship.rank,
                              cargo=getattr(ship, 'cargo', None))
                wreck_list.append(wreck)

    def animate_explosion(self, dying, frame):
        for ship in dying:
            ship.explode = frame

    def remove_dead(self, dying, ships, dead_list, player):
        removed_player = False
        for ship in dying:
            ships.remove(ship)
            dead_list.append(ship)
            if ship == player:
                removed_player = True
        return removed_player
