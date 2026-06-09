import pygame

from spacewar.config.constants import SCREEN_SIZE


class Mine:
    def __init__(self, pos, firer, power):
        self.pos = pos
        self.rect = pygame.Rect(0, 0, 5, 5)
        self.rect.center = pos
        self.firer = firer
        self.power = power
        self.active = True
        self.mask = pygame.mask.Mask((5, 5))
        self.mask.fill()

    def render(self, screen):
        if self.active:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)

    def detonate(self):
        self.active = False
