import pygame

from spacewar.rendering.hex_grid import HexGrid


class Mine:
    """Proximity mine. Drops unarmed, arms once its owner is 2+ hexes
    away, then detonates when any ship comes within 1 hex."""

    def __init__(self, pos, firer, power):
        self.pos = pos
        self.rect = pygame.Rect(0, 0, 5, 5)
        self.rect.center = pos
        self.firer = firer
        self.power = power
        self.active = True
        self.armed = False
        self.mask = pygame.mask.Mask((5, 5))
        self.mask.fill()

    @property
    def hex_pos(self):
        return HexGrid.coords_to_hex(self.pos)

    def render(self, screen):
        if not self.active:
            return
        color = (255, 0, 0) if self.armed else (140, 60, 60)
        pygame.draw.rect(screen, color, self.rect, 1)

    def detonate(self):
        self.active = False
