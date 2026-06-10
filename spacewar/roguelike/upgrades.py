from spacewar.components.base import Component


UPGRADE_COSTS = {
    1: {"common": 3, "scrap": 50},
    2: {"uncommon": 2, "common": 2, "scrap": 100},
    3: {"rare": 1, "uncommon": 2, "scrap": 200},
}

UPGRADE_MULTIPLIERS = {
    1: 1.25,
    2: 1.50,
    3: 2.00,
}

UPGRADEABLE_STATS = {
    "max_speed", "acceleration", "turning_degrees", "maneuvering_points",
    "vision_forward", "vision_backward", "cloak_detection",
    "strength", "passive_regen", "active_dr",
    "collision_damage", "weapon_range", "passive_stealth",
    "power_provided", "teleport_range",
}

NON_SCALING_STATS = {"weapon_type", "ability_type", "active_cloak", "active_regen_mult",
                      "range_fixed", "recharge", "duration"}


def get_upgrade_level(component):
    return getattr(component, 'upgrade_level', 0)


def can_upgrade(component, inventory):
    level = get_upgrade_level(component)
    if level >= 3:
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
    if level >= 3 or not can_upgrade(component, inventory):
        return False
    next_level = level + 1
    costs = UPGRADE_COSTS[next_level]
    for mat, amount in costs.items():
        if mat == "scrap":
            inventory.spend_scrap(amount)
        else:
            inventory.spend_material(mat, amount)

    mult = UPGRADE_MULTIPLIERS[next_level]
    for key, value in component.stats.items():
        if key in UPGRADEABLE_STATS and isinstance(value, (int, float)):
            if isinstance(value, int):
                component.stats[key] = max(value + 1, int(value * mult))
            else:
                component.stats[key] = round(value * mult, 2)

    component.upgrade_level = next_level
    suffix = "+" * next_level
    base_name = component.name.rstrip("+").rstrip()
    component.name = f"{base_name} {suffix}"
    return True


def get_upgrade_cost_text(component):
    level = get_upgrade_level(component)
    if level >= 3:
        return "Max Level"
    costs = UPGRADE_COSTS[level + 1]
    parts = []
    for mat, amount in costs.items():
        parts.append(f"{amount} {mat}")
    return ", ".join(parts)
