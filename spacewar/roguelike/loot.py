import random

from spacewar.components.base import Component, ComponentSlot
from spacewar.components.defaults import (
    basic_engine, basic_sensors, basic_shields, basic_hull,
    basic_stealth, basic_power_source,
)
from spacewar.roguelike.upgrades import allocate_upgrade_points
from spacewar.systems.weapons import WeaponType, WEAPON_STATS


# Basic starter gear is tier 0. Dropped gear comes with base upgrade
# points already allocated; player upgrades can add up to 3 more.
BASE_POINTS_BY_TIER = {1: 2, 2: 6, 3: 10}

# Range-fixed weapons (shockwave, mines) get nothing from weapon_range
# points, so they never drop as loot.
DROPPABLE_WEAPON_TYPES = [
    wt for wt in WeaponType if not WEAPON_STATS[wt].get("range_fixed")
]


def base_points_for_tier(tier):
    return BASE_POINTS_BY_TIER.get(tier, 2 + 4 * (tier - 1))


def power_cost_for_tier(base_cost, tier):
    """Components consume +50% more power per tier above tier 0."""
    return int(base_cost * 1.5 ** tier + 0.5)


def generate_battle_loot(tier, enemies_killed, player_won):
    loot = {"scrap": 0, "materials": {}, "components": []}

    base_scrap = 20 * tier
    loot["scrap"] = base_scrap + enemies_killed * (10 + tier * 5)
    if player_won:
        loot["scrap"] += 30 * tier

    for _ in range(enemies_killed):
        roll = random.random()
        if roll < 0.6:
            loot["materials"]["common"] = loot["materials"].get("common", 0) + 1
        if roll < 0.3:
            loot["materials"]["uncommon"] = loot["materials"].get("uncommon", 0) + 1
        if roll < 0.08 * tier:
            loot["materials"]["rare"] = loot["materials"].get("rare", 0) + 1

    if player_won and random.random() < 0.3 + tier * 0.1:
        comp = _random_component(tier)
        if comp:
            loot["components"].append(comp)

    return loot


def generate_salvage_loot(tier):
    loot = {"scrap": 0, "materials": {}, "components": []}
    loot["scrap"] = random.randint(10, 30) * tier
    loot["materials"]["common"] = random.randint(1, 3)
    if random.random() < 0.4:
        loot["materials"]["uncommon"] = random.randint(1, 2)
    if random.random() < 0.15 * tier:
        loot["materials"]["rare"] = 1
    if random.random() < 0.25:
        comp = _random_component(tier)
        if comp:
            loot["components"].append(comp)
    return loot


def _random_special(tier):
    """Every special ability type drops somewhere in the world.
    (Tractor beams are standard equipment, and ambush is a property
    of cloaking devices, not a separate special.)"""
    from spacewar.components.defaults import (
        phasing_special, teleportation_special,
    )
    comp = random.choice([
        phasing_special, teleportation_special,
    ])()
    comp.name = f"Salvaged {comp.name} Mk{tier}"
    comp.power_cost = power_cost_for_tier(comp.power_cost, tier)
    return comp


def _random_component(tier):
    slot = random.choice([
        ComponentSlot.ENGINE, ComponentSlot.SENSORS, ComponentSlot.SHIELDS,
        ComponentSlot.HULL, ComponentSlot.WEAPON_1, ComponentSlot.WEAPON_2,
        ComponentSlot.STEALTH, ComponentSlot.POWER_SOURCE,
        ComponentSlot.SPECIAL,
    ])

    if slot == ComponentSlot.SPECIAL:
        return _random_special(tier)

    if slot == ComponentSlot.ENGINE:
        comp, base_name = basic_engine(), "Engine"
    elif slot == ComponentSlot.SENSORS:
        comp, base_name = basic_sensors(), "Sensors"
    elif slot == ComponentSlot.SHIELDS:
        comp, base_name = basic_shields(), "Shields"
    elif slot == ComponentSlot.HULL:
        comp, base_name = basic_hull(), "Hull"
    elif slot in (ComponentSlot.WEAPON_1, ComponentSlot.WEAPON_2):
        wtype = random.choice(DROPPABLE_WEAPON_TYPES)
        stats = WEAPON_STATS[wtype]
        comp = Component(slot, "", 3, weapon_type=wtype.value,
                         weapon_range=stats["max_range"])
        base_name = stats["display_name"]
    elif slot == ComponentSlot.STEALTH:
        has_cloak = random.random() < 0.3
        # Some cloaking devices come with the ambush property baked
        # in: +200% damage striking from cloak, upgradeable +10%/point.
        has_ambush = has_cloak and random.random() < 0.4
        comp = basic_stealth(active_cloak=has_cloak, ambush=has_ambush)
        if has_ambush:
            base_name = "Ambush Cloaking Device"
        elif has_cloak:
            base_name = "Cloaking Device"
        else:
            base_name = "Stealth Plating"
    elif slot == ComponentSlot.POWER_SOURCE:
        comp, base_name = basic_power_source(), "Reactor"
    else:
        return None

    comp.name = f"Salvaged {base_name} Mk{tier}"
    comp.power_cost = power_cost_for_tier(comp.power_cost, tier)
    allocate_upgrade_points(comp, base_points_for_tier(tier))
    return comp


def generate_anomaly_component(tier, quality=1):
    """Anomaly loot: gear with special properties. Quality (from the
    host nebula's danger) adds bonus points or upgrades the roll."""
    from spacewar.components.defaults import (
        phasing_special, teleportation_special,
    )
    roll = random.random()
    if roll < 0.40:
        comp = random.choice([
            phasing_special, teleportation_special,
        ])()
        comp.name = f"Anomalous {comp.name}"
        return comp
    if roll < 0.60:
        has_cloak = random.random() < 0.25 + quality * 0.05
        # Anomalous cloaks always carry the ambush property.
        comp = basic_stealth(active_cloak=has_cloak, ambush=has_cloak)
        comp.stats["passive_stealth"] = 3
        comp.name = "Anomalous Ambush Cloak" if has_cloak \
            else "Anomalous Stealth Plating"
        comp.power_cost = power_cost_for_tier(comp.power_cost, tier)
        return comp
    comp = _random_component(tier)
    if comp:
        allocate_upgrade_points(comp, quality * 2)
        comp.name = comp.name.replace("Salvaged", "Anomalous")
    return comp


def apply_loot(loot, inventory):
    inventory.add_scrap(loot.get("scrap", 0))
    for mat, amount in loot.get("materials", {}).items():
        inventory.add_material(mat, amount)
    for comp in loot.get("components", []):
        inventory.add_component(comp)


def format_loot(loot):
    lines = []
    if loot["scrap"]:
        lines.append(f"Scrap: +{loot['scrap']}")
    for mat, amount in loot.get("materials", {}).items():
        if amount > 0:
            lines.append(f"{mat.title()}: +{amount}")
    for comp in loot.get("components", []):
        lines.append(f"Found: {comp.name}")
    return "\n".join(lines) if lines else "Nothing found."
