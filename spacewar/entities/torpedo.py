import math

import pygame


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
        return (self.rect.bottom < 17 or self.rect.top > 159 or
                self.rect.right < 2 or self.rect.left > 157)

    def render(self, screen):
        screen.fill(self.color, self.rect)

    def deactivate(self):
        self.active = False
