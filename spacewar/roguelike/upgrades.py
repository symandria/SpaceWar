import random

from spacewar.components.base import ComponentSlot


UPGRADE_COSTS = {
    1: {"common": 3, "scrap": 50},
    2: {"uncommon": 2, "common": 2, "scrap": 100},
    3: {"rare": 1, "uncommon": 2, "scrap": 200},
}

# Every component can take up to 3 player upgrades, each worth one
# upgrade point on top of the tier's base points (T1 +2, T2 +6, T3 +10).
MAX_UPGRADE_LEVEL = 3

# Each entry is stat: (step, cost) -- one purchase adds `step` to the
# stat and consumes `cost` upgrade points. Relative values per the
# design notes: +1 acceleration is worth 2 max speed; +1 cloak
# detection is worth 2 vision.
COMPONENT_STAT_STEPS = {
    ComponentSlot.ENGINE: {
        "max_speed": (1, 1),
        "acceleration": (1, 2),
        "turning_degrees": (15, 1),
        "maneuvering_points": (1, 2),
    },
    ComponentSlot.SENSORS: {
        "vision_forward": (2, 1),
        "vision_backward": (1, 1),
        "cloak_detection": (1, 1),
    },
    ComponentSlot.SHIELDS: {
        "strength": (15, 1),
        "passive_regen": (3, 1),
        "active_dr": (10, 1),
    },
    ComponentSlot.HULL: {
        "strength": (10, 1),
        "collision_damage": (10, 1),
    },
    ComponentSlot.WEAPON_1: {"weapon_range": (1, 1)},
    ComponentSlot.WEAPON_2: {"weapon_range": (1, 1)},
    ComponentSlot.STEALTH: {
        "passive_stealth": (1, 1),
        "ambush_bonus": (10, 1),  # +10% strike-from-cloak damage
    },
    ComponentSlot.POWER_SOURCE: {"power_provided": (3, 1)},
}

STAT_CAPS = {
    "acceleration": 6,
    "turning_degrees": 360,
    "active_dr": 50,
    "ambush_bonus": 300,
}

# Stats that can only be raised on components that already have them:
# plain stealth plating can't grow an ambush system from nothing.
GATED_STATS = ("ambush_bonus",)


def allocate_upgrade_points(component, points):
    """Spend upgrade points on randomly chosen stats this component type
    can have, respecting per-stat costs and caps. Returns points spent."""
    steps = COMPONENT_STAT_STEPS.get(component.slot, {})
    remaining = points
    while remaining > 0:
        choices = [
            (stat, step, cost) for stat, (step, cost) in steps.items()
            if cost <= remaining and (
                stat not in STAT_CAPS
                or component.stats.get(stat, 0) + step <= STAT_CAPS[stat])
            and (stat not in GATED_STATS
                 or component.stats.get(stat, 0) > 0)
        ]
        if not choices:
            break
        stat, step, cost = random.choice(choices)
        component.stats[stat] = component.stats.get(stat, 0) + step
        remaining -= cost
    return points - remaining


def get_upgrade_level(component):
    return getattr(component, 'upgrade_level', 0)


def can_upgrade(component, inventory):
    level = get_upgrade_level(component)
    if level >= MAX_UPGRADE_LEVEL:
        return False
    if not COMPONENT_STAT_STEPS.get(component.slot):
        return False
    next_level = level + 1
    costs = UPGRADE_COSTS[next_level]
    for mat, amount in costs.items():
        if mat == "scrap":
            if inventory.scrap < amount:
                return False
        elif not inventory.has_materials(mat, amount):
            return False
    return True


def upgrade_component(component, inventory):
    level = get_upgrade_level(component)
    if level >= MAX_UPGRADE_LEVEL or not can_upgrade(component, inventory):
        return False
    next_level = level + 1
    costs = UPGRADE_COSTS[next_level]
    for mat, amount in costs.items():
        if mat == "scrap":
            inventory.spend_scrap(amount)
        else:
            inventory.spend_material(mat, amount)

    allocate_upgrade_points(component, 1)

    component.upgrade_level = next_level
    suffix = "+" * next_level
    base_name = component.name.rstrip("+").rstrip()
    component.name = f"{base_name} {suffix}"
    return True


def get_upgrade_cost_text(component):
    level = get_upgrade_level(component)
    if level >= MAX_UPGRADE_LEVEL:
        return "Max Level"
    costs = UPGRADE_COSTS[level + 1]
    parts = []
    for mat, amount in costs.items():
        parts.append(f"{amount} {mat}")
    return ", ".join(parts)
