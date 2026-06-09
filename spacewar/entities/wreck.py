import pygame
from spacewar.rendering.hex_grid import HexGrid


class Wreck:
    def __init__(self, hex_pos, ship_type, ship_rank):
        self.hex_pos = hex_pos
        self.pos = HexGrid.hex_to_coords(*hex_pos)
        self.ship_type = ship_type
        self.ship_rank = ship_rank
        self.salvaged = False

    def render(self, screen):
        if self.salvaged:
            return
        cx = int(self.pos[0]) + 4
        cy = int(self.pos[1]) + 4
        pygame.draw.circle(screen, (100, 100, 100), (cx, cy), 3)
        pygame.draw.line(screen, (80, 80, 80), (cx - 3, cy - 2), (cx + 2, cy + 3))
        pygame.draw.line(screen, (80, 80, 80), (cx + 3, cy - 2), (cx - 2, cy + 3))
