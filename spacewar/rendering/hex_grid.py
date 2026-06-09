import pygame

from spacewar.config.constants import (
    GRID_ROWS, GRID_COLS_ODD, GRID_COLS_EVEN, SCREEN_SIZE,
    HEX_SPACING_X, HEX_SPACING_Y, HEX_OFFSET_X, HEX_TILE_SIZE,
    GRID_MARGIN_X, GRID_MARGIN_Y, PLAY_AREA_TOP, SPRITE_HALF, max_col,
)


class HexGrid:
    def __init__(self, foreground, background):
        self.foreground = foreground
        self.background = background
        self._build_surfaces()

    def _build_surfaces(self):
        self.hex_tile = pygame.Surface((HEX_TILE_SIZE, HEX_TILE_SIZE))
        self.hex_tile.fill(self.background)
        self.hex_tile.set_colorkey(self.background)
        hex_points = (
            (7, 0), (6, 1), (5, 1), (4, 2), (3, 2), (2, 3), (1, 3),
            (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
            (1, 11), (2, 11), (3, 12), (4, 12), (5, 13), (6, 13), (7, 14),
            (8, 13), (9, 13), (10, 12), (11, 12), (12, 11), (13, 11),
            (14, 10), (14, 9), (14, 8), (14, 7), (14, 6), (14, 5), (14, 4),
            (13, 3), (12, 3), (11, 2), (10, 2), (9, 1), (8, 1),
        )
        for pt in hex_points:
            self.hex_tile.set_at(pt, self.foreground)

        self.select_surface = pygame.Surface((11, 11))
        self.select_surface.fill(self.background)
        self.select_surface.set_colorkey(self.background)
        self.invalid_surface = pygame.Surface((11, 11))
        self.invalid_surface.fill(self.background)
        self.invalid_surface.set_colorkey(self.background)
        diamond_points = (
            (5, 0), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1),
            (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2),
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4),
            (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5),
            (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6),
            (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7),
            (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8),
            (3, 9), (4, 9), (5, 9), (6, 9), (7, 9),
            (5, 10),
        )
        for pt in diamond_points:
            self.select_surface.set_at(pt, (99, 255, 156))
            self.invalid_surface.set_at(pt, (206, 207, 156))

    def build_background(self):
        screen = pygame.Surface(SCREEN_SIZE)
        screen.fill(self.background)
        for row in range(GRID_ROWS):
            cols = GRID_COLS_EVEN if row % 2 else GRID_COLS_ODD
            for column in range(cols):
                screen.blit(self.hex_tile, (
                    GRID_MARGIN_X + HEX_SPACING_X * column + (row % 2) * HEX_OFFSET_X,
                    GRID_MARGIN_Y + HEX_SPACING_Y * row,
                ))
        return screen

    @staticmethod
    def hex_to_coords(row, column):
        return (
            HEX_SPACING_X * column + ((row - 1) % 2) * HEX_OFFSET_X - (HEX_SPACING_X - SPRITE_HALF - 1),
            (GRID_MARGIN_Y - HEX_OFFSET_X) + HEX_SPACING_Y * row,
        )

    @staticmethod
    def coords_to_hex(pos):
        x, y = pos
        x_min = GRID_MARGIN_X
        y_min = PLAY_AREA_TOP
        x_max = GRID_MARGIN_X + (GRID_COLS_ODD - 1) * HEX_SPACING_X + HEX_TILE_SIZE - 2
        y_max = PLAY_AREA_TOP + GRID_ROWS * HEX_SPACING_Y - 1
        if x < x_min or y < y_min or x > x_max or y > y_max:
            return None
        elif x < x_min + HEX_OFFSET_X and (y - y_min) % (2 * HEX_SPACING_Y) >= HEX_SPACING_Y:
            return None
        elif (y - y_min) % (2 * HEX_SPACING_Y) < HEX_SPACING_Y:
            return (y - y_min) // HEX_SPACING_Y + 1, (x - x_min) // HEX_SPACING_X + 1
        else:
            return (y - y_min) // HEX_SPACING_Y + 1, (x - x_min - HEX_OFFSET_X) // HEX_SPACING_X + 1

    @staticmethod
    def hex_distance(hex1, hex2):
        hex1 = hex1[0], hex1[1] - (hex1[0] + 1) // 2
        hex1 += (0 - hex1[0] - hex1[1],)
        hex2 = hex2[0], hex2[1] - (hex2[0] + 1) // 2
        hex2 += (0 - hex2[0] - hex2[1],)
        return max(abs(hex1[0] - hex2[0]), abs(hex1[1] - hex2[1]), abs(hex1[2] - hex2[2]))
