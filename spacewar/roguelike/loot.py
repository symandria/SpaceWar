import random

from spacewar.components.base import Component, ComponentSlot
from spacewar.systems.weapons import WeaponType, WEAPON_STATS


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


def _random_component(tier):
    slot = random.choice([
        ComponentSlot.ENGINE, ComponentSlot.SENSORS, ComponentSlot.SHIELDS,
        ComponentSlot.HULL, ComponentSlot.WEAPON_1, ComponentSlot.WEAPON_2,
        ComponentSlot.STEALTH,
    ])

    mult = 1.0 + tier * 0.15

    if slot == ComponentSlot.ENGINE:
        return Component(slot, f"Salvaged Engine Mk{tier}", 3 + tier,
                         max_speed=int(5 * mult), acceleration=int(2 * mult),
                         turning_degrees=90, maneuvering_points=1)
    elif slot == ComponentSlot.SENSORS:
        return Component(slot, f"Salvaged Sensors Mk{tier}", 2 + tier,
                         vision_forward=int(10 * mult), vision_backward=int(5 * mult),
                         cloak_detection=tier - 1)
    elif slot == ComponentSlot.SHIELDS:
        return Component(slot, f"Salvaged Shields Mk{tier}", 4 + tier,
                         strength=int(100 * mult), passive_regen=5 + tier * 2,
                         active_regen_mult=1.0, active_dr=0)
    elif slot == ComponentSlot.HULL:
        return Component(slot, f"Salvaged Hull Mk{tier}", 2 + tier,
                         strength=int(50 * mult), collision_damage=int(25 * mult))
    elif slot in (ComponentSlot.WEAPON_1, ComponentSlot.WEAPON_2):
        wtype = random.choice(list(WeaponType))
        stats = WEAPON_STATS[wtype]
        base_range = stats["max_range"]
        return Component(slot, f"Salvaged {stats['display_name']}", 3 + tier,
                         weapon_type=wtype.value,
                         weapon_range=base_range + tier)
    elif slot == ComponentSlot.STEALTH:
        has_cloak = random.random() < 0.3
        return Component(slot, f"Salvaged Stealth Mk{tier}", 2 + tier,
                         passive_stealth=tier, active_cloak=has_cloak)
    return None


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
