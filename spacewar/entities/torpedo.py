import math

import pygame

from spacewar.config import constants
from spacewar.config.constants import PLAY_AREA_TOP, GRID_MARGIN_X


class Torpedo:
    def __init__(self, pos, target, firer, power, color):
        self.rect = pygame.Rect(0, 0, 3, 3)
        self.rect.center = pos
        self.pos = pos
        delta = target[0] - pos[0], target[1] - pos[1]
        if abs(delta[0]) <= 0.01 and abs(delta[1]) <= 0.01:
            self.dx, self.dy = 3.0, 0.0
        else:
            dist = math.hypot(*delta)
            self.dx = (delta[0] / dist) * 3
            self.dy = (delta[1] / dist) * 3
        self.firer = firer
        self.power = power
        self.color = color
        self.mask = pygame.mask.Mask((3, 3))
        self.mask.fill()
        self.active = True

    def advance(self):
        if self.active:
            self.pos = (self.pos[0] + self.dx, self.pos[1] + self.dy)
            self.rect.center = self.pos

    def is_off_screen(self):
        screen_size = constants.SCREEN_SIZE
        return (self.rect.bottom < PLAY_AREA_TOP or
                self.rect.top > screen_size[1] - 1 or
                self.rect.right < GRID_MARGIN_X or
                self.rect.left > screen_size[0] - 3)

    def render(self, screen):
        screen.fill(self.color, self.rect)

    def deactivate(self):
        self.active = False
