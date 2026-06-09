class CollisionSystem:
    PROXIMITY_THRESHOLD = 9

    def __init__(self):
        self._active = []

    def update(self, ships, match_stats, team_game, player, asset_loader):
        for i, ship in enumerate(ships):
            for other in ships[i + 1:]:
                if ship.phasing_active or other.phasing_active:
                    continue
                if (abs(ship.pos[0] - other.pos[0]) < self.PROXIMITY_THRESHOLD and
                        abs(ship.pos[1] - other.pos[1]) < self.PROXIMITY_THRESHOLD):
                    if (ship, other) not in self._active and \
                            (other, ship) not in self._active:
                        self._active.append((ship, other))
                        asset_loader.play_sound("hit")
                        ship_was_dead = ship.is_dead()
                        other_was_dead = other.is_dead()
                        ship.apply_damage(other.collision_damage)
                        other.apply_damage(ship.collision_damage)
                        if ship == player and other.is_dead() and not other_was_dead:
                            match_stats[player]["kills-" + other.type] += 1
                        elif other == player and ship.is_dead() and not ship_was_dead:
                            match_stats[player]["kills-" + ship.type] += 1
                        if team_game and ship.type == other.type:
                            match_stats[ship]["teamdamage"] -= other.collision_damage
                            match_stats[other]["teamdamage"] -= ship.collision_damage
                        else:
                            match_stats[ship]["damage"] += other.collision_damage
                            match_stats[other]["damage"] += ship.collision_damage
                elif (ship, other) in self._active:
                    self._active.remove((ship, other))
                elif (other, ship) in self._active:
                    self._active.remove((other, ship))

    def reset(self):
        self._active.clear()
