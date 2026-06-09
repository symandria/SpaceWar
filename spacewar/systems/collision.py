class CollisionSystem:
    PROXIMITY_THRESHOLD = 9
    BASE_DAMAGE = 10

    def __init__(self):
        self._active = []

    def update(self, ships, match_stats, team_game, player, asset_loader):
        for i, ship in enumerate(ships):
            for other in ships[i + 1:]:
                if (abs(ship.pos[0] - other.pos[0]) < self.PROXIMITY_THRESHOLD and
                        abs(ship.pos[1] - other.pos[1]) < self.PROXIMITY_THRESHOLD):
                    if (ship, other) not in self._active and \
                            (other, ship) not in self._active:
                        self._active.append((ship, other))
                        asset_loader.play_sound("hit")
                        before = ship.shields, other.shields
                        ship_ramming = 3 if "ramming" in ship.specials else 1
                        other_ramming = 3 if "ramming" in other.specials else 1
                        ship.apply_damage(self.BASE_DAMAGE * other_ramming)
                        other.apply_damage(self.BASE_DAMAGE * ship_ramming)
                        if ship == player and other.shields < 0 and before[1] >= 0:
                            match_stats[player]["kills-" + other.type] += 1
                        elif other == player and ship.shields < 0 and before[0] >= 0:
                            match_stats[player]["kills-" + ship.type] += 1
                        damage = before[0] - ship.shields, before[1] - other.shields
                        if team_game and ship.type == other.type:
                            match_stats[ship]["teamdamage"] -= damage[0]
                            match_stats[other]["teamdamage"] -= damage[1]
                        else:
                            match_stats[ship]["damage"] += damage[0]
                            match_stats[other]["damage"] += damage[1]
                elif (ship, other) in self._active:
                    self._active.remove((ship, other))
                elif (other, ship) in self._active:
                    self._active.remove((other, ship))

    def reset(self):
        self._active.clear()
