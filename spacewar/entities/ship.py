import pygame
import pygame.gfxdraw

from spacewar.config.constants import BITBOX
from spacewar.components.base import ComponentSlot
from spacewar.components.defaults import build_default_loadout
from spacewar.rendering.hex_grid import HexGrid


class Ship:
    def __init__(self, ship_type, pos, angle, rank, captain, name,
                 shields, weapon_power, engine, loadout=None, specials=None,
                 human=False, pixel_perfect=True):
        self.type = ship_type
        self.pos = pos
        self.angle = angle
        self.rank = rank
        self.captain = captain
        self.name = name
        self.human = human
        self.pixel_perfect = pixel_perfect

        if loadout is not None:
            self.loadout = loadout
        else:
            self.loadout = build_default_loadout(specials or [])

        self.weapon_power = weapon_power

        self.shields = min(shields, self.max_shields)
        self.hull = self.max_hull

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

    @property
    def max_shields(self):
        return self.loadout.get_stat(ComponentSlot.SHIELDS, "strength", 100)

    @property
    def max_hull(self):
        return self.loadout.get_stat(ComponentSlot.HULL, "strength", 50)

    @property
    def engine(self):
        return self.loadout.get_stat(ComponentSlot.ENGINE, "max_speed", 5)

    @property
    def acceleration(self):
        return self.loadout.get_stat(ComponentSlot.ENGINE, "acceleration", 2)

    @property
    def turning_degrees(self):
        return self.loadout.get_stat(ComponentSlot.ENGINE, "turning_degrees", 90)

    @property
    def maneuvering_points(self):
        return self.loadout.get_stat(ComponentSlot.ENGINE, "maneuvering_points", 1)

    @property
    def passive_regen(self):
        return self.loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen", 5)

    @property
    def active_regen_mult(self):
        return self.loadout.get_stat(ComponentSlot.SHIELDS, "active_regen_mult", 1.0)

    @property
    def active_dr(self):
        return self.loadout.get_stat(ComponentSlot.SHIELDS, "active_dr", 0)

    @property
    def collision_damage(self):
        return self.loadout.get_stat(ComponentSlot.HULL, "collision_damage", 25)

    @property
    def active_cloak(self):
        return self.loadout.get_stat(ComponentSlot.STEALTH, "active_cloak", False)

    @property
    def passive_stealth(self):
        return self.loadout.get_stat(ComponentSlot.STEALTH, "passive_stealth", 0)

    @property
    def vision_forward(self):
        return self.loadout.get_stat(ComponentSlot.SENSORS, "vision_forward", 10)

    @property
    def vision_backward(self):
        return self.loadout.get_stat(ComponentSlot.SENSORS, "vision_backward", 5)

    @property
    def cloak_detection(self):
        return self.loadout.get_stat(ComponentSlot.SENSORS, "cloak_detection", 0)

    @property
    def phasers(self):
        return self.weapon_power * 2

    @property
    def torpedoes(self):
        return self.weapon_power * 3

    @property
    def specials(self):
        result = []
        if self.active_cloak:
            if self.active_dr > 0:
                result.append("cloaking_always")
            else:
                result.append("cloaking")
        if self.loadout.has_special("teleportation"):
            result.append("teleportation")
        if self.acceleration > 2:
            result.append("acceleration")
        if self.loadout.has_special("ambush"):
            result.append("ambush")
        if self.active_dr > 0:
            result.append("ablative")
        if self.passive_regen > 5:
            result.append("regeneration")
        return result

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
        if key in sprite_lookup:
            self.image = pygame.transform.rotate(sprite_lookup[key], angle)

    def cloak(self, enabled, sprite_lookup):
        self.cloaked = enabled
        self.was_cloaked = enabled
        self.rotate(self.angle, sprite_lookup)

    def apply_damage(self, amount):
        if self.cloaked:
            amount *= 2
        if self.active_dr > 0 and not self.action:
            amount = int(amount * (100 - self.active_dr) / 100)
        shield_damage = min(amount, max(self.shields, 0))
        self.shields -= shield_damage
        remaining = amount - shield_damage
        if remaining > 0:
            self.hull -= remaining
        self.shot_recently = 5
        return amount

    def is_dead(self):
        return self.hull < 0

    def get_valid_destination(self, row, column, attacking):
        ship_hex = HexGrid.coords_to_hex(self.pos)
        dist = HexGrid.hex_distance(ship_hex, (row, column))
        buffer = self.acceleration
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
