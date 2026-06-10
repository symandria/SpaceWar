import random

from spacewar.rendering.hex_grid import HexGrid


TRACTOR_RANGE = 1


class HarvestSystem:
    """Tractor-beam harvesting: pull resources off asteroids, strip
    wrecks, and crack open nebula anomalies. Loot accumulates on
    battle.harvested and is banked into the run after the battle."""

    def process(self, ship, battle, asset_loader):
        target = ship.target
        ship_hex = HexGrid.coords_to_hex(ship.pos)
        if target is None or ship_hex is None:
            return False
        if not ship.loadout.has_tractor():
            return False
        # The beam needs a full turn of contact: you must start the
        # turn within 1 hex of the target and may orbit it, but not
        # leave that range while harvesting.
        start_hex = getattr(ship, 'turn_start_hex', None) or ship_hex
        if HexGrid.hex_distance(start_hex, target) > TRACTOR_RANGE:
            return False
        dest = ship.movement
        if dest is not None and \
                HexGrid.hex_distance(dest, target) > TRACTOR_RANGE:
            return False
        harvested = getattr(battle, 'harvested', None)
        if harvested is None:
            return False

        for anomaly in getattr(battle, 'anomalies', ()):
            if anomaly.hex_pos == target and not anomaly.looted:
                anomaly.looted = True
                tier = getattr(battle, 'tier', 1)
                from spacewar.roguelike.loot import generate_anomaly_component
                comp = generate_anomaly_component(tier, anomaly.quality)
                if comp:
                    harvested["components"].append(comp)
                asset_loader.play_sound("teleport")
                return True

        for ast in battle.asteroids:
            if ast.hex_pos == target and not ast.is_dead() and ast.resource:
                kind, amount = ast.resource
                if kind == "scrap":
                    harvested["scrap"] += amount
                else:
                    harvested["materials"][kind] = \
                        harvested["materials"].get(kind, 0) + amount
                ast.resource = None
                asset_loader.play_sound("teleport")
                return True

        for wreck in battle.wrecks:
            if wreck.hex_pos == target and not wreck.salvaged:
                wreck.salvaged = True
                tier = getattr(battle, 'tier', 1)
                from spacewar.roguelike.loot import _random_component
                comp = _random_component(tier)
                if comp:
                    harvested["components"].append(comp)
                harvested["materials"]["common"] = \
                    harvested["materials"].get("common", 0) + random.randint(1, 2)
                cargo = getattr(wreck, 'cargo', None)
                if cargo:
                    # A dead miner's hold spills into its wreck.
                    harvested["scrap"] += cargo.get("scrap", 0)
                    for mat, amount in cargo.get("materials", {}).items():
                        harvested["materials"][mat] = \
                            harvested["materials"].get(mat, 0) + amount
                asset_loader.play_sound("teleport")
                return True

        return False


def roll_asteroid_resource(tier):
    """Random harvestable for an asteroid, weighted by rarity."""
    roll = random.random()
    if roll < 0.50:
        return ("scrap", random.randint(10, 25) * tier)
    if roll < 0.80:
        return ("common", random.randint(1, 2))
    if roll < 0.95:
        return ("uncommon", 1)
    return ("rare", 1)
