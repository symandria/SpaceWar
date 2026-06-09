from spacewar.components.base import ComponentSlot
from spacewar.components.defaults import (
    build_default_loadout, basic_engine, basic_shields, basic_stealth,
    teleportation_special, ambush_special, no_special,
)

RACE_COMPONENT_OVERRIDES = {
    "federation": {
        "shields": lambda: basic_shields(active_dr=50),
    },
    "klingon": {
        "stealth": lambda: basic_stealth(active_cloak=True),
    },
    "tholian": {
        "engine": lambda: basic_engine(acceleration=3),
    },
    "dominion": {
        "shields": lambda: _regen_shields(10),
    },
    "borg": {
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
        "shields": lambda: _regen_shields(10),
    },
    "earth": {
        "special": lambda: teleportation_special(teleport_range=8, recharge=4),
    },
    "minbari": {
        "shields": lambda: _regen_shields(10),
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
    },
    "narn": {
        "shields": lambda: basic_shields(active_dr=50),
        "engine": lambda: basic_engine(acceleration=3),
    },
    "centauri": {
        "shields": lambda: _regen_shields(10, active_dr=50),
    },
    "shadow": {
        "stealth": lambda: basic_stealth(active_cloak=True),
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
        "shields": lambda: _regen_shields(10),
    },
    "terran": {
        "shields": lambda: basic_shields(active_dr=50),
    },
    "psiloth": {
        "stealth": lambda: basic_stealth(active_cloak=True),
    },
    "zlorg": {
        "engine": lambda: basic_engine(acceleration=3),
    },
    "wental": {
        "shields": lambda: _regen_shields(10),
    },
    "riftbound": {
        "special": lambda: teleportation_special(teleport_range=10, recharge=3),
        "shields": lambda: _regen_shields(10),
    },
    "sentry": {},
}

SLOT_MAP = {
    "engine": ComponentSlot.ENGINE,
    "shields": ComponentSlot.SHIELDS,
    "stealth": ComponentSlot.STEALTH,
    "special": ComponentSlot.SPECIAL,
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
