import pygame
from spacewar.config import constants


VIEWPORT_SIZE = (160, 160)


class Viewport:
    def __init__(self):
        screen_size = constants.SCREEN_SIZE
        self.center = (screen_size[0] // 2, screen_size[1] // 2)
        self.size = VIEWPORT_SIZE

    def update(self, ship_pos, sensor_range=10):
        screen_size = constants.SCREEN_SIZE
        target_x = int(ship_pos[0]) + 4
        target_y = int(ship_pos[1]) + 4
        half_w = self.size[0] // 2
        half_h = self.size[1] // 2

        x = max(half_w, min(target_x, screen_size[0] - half_w))
        y = max(half_h, min(target_y, screen_size[1] - half_h))
        self.center = (x, y)

    def get_view_rect(self):
        half_w = self.size[0] // 2
        half_h = self.size[1] // 2
        return pygame.Rect(
            self.center[0] - half_w,
            self.center[1] - half_h,
            self.size[0], self.size[1],
        )

    def world_to_screen(self, world_pos):
        rect = self.get_view_rect()
        return (world_pos[0] - rect.left, world_pos[1] - rect.top)

    def screen_to_world(self, screen_pos):
        rect = self.get_view_rect()
        return (screen_pos[0] + rect.left, screen_pos[1] + rect.top)
