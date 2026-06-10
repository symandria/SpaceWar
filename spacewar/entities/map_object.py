import pygame
from spacewar.rendering.hex_grid import HexGrid


RESOURCE_SPOT_COLORS = {
    "scrap": (255, 220, 0),
    "common": (120, 220, 120),
    "uncommon": (80, 160, 255),
    "rare": (200, 80, 255),
}


class Asteroid:
    def __init__(self, hex_pos, resource=None):
        self.hex_pos = hex_pos
        self.pos = HexGrid.hex_to_coords(*hex_pos)
        self.hull = 100
        # (kind, amount) where kind is "scrap" or a material tier;
        # harvestable with a tractor beam, None when empty.
        self.resource = resource
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
            if self.resource:
                color = RESOURCE_SPOT_COLORS.get(self.resource[0], (255, 220, 0))
                pygame.draw.circle(screen, color, (cx, cy), 1)


class Anomaly:
    """Sensor anomaly hidden inside a nebula. Loot it with a tractor
    beam for gear with special properties. Quality scales with how
    dangerous the host nebula is."""

    def __init__(self, hex_pos, quality=1):
        self.hex_pos = hex_pos
        self.pos = HexGrid.hex_to_coords(*hex_pos)
        self.quality = quality
        self.looted = False

    def render(self, screen):
        if self.looted:
            return
        cx = int(self.pos[0]) + 4
        cy = int(self.pos[1]) + 4
        pygame.draw.line(screen, (0, 255, 230), (cx - 2, cy), (cx + 2, cy))
        pygame.draw.line(screen, (0, 255, 230), (cx, cy - 2), (cx, cy + 2))
        pygame.draw.circle(screen, (140, 255, 245), (cx, cy), 3, 1)


class NebulaTile:
    RED = "red"
    GREEN = "green"
    PURPLE = "purple"
    ION = "ion"
    PLASMA = "plasma"
    GRAVITY = "gravity"
    STATIC = "static"
    TACHYON = "tachyon"
    COMET = "comet"
    EVERBRIGHT = "everbright"
    BLACKHOLE = "blackhole"
    SLIPSTREAM = "slipstream"

    COLORS = {
        "red": (180, 40, 40),
        "green": (40, 180, 40),
        "purple": (120, 40, 180),
        "ion": (220, 220, 60),
        "plasma": (255, 120, 0),
        "gravity": (90, 90, 255),
        "static": (150, 150, 150),
        "tachyon": (0, 220, 220),
        "comet": (190, 220, 255),
        "everbright": (255, 255, 190),
        "blackhole": (40, 0, 70),
        "slipstream": (0, 255, 170),
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


# Shown when the player clicks a stellar object within sensor range.
NEBULA_DESCRIPTIONS = {
    "red": ("Red Nebula\nCorrosive gas damages ships passing through "
            "(10% of max strength per hex)."),
    "green": ("Green Nebula\nEnergized particles restore 5% shields "
              "per hex traveled."),
    "purple": ("Purple Nebula\nSensor-opaque: ships inside are hidden "
               "from sensors, but shields collapse to 0 at turn end."),
    "ion": ("Ion Storm\nElectrical surges drain 10% of max shields each "
            "turn inside and disrupt cloaking devices."),
    "plasma": ("Plasma Field\nSuperheated plasma burns 5% of max hull "
               "per hex - shields offer no protection."),
    "gravity": ("Gravity Rift\nIntense gravity drags nearby ships one "
                "hex toward it every turn."),
    "static": ("Static Cloud\nCharged dust halves sensor range while "
               "inside."),
    "tachyon": ("Tachyon Stream\nExotic particles instantly recharge "
                "special systems at turn end."),
    "comet": ("Comet Tail\nIce and grit scour ships passing through, "
              "and the drag slows engines next turn."),
    "everbright": ("Everbright Nebula\nBlinding radiance: halves your "
                   "sensors while inside and burns away any cloak."),
    "blackhole": ("Micro Black Hole\nDrags everything within 3 hexes "
                  "closer each turn; tidal forces crush hulls at "
                  "point-blank range."),
    "slipstream": ("Slipstream Corridor\nRiding the current at turn "
                   "end supercharges your engines next turn."),
}

OBJECT_DESCRIPTIONS = {
    "asteroid": ("Asteroid\nBlocks fire and damages ships on collision. "
                 "A colored spot marks a harvestable resource - use a "
                 "tractor beam."),
    "wreck": ("Ship Wreck\nSalvage with a tractor beam for a component "
              "and materials."),
    "anomaly": ("Sensor Anomaly\nUnknown energy signature. Loot with a "
                "tractor beam for exotic gear."),
    "mine": ("Mine\nDetonates when a ship moves within 1 hex. Dim mines "
             "are not armed yet."),
}
