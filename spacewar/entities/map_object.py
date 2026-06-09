import pygame
from spacewar.rendering.hex_grid import HexGrid


class Asteroid:
    def __init__(self, hex_pos):
        self.hex_pos = hex_pos
        self.pos = HexGrid.hex_to_coords(*hex_pos)
        self.hull = 100
        self.rect = pygame.Rect(0, 0, 9, 9)
        self.rect.topleft = self.pos
        self.mask = pygame.mask.Mask((9, 9))
        self.mask.fill()

    def apply_damage(self, amount):
        self.hull -= amount
        return amount

    def is_dead(self):
        return self.hull <= 0

    def render(self, screen):
        if not self.is_dead():
            cx = int(self.pos[0]) + 4
            cy = int(self.pos[1]) + 4
            pts = [(cx, cy - 4), (cx + 3, cy - 2), (cx + 4, cy + 1),
                   (cx + 2, cy + 4), (cx - 2, cy + 3), (cx - 4, cy),
                   (cx - 3, cy - 3)]
            pygame.draw.polygon(screen, (160, 160, 160), pts)
            pygame.draw.polygon(screen, (100, 100, 100), pts, 1)


class NebulaTile:
    RED = "red"
    GREEN = "green"
    PURPLE = "purple"

    COLORS = {
        "red": (180, 40, 40),
        "green": (40, 180, 40),
        "purple": (120, 40, 180),
    }

    def __init__(self, hex_pos, nebula_type):
        self.hex_pos = hex_pos
        self.nebula_type = nebula_type
        self.pos = HexGrid.hex_to_coords(*hex_pos)
        self.color = self.COLORS[nebula_type]

    def render(self, screen):
        cx = int(self.pos[0]) + 4
        cy = int(self.pos[1]) + 4
        r, g, b = self.color
        dim_color = (r // 3, g // 3, b // 3)
        pygame.draw.circle(screen, dim_color, (cx, cy), 6)
