from spacewar.components.base import Component, ComponentSlot


def basic_engine(acceleration=2):
    return Component(
        ComponentSlot.ENGINE, "Basic Engine", 3,
        max_speed=5, acceleration=acceleration,
        turning_degrees=90, maneuvering_points=1,
    )


def basic_sensors():
    return Component(
        ComponentSlot.SENSORS, "Basic Sensors", 2,
        vision_forward=14, vision_backward=7,
        cloak_detection=0,
    )


def basic_shields(active_dr=0):
    return Component(
        ComponentSlot.SHIELDS, "Basic Shields", 4,
        strength=100, passive_regen=2,
        active_regen_mult=1.0, active_dr=active_dr,
    )


def basic_hull():
    return Component(
        ComponentSlot.HULL, "Basic Hull", 2,
        strength=50, collision_damage=25,
    )


def basic_lazers():
    return Component(
        ComponentSlot.WEAPON_1, "Basic Lazers", 3,
        weapon_type="lazers", weapon_range=15,
    )


def basic_torpedoes():
    return Component(
        ComponentSlot.WEAPON_2, "Basic Torpedoes", 3,
        weapon_type="torpedoes", weapon_range=15,
    )


def basic_stealth(active_cloak=False):
    # Cloaking devices start with 0% ambush bonus; both passive
    # stealth and ambush (+10% strike-from-cloak damage per point)
    # are upgrade choices for them.
    power = 3 if active_cloak else 1
    return Component(
        ComponentSlot.STEALTH, "Basic Stealth", power,
        passive_stealth=0, active_cloak=active_cloak, ambush_bonus=0,
    )


def basic_power_source():
    return Component(
        ComponentSlot.POWER_SOURCE, "Basic Power Source", 0,
        power_provided=24,
    )


def no_special():
    return Component(
        ComponentSlot.SPECIAL, "None", 0,
        ability_type=None,
    )


def teleportation_special(teleport_range=10, recharge=3):
    return Component(
        ComponentSlot.SPECIAL, "Teleportation", 3,
        ability_type="teleportation",
        teleport_range=teleport_range, recharge=recharge,
    )


def phasing_special(duration=3, recharge=3):
    return Component(
        ComponentSlot.SPECIAL, "Phasing Device", 3,
        ability_type="phasing",
        duration=duration, recharge=recharge,
    )


def stealth_module_special():
    # Pure passive-stealth special (strength 3); it can also take
    # ambush upgrades, which stack with any other ambush bonuses.
    return Component(
        ComponentSlot.SPECIAL, "Stealth Module", 2,
        ability_type="stealth_module",
        passive_stealth=3, ambush_bonus=0, ambush_capable=True,
    )


def basic_tractor_beam():
    # Standard shipboard equipment, not a special: every hull mounts
    # one for looting asteroids, wrecks and anomalies at range 1.
    return Component(
        ComponentSlot.TRACTOR, "Tractor Beam", 0,
        tractor_range=1,
    )


def build_default_loadout(race_specials=None):
    from spacewar.components.ship_loadout import ShipLoadout
    loadout = ShipLoadout()
    loadout.equip(basic_engine())
    loadout.equip(basic_sensors())
    loadout.equip(basic_shields())
    loadout.equip(basic_hull())
    loadout.equip(basic_lazers())
    loadout.equip(basic_torpedoes())
    loadout.equip(basic_stealth())
    loadout.equip(basic_power_source())
    loadout.equip(basic_tractor_beam())
    loadout.equip(no_special())

    if race_specials:
        _apply_race_specials(loadout, race_specials)

    return loadout


def _apply_race_specials(loadout, specials):
    for special in specials:
        if special == "cloaking" or special == "cloaking_always":
            loadout.equip(basic_stealth(active_cloak=True))
        elif special == "teleportation" or special == "teleportation_always":
            loadout.equip(teleportation_special())
        elif special == "ablative" or special == "ablative_always":
            loadout.equip(basic_shields(active_dr=50))
        elif special == "acceleration" or special == "acceleration_always":
            loadout.equip(basic_engine(acceleration=3))
        elif special == "ambush":
            cloak = basic_stealth(active_cloak=True)
            cloak.stats["ambush_bonus"] = 30  # 3 points of ambush
            loadout.equip(cloak)
        elif special == "regeneration" or special == "regeneration_always":
            _update_shield_regen(loadout, 10)
        elif special.startswith("regen_"):
            regen_val = 5
            if "10" in special:
                regen_val = 10
            elif "15" in special:
                regen_val = 15
            _update_shield_regen(loadout, regen_val)


def _update_shield_regen(loadout, regen_val):
    current = loadout.get_component(ComponentSlot.SHIELDS)
    dr = current.get("active_dr", 0) if current else 0
    shields = basic_shields(active_dr=dr)
    shields.stats["passive_regen"] = regen_val
    loadout.equip(shields)
