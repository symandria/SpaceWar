import pygame


class HexGrid:
    def __init__(self, foreground, background):
        self.foreground = foreground
        self.background = background
        self._build_surfaces()

    def _build_surfaces(self):
        self.hex_tile = pygame.Surface((15, 15))
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
        screen = pygame.Surface((160, 160))
        screen.fill(self.background)
        for row in range(14):
            for column in range(10 if row % 2 else 11):
                screen.blit(self.hex_tile, (2 + 14 * column + (row % 2) * 7, 15 + 10 * row))
        return screen

    @staticmethod
    def hex_to_coords(row, column):
        return (14 * column + ((row - 1) % 2) * 7 - 9, 8 + 10 * row)

    @staticmethod
    def coords_to_hex(pos):
        if pos[0] < 2 or pos[1] < 17 or pos[0] > 155 or pos[1] > 156:
            return None
        elif pos[0] < 9 and (pos[1] - 17) % 20 >= 10:
            return None
        elif (pos[1] - 17) % 20 < 10:
            return (pos[1] - 17) // 10 + 1, (pos[0] - 2) // 14 + 1
        else:
            return (pos[1] - 17) // 10 + 1, (pos[0] - 9) // 14 + 1

    @staticmethod
    def hex_distance(hex1, hex2):
        hex1 = hex1[0], hex1[1] - (hex1[0] + 1) // 2
        hex1 += (0 - hex1[0] - hex1[1],)
        hex2 = hex2[0], hex2[1] - (hex2[0] + 1) // 2
        hex2 += (0 - hex2[0] - hex2[1],)
        return max(abs(hex1[0] - hex2[0]), abs(hex1[1] - hex2[1]), abs(hex1[2] - hex2[2]))
