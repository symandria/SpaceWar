import os
from collections import OrderedDict

import pygame

SCREEN_SIZE = (160, 160)

BITBOX = pygame.mask.Mask((9, 9))
BITBOX.fill()

SENTRY_INVALID = (
    (1, 11), (2, 10), (3, 10), (3, 9), (4, 8), (5, 8), (6, 7), (7, 7),
    (7, 6), (8, 6), (8, 5), (9, 5), (10, 4), (11, 4), (12, 3), (12, 2),
    (13, 2), (14, 1),
)

RANKS = (
    "cadet",
    "ensign",
    "lieutenant jg",
    "lieutenant",
    "commander",
    "captain",
    "commodore",
    "rear admiral",
    "vice admiral",
    "admiral",
    "fleet admiral",
    "random",
)

XP_VALUES = [1500, 5000, 12000, 25000]
while len(XP_VALUES) < len(RANKS) - 1:
    i = len(XP_VALUES) - 3
    XP_VALUES.append(25000 * i**2 - 25000 * i + 50000)
XP_VALUES.append(100000000)
while len(XP_VALUES) >= len(RANKS):
    XP_VALUES.pop()

RANK_XP = OrderedDict(zip(RANKS, XP_VALUES))

RANK_PROMOTE = OrderedDict()
for i, rank in enumerate(RANKS[:-1]):
    RANK_PROMOTE[rank] = RANKS[i + 1]

STATS = {
    "shields": {
        "min": 150,
        "max": 2000,
        "step": 15,
    },
    "weapon power": {
        "min": 5,
        "max": 100,
        "step": 1,
    },
    "engine": {
        "min": 5,
        "max": 10,
        "step": 1,
    },
}

INI_DEFAULTS = OrderedDict((
    ('Window', OrderedDict((
        ('Caption', 'SpaceWar'),
        ('Icon', os.path.join('data', 'icon.png')),
    ))),
    ('Data Files', OrderedDict((
        ('Sound folder', os.path.join('data', 'sound')),
        ('Theme folder', os.path.join('data', 'themes')),
        ('Character folder', os.path.join('data', 'saves')),
        ('Localization file', os.path.join('data', 'English.txt')),
        ('Settings file', 'settings.cfg'),
    ))),
))
