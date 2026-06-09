import random

from spacewar.config.constants import GRID_ROWS, SENTRY_INVALID, max_col
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.weapons import WeaponType, WEAPON_STATS


class AISystem:
    def decide_actions(self, ships, player, team_game):
        for enemy in ships:
            if enemy == player:
                continue
            ehex = HexGrid.coords_to_hex(enemy.pos)

            enemies_of = [s for s in ships if s != enemy and not s.is_dead()
                          and not (team_game and s.type == enemy.type)]
            nearest = self._find_nearest_enemy(enemy, enemies_of)

            if enemy.type == "sentry":
                enemy.action = "weapon_2"
            else:
                enemy.action = self._choose_action(enemy, nearest)

            if enemy.action in ("weapon_1", "weapon_2"):
                target_hex = self._choose_target(enemy, nearest, enemies_of)
                enemy.target = target_hex
            elif enemy.action == "regen_shields":
                enemy.target = None

            enemy.movement = self._choose_movement(enemy, ehex, nearest, enemies_of)

            has_teleport = (enemy.loadout.has_special("teleportation") and
                            enemy.teleport_cooldown == 0)
            if has_teleport and enemy.hull < enemy.max_hull * 0.3:
                safe_row = random.randint(3, GRID_ROWS - 2)
                enemy.movement = safe_row, random.randint(2, max_col(safe_row) - 1)

    def _find_nearest_enemy(self, ship, enemies):
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        nearest = None
        nearest_dist = 999
        for e in enemies:
            if e.cloaked:
                continue
            ehex = HexGrid.coords_to_hex(e.pos)
            d = HexGrid.hex_distance(ship_hex, ehex)
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
            return None

        ship_hex = HexGrid.coords_to_hex(ship.pos)
        target_hex = HexGrid.coords_to_hex(nearest.pos)
        dist = HexGrid.hex_distance(ship_hex, target_hex)

        w1 = ship.loadout.get_weapon(1)
        w2 = ship.loadout.get_weapon(2)
        w1_range = w1.get("weapon_range", 15) if w1 else 0
        w2_range = w2.get("weapon_range", 15) if w2 else 0

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
            row = random.randint(1, GRID_ROWS)
            return row, random.randint(1, max_col(row))

        thex = HexGrid.coords_to_hex(nearest.pos)
        lead_offset = min(nearest.speed, 2)
        if lead_offset > 0:
            dr = random.randint(-lead_offset, lead_offset)
            dc = random.randint(-lead_offset, lead_offset)
            row = max(1, min(GRID_ROWS, thex[0] + dr))
            col = max(1, min(max_col(row), thex[1] + dc))
            return row, col
        return thex

    def _choose_movement(self, ship, current_hex, nearest, enemies):
        valid = []
        for row in range(1, GRID_ROWS + 1):
            for col in range(1, max_col(row) + 1):
                if ship.get_valid_destination(row, col, bool(ship.action)) and \
                        (ship.type == "sentry" or (row, col) != current_hex):
                    valid.append((row, col))

        if not valid:
            return current_hex

        if nearest is None:
            return random.choice(valid)

        target_hex = HexGrid.coords_to_hex(nearest.pos)
        w1 = ship.loadout.get_weapon(1)
        ideal_range = w1.get("weapon_range", 15) // 2 if w1 else 5

        if ship.hull < ship.max_hull * 0.25:
            valid.sort(key=lambda h: -HexGrid.hex_distance(h, target_hex))
            return valid[0]

        best = min(valid,
                   key=lambda h: abs(HexGrid.hex_distance(h, target_hex) - ideal_range))
        return best
