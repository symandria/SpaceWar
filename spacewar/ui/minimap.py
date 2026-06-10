import pygame
from spacewar.config import constants
from spacewar.rendering.hex_grid import HexGrid


class Minimap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.scale_x = width / (constants.GRID_COLS_ODD + 1)
        self.scale_y = height / (constants.GRID_ROWS + 1)

    def render(self, display, battle, viewport_rect, x_pos, y_pos,
               visible_hexes=None):
        """visible_hexes: hexes the player can currently see; anything
        outside is omitted so the minimap never reveals unexplored
        information."""
        # Board size can change between battles.
        self.scale_x = self.width / (constants.GRID_COLS_ODD + 1)
        self.scale_y = self.height / (constants.GRID_ROWS + 1)
        self.surface.fill((10, 10, 20))
        pygame.draw.rect(self.surface, (40, 40, 60),
                         self.surface.get_rect(), 1)

        def seen(hex_pos):
            return visible_hexes is None or hex_pos in visible_hexes

        for neb in battle.nebulae:
            if not seen(neb.hex_pos):
                continue
            r, c = neb.hex_pos
            mx = int(c * self.scale_x)
            my = int(r * self.scale_y)
            color = tuple(max(30, v // 2) for v in neb.color)
            self.surface.set_at((min(mx, self.width - 1), min(my, self.height - 1)), color)

        for ast in battle.asteroids:
            if ast.is_dead() or not seen(ast.hex_pos):
                continue
            r, c = ast.hex_pos
            mx = int(c * self.scale_x)
            my = int(r * self.scale_y)
            self.surface.set_at((min(mx, self.width - 1), min(my, self.height - 1)), (120, 120, 120))

        for wreck in battle.wrecks:
            if wreck.salvaged or not seen(wreck.hex_pos):
                continue
            r, c = wreck.hex_pos
            mx = int(c * self.scale_x)
            my = int(r * self.scale_y)
            self.surface.set_at((min(mx, self.width - 1), min(my, self.height - 1)), (80, 80, 80))

        for ship in battle.ships:
            shex = HexGrid.coords_to_hex(ship.pos)
            if shex is None:
                continue
            if ship != battle.player and not seen(shex):
                continue
            r, c = shex
            mx = int(c * self.scale_x)
            my = int(r * self.scale_y)
            mx = min(mx, self.width - 2)
            my = min(my, self.height - 2)
            if ship == battle.player:
                color = (0, 255, 0)
            elif (getattr(ship, 'is_shop', False) or
                  getattr(ship, 'neutral', False)) and \
                    not getattr(ship, 'hostile', False):
                color = (255, 220, 0)
            elif ship.cloaked:
                continue
            elif battle.team_game and battle.player and ship.type == battle.player.type:
                color = (0, 200, 255)
            else:
                color = (255, 60, 60)
            pygame.draw.rect(self.surface, color, (mx, my, 2, 2))

        display.blit(self.surface, (x_pos, y_pos))
