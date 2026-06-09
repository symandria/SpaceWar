import pygame
import pygame.gfxdraw

from spacewar.config.constants import BITBOX
from spacewar.rendering.hex_grid import HexGrid


class Ship:
    def __init__(self, ship_type, pos, angle, rank, captain, name,
                 shields, phasers, torpedoes, engine, specials,
                 human=False, pixel_perfect=True):
        self.type = ship_type
        self.specials = specials
        self.pos = pos
        self.angle = angle
        self.rank = rank
        self.captain = captain
        self.name = name
        self.shields = shields
        self.max_shields = shields
        self.phasers = phasers
        self.torpedoes = torpedoes
        self.engine = engine
        self.human = human
        self.pixel_perfect = pixel_perfect
        self.speed = 2
        self.cloaked = False
        self.was_cloaked = False
        self.action = None
        self.target = None
        self.movement = None
        self.shot_recently = 0
        self.explode = 0
        self.regen = 0
        self.move_target = None
        self.teleport_target = None
        self.image = None

    def set_image(self, image):
        self.image = image

    def render(self, screen):
        if self.explode:
            pygame.gfxdraw.filled_circle(
                screen, int(self.pos[0]) + 4, int(self.pos[1]) + 4,
                -self.explode, (255, 127, 0))
        else:
            screen.blit(self.image, self.pos)

    def interpolate_toward(self, target_pos, remaining_frames):
        self.pos = (
            (target_pos[0] - self.pos[0]) / remaining_frames + self.pos[0],
            (target_pos[1] - self.pos[1]) / remaining_frames + self.pos[1],
        )
        if remaining_frames == 1:
            self.pos = (int(self.pos[0]), int(self.pos[1]))

    def rotate(self, angle, sprite_lookup):
        self.angle = angle
        key = "cloaked-" + self.type if self.cloaked else self.type
        self.image = pygame.transform.rotate(sprite_lookup[key], angle)

    def cloak(self, enabled, sprite_lookup):
        self.cloaked = enabled
        self.was_cloaked = enabled
        self.rotate(self.angle, sprite_lookup)

    def apply_damage(self, amount):
        if self.cloaked:
            amount *= 2
        if ("ablative" in self.specials and not self.action) or \
                "ablative_always" in self.specials:
            amount = amount // 2
        self.shields -= amount
        self.shot_recently = 5
        return amount

    def get_valid_destination(self, row, column, attacking):
        ship_hex = HexGrid.coords_to_hex(self.pos)
        dist = HexGrid.hex_distance(ship_hex, (row, column))
        has_accel = (
            ("acceleration" in self.specials and not attacking) or
            "acceleration_always" in self.specials
        )
        buffer = 4 if has_accel else 2
        if dist >= self.speed - buffer and dist <= self.speed + buffer and dist <= self.engine:
            return True
        return False

    @property
    def mask(self):
        if self.pixel_perfect:
            return pygame.mask.from_surface(self.image)
        return BITBOX

    @property
    def center(self):
        return (self.pos[0] + 4, self.pos[1] + 4)
