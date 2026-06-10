from spacewar.components.base import Component, ComponentSlot
from spacewar.components.defaults import (
    build_default_loadout, basic_engine, basic_shields, basic_stealth,
    teleportation_special, ambush_special, no_special,
)


def _weapon(slot_num, weapon_type, weapon_range=15):
    slot = ComponentSlot.WEAPON_1 if slot_num == 1 else ComponentSlot.WEAPON_2
    name = weapon_type.replace("_", " ").title()
    return Component(slot, f"Basic {name}", 3,
                     weapon_type=weapon_type, weapon_range=weapon_range)


RACE_COMPONENT_OVERRIDES = {
    "federation": {
        "shields": lambda: basic_shields(active_dr=50),
        "weapon_1": lambda: _weapon(1, "lazers"),
        "weapon_2": lambda: _weapon(2, "point_lazers"),
    },
    "klingon": {
        "stealth": lambda: basic_stealth(active_cloak=True),
        "weapon_1": lambda: _weapon(1, "disruptors", weapon_range=8),
        "weapon_2": lambda: _weapon(2, "mines", weapon_range=1),
    },
    "tholian": {
        "engine": lambda: basic_engine(acceleration=3),
        "weapon_1": lambda: _weapon(1, "shockwave", weapon_range=2),
        "weapon_2": lambda: _weapon(2, "torpedoes"),
    },
    "dominion": {
        "shields": lambda: _regen_shields(10),
        "weapon_1": lambda: _weapon(1, "he_torpedo", weapon_range=12),
        "weapon_2": lambda: _weapon(2, "lazers"),
    },
    "borg": {
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
        "shields": lambda: _regen_shields(10),
        "weapon_1": lambda: _weapon(1, "lazers"),
        "weapon_2": lambda: _weapon(2, "he_torpedo", weapon_range=12),
    },
    "earth": {
        "special": lambda: teleportation_special(teleport_range=8, recharge=4),
        "weapon_1": lambda: _weapon(1, "lazers"),
        "weapon_2": lambda: _weapon(2, "torpedoes"),
    },
    "minbari": {
        "shields": lambda: _regen_shields(10),
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
        "weapon_1": lambda: _weapon(1, "point_lazers"),
        "weapon_2": lambda: _weapon(2, "disruptors", weapon_range=8),
    },
    "narn": {
        "shields": lambda: basic_shields(active_dr=50),
        "engine": lambda: basic_engine(acceleration=3),
        "weapon_1": lambda: _weapon(1, "torpedoes"),
        "weapon_2": lambda: _weapon(2, "he_torpedo", weapon_range=12),
    },
    "centauri": {
        "shields": lambda: _regen_shields(10, active_dr=50),
        "weapon_1": lambda: _weapon(1, "lazers"),
        "weapon_2": lambda: _weapon(2, "mines", weapon_range=1),
    },
    "shadow": {
        "stealth": lambda: basic_stealth(active_cloak=True),
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
        "shields": lambda: _regen_shields(10),
        "weapon_1": lambda: _weapon(1, "disruptors", weapon_range=8),
        "weapon_2": lambda: _weapon(2, "shockwave", weapon_range=2),
    },
    "terran": {
        "shields": lambda: basic_shields(active_dr=50),
        "weapon_1": lambda: _weapon(1, "lazers"),
        "weapon_2": lambda: _weapon(2, "point_lazers"),
    },
    "psiloth": {
        "stealth": lambda: basic_stealth(active_cloak=True),
        "weapon_1": lambda: _weapon(1, "disruptors", weapon_range=8),
        "weapon_2": lambda: _weapon(2, "torpedoes"),
    },
    "zlorg": {
        "engine": lambda: basic_engine(acceleration=3),
        "weapon_1": lambda: _weapon(1, "shockwave", weapon_range=2),
        "weapon_2": lambda: _weapon(2, "he_torpedo", weapon_range=12),
    },
    "wental": {
        "shields": lambda: _regen_shields(10),
        "weapon_1": lambda: _weapon(1, "lazers"),
        "weapon_2": lambda: _weapon(2, "mines", weapon_range=1),
    },
    "riftbound": {
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
        "shields": lambda: _regen_shields(10),
        "weapon_1": lambda: _weapon(1, "point_lazers"),
        "weapon_2": lambda: _weapon(2, "torpedoes"),
    },
    "sentry": {
        "weapon_1": lambda: _weapon(1, "lazers"),
        "weapon_2": lambda: _weapon(2, "torpedoes"),
    },
}

SLOT_MAP = {
    "engine": ComponentSlot.ENGINE,
    "shields": ComponentSlot.SHIELDS,
    "stealth": ComponentSlot.STEALTH,
    "special": ComponentSlot.SPECIAL,
    "weapon_1": ComponentSlot.WEAPON_1,
    "weapon_2": ComponentSlot.WEAPON_2,
}


def build_race_loadout(race):
    loadout = build_default_loadout()
    overrides = RACE_COMPONENT_OVERRIDES.get(race, {})
    for key, factory in overrides.items():
        slot = SLOT_MAP.get(key)
        if slot:
            loadout.equip(factory())
    return loadout


def _regen_shields(regen_val, active_dr=0):
    shields = basic_shields(active_dr=active_dr)
    shields.stats["passive_regen"] = regen_val
    return shields
