import random

from spacewar.config.constants import GRID_ROWS, SENTRY_INVALID, max_col
from spacewar.rendering.hex_grid import HexGrid


class AISystem:
    def decide_actions(self, ships, player, team_game):
        for enemy in ships:
            if enemy == player:
                continue
            ehex = HexGrid.coords_to_hex(enemy.pos)
            if enemy.type == "sentry":
                enemy.action = "torpedo"
            else:
                enemy.action = random.choice((None, "phaser", "torpedo"))

            valid_targets = []
            valid_movements = []
            for row in range(1, GRID_ROWS + 1):
                for col in range(1, max_col(row) + 1):
                    if enemy.get_valid_destination(row, col, bool(enemy.action)) and \
                            (enemy.type == "sentry" or (row, col) != ehex):
                        valid_movements.append((row, col))
                    if enemy.type == "sentry":
                        if (row, col) not in SENTRY_INVALID:
                            valid_targets.append((row, col))
                    else:
                        for target in ships:
                            if target == enemy or target.cloaked or \
                                    (team_game and target.type == enemy.type):
                                continue
                            thex = HexGrid.coords_to_hex(target.pos)
                            if HexGrid.hex_distance(thex, (row, col)) <= \
                                    min(target.speed + 2, target.engine) // 2:
                                valid_targets.append((row, col))
                                break

            if enemy.action and not valid_targets:
                row = random.randint(1, GRID_ROWS)
                enemy.target = row, random.randint(1, max_col(row))
            elif enemy.action:
                enemy.target = random.choice(valid_targets)

            if valid_movements:
                enemy.movement = random.choice(valid_movements)
            else:
                enemy.movement = ehex

            if (("teleportation" in enemy.specials and not enemy.action) or
                    "teleportation_always" in enemy.specials) and random.random() > 0.5:
                row = random.randint(1, GRID_ROWS)
                enemy.movement = row, random.randint(1, max_col(row))
