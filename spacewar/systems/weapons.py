import math
from enum import Enum


class WeaponType(Enum):
    LAZERS = "lazers"
    TORPEDOES = "torpedoes"
    DISRUPTORS = "disruptors"
    POINT_LAZERS = "point_lazers"
    SHOCKWAVE = "shockwave"
    HE_TORPEDO = "he_torpedo"
    MINES = "mines"


WEAPON_STATS = {
    # damage_per_hit is per firing tick, rounded up; full-turn damage is
    # damage_per_hit * hits. Totals are relative to the torpedo baseline
    # (1x = 4 * weapon power): lazers 1.66x, disruptors 1.4x, point
    # lazers 0.4x, shockwave 0.7x, HE torpedo 0.7x, mines 2x.
    WeaponType.LAZERS: {
        "display_name": "Lazers",
        "max_range": 15,
        "hits": 5,
        "damage_per_hit": lambda wp: max(1, math.ceil(wp * 6.6 / 5)),
        "projectile": False,
        "fire_type": "hitscan_multi",
    },
    WeaponType.TORPEDOES: {
        "display_name": "Torpedoes",
        "max_range": 15,
        "hits": 1,
        "damage_per_hit": lambda wp: wp * 4,  # baseline (1x)
        "projectile": True,
        "speed": 3.0,
        "fire_type": "projectile",
    },
    WeaponType.DISRUPTORS: {
        "display_name": "Disruptors",
        "max_range": 8,
        "hits": 6,  # 2 bolts per volley x 3 volleys
        "damage_per_hit": lambda wp: max(1, math.ceil(wp * 5.6 / 6)),
        "projectile": True,
        "speed": 3.0,
        "fire_type": "projectile_burst",
        "volleys": 3,
        "bolts_per_volley": 2,
    },
    WeaponType.POINT_LAZERS: {
        "display_name": "Point Lazers",
        "max_range": 15,
        "hits": 1,
        "damage_per_hit": lambda wp: max(1, math.ceil(wp * 1.6)),
        "projectile": False,
        "fire_type": "instant_hit",
    },
    WeaponType.SHOCKWAVE: {
        "display_name": "Shockwave",
        "max_range": 2,
        "hits": 1,
        "damage_per_hit": lambda wp: max(1, math.ceil(wp * 2.8)),
        "projectile": False,
        "fire_type": "aoe_self",
        "aoe_radius": 2,
        "range_fixed": True,
    },
    WeaponType.HE_TORPEDO: {
        "display_name": "HE Torpedo",
        "max_range": 12,
        "hits": 1,
        "damage_per_hit": lambda wp: max(1, math.ceil(wp * 2.8)),
        "projectile": True,
        "speed": 3.0,
        "fire_type": "projectile_aoe",
        "aoe_radius": 1,
        "arm_distance": 2,
    },
    WeaponType.MINES: {
        "display_name": "Mines",
        "max_range": 1,  # drop range: own hex or adjacent
        "hits": 1,
        "damage_per_hit": lambda wp: wp * 6,  # 1.5x baseline
        "projectile": False,
        "fire_type": "mine",
        "range_fixed": True,
    },
}


def get_weapon_damage(weapon_type, weapon_power):
    stats = WEAPON_STATS[weapon_type]
    return stats["damage_per_hit"](weapon_power) * stats["hits"]


def get_weapon_display_name(weapon_type):
    return WEAPON_STATS[weapon_type]["display_name"]


def get_weapon_range(weapon_type):
    return WEAPON_STATS[weapon_type]["max_range"]
