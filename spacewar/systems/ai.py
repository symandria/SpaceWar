import random

from spacewar.config import constants
from spacewar.config.constants import max_col
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.weapons import WeaponType, WEAPON_STATS

# Nebula types a careful captain stays out of.
DAMAGING_NEBULAE = ("red", "plasma", "ion", "purple", "comet", "blackhole")
DEFENDER_LEASH = 10


def _is_neutral(ship):
    """Shops and unprovoked colonials are nobody's target."""
    if getattr(ship, 'is_shop', False) or getattr(ship, 'neutral', False):
        return not getattr(ship, 'hostile', False)
    return False


class AISystem:
    def decide_actions(self, ships, player, team_game, battle=None):
        for enemy in ships:
            if enemy == player:
                continue
            if getattr(enemy, 'is_shop', False) or \
                    getattr(enemy, 'is_turret', False):
                self._decide_shop(enemy, ships, player, team_game)
                continue
            if getattr(enemy, 'is_miner', False):
                self._decide_miner(enemy, ships, player, battle)
                continue
            ehex = HexGrid.coords_to_hex(enemy.pos)

            enemies_of = [
                s for s in ships if s != enemy and not s.is_dead()
                and not self._is_friendly(enemy, s, team_game)
                and not _is_neutral(s)
            ]
            nearest = self._find_nearest_enemy(enemy, enemies_of)

            # Unprovoked colonials never start a fight; escorts shadow
            # their mining ship instead.
            if _is_neutral(enemy):
                enemy.action = None
                enemy.target = None
                enemy.movement = self._choose_movement(
                    enemy, ehex, None, enemies_of, battle, player)
                continue

            # Un-aggroed ships patrol until something enters sensor
            # range or they take fire.
            if not enemy.aggro:
                if nearest is not None or enemy.shot_recently:
                    enemy.aggro = True
                else:
                    enemy.action = None
                    enemy.target = None
                    enemy.movement = self._choose_movement(
                        enemy, ehex, None, enemies_of, battle, player)
                    continue

            if enemy.type == "sentry":
                enemy.action = "weapon_2"
            else:
                enemy.action = self._choose_action(enemy, nearest)

            if enemy.action in ("weapon_1", "weapon_2"):
                target_hex = self._choose_target(enemy, nearest, enemies_of)
                enemy.target = target_hex
            elif enemy.action == "regen_shields":
                enemy.target = None

            enemy.movement = self._choose_movement(
                enemy, ehex, nearest, enemies_of, battle, player)

            has_teleport = (enemy.loadout.has_special("teleportation") and
                            enemy.teleport_cooldown == 0)
            if has_teleport and enemy.hull < enemy.max_hull * 0.3 and \
                    not getattr(enemy, 'reckless', False):
                safe_row = random.randint(3, constants.GRID_ROWS - 2)
                enemy.movement = safe_row, random.randint(2, max_col(safe_row) - 1)

    def _is_friendly(self, ship, other, team_game):
        if team_game and other.type == ship.type:
            return True
        from spacewar.roguelike.factions import are_allied
        return are_allied(ship, other)

    def _decide_shop(self, shop, ships, player, team_game):
        shop.movement = None
        if not getattr(shop, 'hostile', False):
            shop.action = None
            shop.target = None
            return
        enemies_of = [s for s in ships if s != shop and not s.is_dead()
                      and not getattr(s, 'is_shop', False)]
        nearest = self._find_nearest_enemy(shop, enemies_of)
        if nearest is not None:
            shop.action = "weapon_2"
            shop.target = HexGrid.coords_to_hex(nearest.pos)
        else:
            shop.action = None
            shop.target = None

    def _decide_miner(self, miner, ships, player, battle):
        """Mining ships crawl from rock to rock and never shoot. The
        actual ore transfer happens at end of turn in the resolver."""
        miner.action = None
        miner.target = None
        miner.movement = None
        mhex = HexGrid.coords_to_hex(miner.pos)
        if battle is None or mhex is None:
            return
        targets = [a for a in battle.asteroids
                   if a.resource and not a.is_dead()]
        if not targets:
            return
        nearest = min(targets,
                      key=lambda a: HexGrid.hex_distance(mhex, a.hex_pos))
        if HexGrid.hex_distance(mhex, nearest.hex_pos) <= 1:
            return  # parked alongside; keep mining

        avoid = self._hazard_hexes(battle, include_mines=True)
        if player is not None:
            phex = HexGrid.coords_to_hex(player.pos)
            if phex:
                avoid = avoid | {phex}
        occupied = {HexGrid.coords_to_hex(s.pos) for s in ships if s != miner}
        best = None
        best_d = HexGrid.hex_distance(mhex, nearest.hex_pos)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                cand = (mhex[0] + dr, mhex[1] + dc)
                if cand == mhex or cand in avoid or cand in occupied:
                    continue
                if cand[0] < 1 or cand[0] > constants.GRID_ROWS or \
                        cand[1] < 1 or cand[1] > max_col(cand[0]):
                    continue
                if HexGrid.hex_distance(mhex, cand) != 1:
                    continue
                d = HexGrid.hex_distance(cand, nearest.hex_pos)
                if d < best_d:
                    best_d = d
                    best = cand
        miner.movement = best

    def _hazard_hexes(self, battle, include_mines=False):
        """Hexes a hazard-averse captain refuses to enter."""
        hazard = set()
        if battle is None:
            return hazard
        for hx, neb in getattr(battle, 'nebulae_by_hex', {}).items():
            if neb.nebula_type in DAMAGING_NEBULAE:
                hazard.add(hx)
        if include_mines:
            for mine in getattr(battle, 'mines', ()):
                mhex = mine.hex_pos
                if mhex is None or not mine.active:
                    continue
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        hazard.add((mhex[0] + dr, mhex[1] + dc))
        return hazard

    def _find_nearest_enemy(self, ship, enemies):
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        # AI can only target what its own sensors can reach.
        sensor_range = ship.vision_forward
        nearest = None
        nearest_dist = 999
        for e in enemies:
            if e.cloaked:
                continue
            ehex = HexGrid.coords_to_hex(e.pos)
            d = HexGrid.hex_distance(ship_hex, ehex)
            if d > sensor_range:
                continue
            if d < nearest_dist:
                nearest_dist = d
                nearest = e
        return nearest

    def _choose_action(self, ship, nearest):
        if ship.shields < ship.max_shields * 0.2 and ship.hull < ship.max_hull * 0.4:
            return "regen_shields"

        if ship.active_dr > 0 and ship.hull < ship.max_hull * 0.3:
            return "power_shields"

        if nearest is None:
            # Nothing in sensor range: cloak if able, otherwise idle.
            if ship.active_cloak and not ship.cloaked:
                return "cloak"
            return None

        ship_hex = HexGrid.coords_to_hex(ship.pos)
        target_hex = HexGrid.coords_to_hex(nearest.pos)
        dist = HexGrid.hex_distance(ship_hex, target_hex)

        w1 = ship.loadout.get_weapon(1)
        w2 = ship.loadout.get_weapon(2)
        w1_range = w1.get("weapon_range", 15) if w1 else 0
        w2_range = w2.get("weapon_range", 15) if w2 else 0

        if ship.active_cloak and not ship.cloaked and \
                dist > max(w1_range, w2_range) + 2:
            return "cloak"  # close in under cloak

        if dist <= w1_range and dist <= w2_range:
            w1_type = w1.get("weapon_type", "lazers") if w1 else "lazers"
            w2_type = w2.get("weapon_type", "torpedoes") if w2 else "torpedoes"
            try:
                w1_dmg = WEAPON_STATS[WeaponType(w1_type)]["damage_per_hit"](ship.weapon_power)
                w2_dmg = WEAPON_STATS[WeaponType(w2_type)]["damage_per_hit"](ship.weapon_power)
                return "weapon_1" if w1_dmg >= w2_dmg else "weapon_2"
            except (ValueError, KeyError):
                return "weapon_1"
        elif dist <= w1_range:
            return "weapon_1"
        elif dist <= w2_range:
            return "weapon_2"
        else:
            return random.choice(["weapon_1", "weapon_2"])

    def _choose_target(self, ship, nearest, enemies):
        if nearest is None:
            # Blind fire stays within own sensor range.
            ship_hex = HexGrid.coords_to_hex(ship.pos)
            reach = max(1, ship.vision_forward)
            for _ in range(20):
                row = random.randint(1, constants.GRID_ROWS)
                col = random.randint(1, max_col(row))
                if ship_hex is None or \
                        HexGrid.hex_distance(ship_hex, (row, col)) <= reach:
                    return row, col
            return ship_hex

        thex = HexGrid.coords_to_hex(nearest.pos)
        lead_offset = min(nearest.speed, 2)
        if lead_offset > 0:
            dr = random.randint(-lead_offset, lead_offset)
            dc = random.randint(-lead_offset, lead_offset)
            row = max(1, min(constants.GRID_ROWS, thex[0] + dr))
            col = max(1, min(max_col(row), thex[1] + dc))
            return row, col
        return thex

    def _choose_movement(self, ship, current_hex, nearest, enemies,
                         battle=None, player=None):
        valid = []
        for row in range(1, constants.GRID_ROWS + 1):
            for col in range(1, max_col(row) + 1):
                if ship.get_valid_destination(row, col, bool(ship.action)) and \
                        (ship.type == "sentry" or (row, col) != current_hex):
                    valid.append((row, col))

        if not valid:
            return current_hex

        valid = self._apply_faction_filters(
            ship, valid, battle, player)
        if not valid:
            return current_hex

        if nearest is None:
            anchor = self._idle_anchor(ship, battle)
            if anchor is not None:
                # Guard duty: orbit the thing we protect.
                return min(valid, key=lambda h: abs(
                    HexGrid.hex_distance(h, anchor) - 1))
            return random.choice(valid)

        target_hex = HexGrid.coords_to_hex(nearest.pos)
        w1 = ship.loadout.get_weapon(1)
        ideal_range = w1.get("weapon_range", 15) // 2 if w1 else 5

        if ship.hull < ship.max_hull * 0.25 and \
                not getattr(ship, 'reckless', False):
            valid.sort(key=lambda h: -HexGrid.hex_distance(h, target_hex))
            return valid[0]

        best = min(valid,
                   key=lambda h: abs(HexGrid.hex_distance(h, target_hex) - ideal_range))
        return best

    def _apply_faction_filters(self, ship, valid, battle, player):
        """Trim destinations by faction temperament. Filters relax
        rather than strand a ship: if nothing safe remains, the
        original list survives."""
        if battle is None:
            return valid

        # Hazard-averse captains: aliens stay out of damaging space
        # while at peace; colonials always do, and also shun mines.
        if getattr(ship, 'avoid_hazards', False):
            always = getattr(ship, 'neutral', False)
            if always or not ship.aggro:
                hazard = self._hazard_hexes(battle, include_mines=always)
                safe = [h for h in valid if h not in hazard]
                if safe:
                    valid = safe

        # Colonials plot courses around the player's position.
        if getattr(ship, 'neutral', False) and player is not None:
            phex = HexGrid.coords_to_hex(player.pos)
            if phex:
                clear = [h for h in valid if h != phex]
                if clear:
                    valid = clear

        # Escort leash: defenders stay within reach of their miner
        # unless another escort already covers it.
        guard = getattr(ship, 'guard_target', None)
        if guard is not None and guard in battle.ships and not guard.is_dead():
            ghex = HexGrid.coords_to_hex(guard.pos)
            if ghex:
                covered = any(
                    s is not ship and not s.is_dead() and
                    getattr(s, 'guard_target', None) is guard and
                    HexGrid.hex_distance(
                        HexGrid.coords_to_hex(s.pos), ghex) <= DEFENDER_LEASH
                    for s in battle.ships
                    if HexGrid.coords_to_hex(s.pos) is not None)
                if not covered:
                    leashed = [h for h in valid
                               if HexGrid.hex_distance(h, ghex) <= DEFENDER_LEASH]
                    if leashed:
                        valid = leashed
        return valid

    def _idle_anchor(self, ship, battle):
        """What an idle ship hovers around: escorts guard their miner,
        anomaly-protecting aliens hold position at the anomaly."""
        guard = getattr(ship, 'guard_target', None)
        if guard is not None and battle is not None and \
                guard in battle.ships and not guard.is_dead():
            return HexGrid.coords_to_hex(guard.pos)
        if getattr(ship, 'protect_anomalies', False) and battle is not None:
            shex = HexGrid.coords_to_hex(ship.pos)
            unlooted = [a for a in getattr(battle, 'anomalies', ())
                        if not a.looted]
            if shex and unlooted:
                nearest = min(unlooted, key=lambda a: HexGrid.hex_distance(
                    shex, a.hex_pos))
                return nearest.hex_pos
        return None
