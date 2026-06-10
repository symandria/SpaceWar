import random
from enum import Enum

from spacewar.config.constants import RANKS


class NodeType(Enum):
    BATTLE = "battle"
    ELITE = "elite"
    SHOP = "shop"
    SALVAGE = "salvage"
    REST = "rest"
    EVENT = "event"
    BOSS = "boss"
    START = "start"


NODE_ICONS = {
    NodeType.BATTLE: "!",
    NodeType.ELITE: "!!",
    NodeType.SHOP: "$",
    NodeType.SALVAGE: "?",
    NodeType.REST: "R",
    NodeType.EVENT: "E",
    NodeType.BOSS: "B",
    NodeType.START: "S",
}

TIER_RANKS = {
    1: ["cadet", "ensign", "lieutenant jg"],
    2: ["lieutenant", "commander", "captain"],
    3: ["commodore", "rear admiral", "vice admiral"],
}

TIER_ENEMY_COUNTS = {
    1: (1, 2),
    2: (2, 3),
    3: (2, 3),
}

BOSS_RANKS = {
    1: "captain",
    2: "rear admiral",
    3: "fleet admiral",
}

# Classic is the base theme; difficulty scales by rank/count per tier,
# not by race.
BASE_RACES = ("federation", "klingon", "tholian", "dominion", "borg")

# Terrain definitions. Asteroid counts target roughly 5-10% of the
# ~600 board hexes for fields. Every terrain has something to harvest
# except open space, which instead brings extra (un-teamed) hostiles.
ENVIRONMENTS = {
    "clear": {
        "label": "Open Space", "weight": 1,
        "asteroids": (2, 5), "harvestable": False, "extra_enemies": 1,
        "nebula": None, "clusters": 0,
        "anomaly_chance": 0.0, "anomaly_quality": 0,
    },
    "asteroid_field": {
        "label": "Asteroid Field", "weight": 2,
        "asteroids": (30, 55), "harvestable": True, "extra_enemies": 0,
        "nebula": None, "clusters": 0,
        "anomaly_chance": 0.0, "anomaly_quality": 0,
    },
    "dense_field": {
        "label": "Dense Asteroid Field", "weight": 1,
        "asteroids": (40, 65), "harvestable": True, "extra_enemies": 0,
        "nebula": None, "clusters": 0,
        "anomaly_chance": 0.0, "anomaly_quality": 0,
    },
    "green_nebula": {
        "label": "Green Nebula", "weight": 2,
        "asteroids": (4, 10), "harvestable": True, "extra_enemies": 0,
        "nebula": "green", "clusters": 3,
        "anomaly_chance": 0.4, "anomaly_quality": 1,
    },
    "red_nebula": {
        "label": "Red Nebula", "weight": 1,
        "asteroids": (4, 10), "harvestable": True, "extra_enemies": 0,
        "nebula": "red", "clusters": 3,
        "anomaly_chance": 0.7, "anomaly_quality": 2,
    },
    "purple_nebula": {
        "label": "Purple Nebula", "weight": 1,
        "asteroids": (3, 8), "harvestable": True, "extra_enemies": 0,
        "nebula": "purple", "clusters": 3,
        "anomaly_chance": 1.0, "anomaly_quality": 3,
    },
    "mixed_hazard": {
        "label": "Hazard Zone", "weight": 1,
        "asteroids": (10, 20), "harvestable": True, "extra_enemies": 0,
        "nebula": "mixed", "clusters": 3,
        "anomaly_chance": 0.6, "anomaly_quality": 2,
    },
    "ion_storm": {
        "label": "Ion Storm", "weight": 1,
        "asteroids": (3, 8), "harvestable": True, "extra_enemies": 0,
        "nebula": "ion", "clusters": 3,
        "anomaly_chance": 0.5, "anomaly_quality": 2,
    },
    "plasma_field": {
        "label": "Plasma Field", "weight": 1,
        "asteroids": (3, 8), "harvestable": True, "extra_enemies": 0,
        "nebula": "plasma", "clusters": 3,
        "anomaly_chance": 0.6, "anomaly_quality": 2,
    },
    "gravity_rift": {
        "label": "Gravity Rift", "weight": 1,
        "asteroids": (5, 12), "harvestable": True, "extra_enemies": 0,
        "nebula": "gravity", "clusters": 2,
        "anomaly_chance": 0.8, "anomaly_quality": 3,
    },
    "static_cloud": {
        "label": "Static Cloud", "weight": 1,
        "asteroids": (4, 10), "harvestable": True, "extra_enemies": 0,
        "nebula": "static", "clusters": 4,
        "anomaly_chance": 0.4, "anomaly_quality": 1,
    },
    "tachyon_stream": {
        "label": "Tachyon Stream", "weight": 1,
        "asteroids": (3, 8), "harvestable": True, "extra_enemies": 0,
        "nebula": "tachyon", "clusters": 3,
        "anomaly_chance": 0.5, "anomaly_quality": 2,
    },
    # --- Zones inspired by the Space Race track segments ---
    "solar_flare": {
        "label": "Solar Flare Corridor", "weight": 1,
        "asteroids": (3, 8), "harvestable": True, "extra_enemies": 0,
        "nebula": None, "clusters": 0,
        "anomaly_chance": 0.2, "anomaly_quality": 1,
        "zone_effect": "solar_flare",
    },
    "comet_tail": {
        "label": "Comet Tail", "weight": 1,
        "asteroids": (6, 12), "harvestable": True, "extra_enemies": 0,
        "nebula": "comet", "clusters": 4,
        "anomaly_chance": 0.3, "anomaly_quality": 1,
    },
    "debris_ring": {
        "label": "Shattered Moon Debris Ring", "weight": 1,
        "asteroids": (15, 30), "harvestable": True, "extra_enemies": 0,
        "nebula": None, "clusters": 0,
        "anomaly_chance": 0.2, "anomaly_quality": 1,
        "wrecks": (2, 4),
    },
    "warship_graveyard": {
        "label": "Derelict Warship Graveyard", "weight": 1,
        "asteroids": (4, 8), "harvestable": True, "extra_enemies": 0,
        "nebula": None, "clusters": 0,
        "anomaly_chance": 0.5, "anomaly_quality": 2,
        "wrecks": (4, 7),
    },
    "everbright": {
        "label": "Everbright Nebula", "weight": 1,
        "asteroids": (3, 8), "harvestable": True, "extra_enemies": 0,
        "nebula": "everbright", "clusters": 3,
        "anomaly_chance": 0.4, "anomaly_quality": 2,
    },
    "black_hole": {
        "label": "Micro Black Hole", "weight": 1,
        "asteroids": (5, 10), "harvestable": True, "extra_enemies": 0,
        "nebula": "blackhole", "clusters": 1, "cluster_radius": 0,
        "anomaly_chance": 0.9, "anomaly_quality": 3,
    },
    "turret_zone": {
        "label": "Automated Defense Zone", "weight": 1,
        "asteroids": (5, 10), "harvestable": True, "extra_enemies": 0,
        "nebula": None, "clusters": 0,
        "anomaly_chance": 0.3, "anomaly_quality": 2,
        "turrets": (1, 2),
    },
    "slipstream": {
        "label": "Slipstream Corridor", "weight": 1,
        "asteroids": (2, 6), "harvestable": True, "extra_enemies": 0,
        "nebula": "slipstream", "clusters": 4,
        "anomaly_chance": 0.3, "anomaly_quality": 1,
    },
}


def pick_environment():
    keys = list(ENVIRONMENTS)
    weights = [ENVIRONMENTS[k]["weight"] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]


# Region sizes in base-map units (height x length). The standard
# board is 2x2; boss arenas may also be a tight 1x1.
REGION_SIZES = ["1x2", "1x3", "2x2", "2x3"]
BOSS_REGION_SIZES = REGION_SIZES + ["1x1"]


def generate_battle_config(tier, node_type=NodeType.BATTLE, races=None,
                           environment=None):
    if races:
        races = [r for r in races if r != "sentry"]
    else:
        races = list(BASE_RACES)
    ranks = TIER_RANKS.get(tier, TIER_RANKS[1])

    if node_type == NodeType.BOSS:
        map_size = random.choice(BOSS_REGION_SIZES)
    else:
        map_size = random.choice(REGION_SIZES)

    if environment is None:
        environment = pick_environment()
    env_data = ENVIRONMENTS.get(environment, ENVIRONMENTS["clear"])

    from spacewar.roguelike.factions import (
        pick_region_factions, random_faction_race, BOSS_FACTIONS,
    )
    has_anomalies = env_data.get("anomaly_chance", 0) > 0

    boss_mode = None
    boss_faction = None
    factions = []
    if node_type == NodeType.BOSS:
        # Bosses can be unique, or styled after any faction. A lone-wolf
        # pirate boss trusts nobody, so it always duels alone.
        boss_faction = random.choice(BOSS_FACTIONS)
        if boss_faction == "pirates_lone":
            boss_mode = "duel"
        else:
            # Either a lone boss at twice the player's power, or a
            # teamed pair matching the player's power level.
            boss_mode = random.choice(["duel", "pair"])
        if boss_faction == "unique":
            boss_race = random.choice(races)
            faction_tag = None
        else:
            # Faction ships keep their signature sprite even when it
            # comes from another theme's asset pool.
            boss_race = random_faction_race(boss_faction) or \
                random.choice(races)
            faction_tag = boss_faction
            factions = [boss_faction]
        if boss_mode == "duel":
            enemies = [(BOSS_RANKS[tier], boss_race, faction_tag)]
        else:
            pair_rank = ranks[-1] if ranks else RANKS[0]
            enemies = [(pair_rank, boss_race, faction_tag),
                       (pair_rank, boss_race, faction_tag)]
    else:
        factions = pick_region_factions(env_data, has_anomalies)
        hostile = [f for f in factions if f != "colonial"]
        count = random.randint(*TIER_ENEMY_COUNTS[tier])
        count += env_data.get("extra_enemies", 0)
        if node_type == NodeType.ELITE:
            pick_ranks = ranks[-1:] if ranks else [RANKS[0]]
        else:
            pick_ranks = ranks
        enemies = []
        for _ in range(count):
            faction = random.choice(hostile) if hostile else None
            race = random_faction_race(faction) if faction else None
            if race is None:
                race = random.choice(races)
            enemies.append((random.choice(pick_ranks), race, faction))

    return {
        "enemies": enemies,
        "environment": environment,
        "tier": tier,
        "is_boss": node_type == NodeType.BOSS,
        "boss_mode": boss_mode,
        "boss_faction": boss_faction,
        "factions": factions,
        "colonial": "colonial" in factions,
        "map_size": map_size,
    }


def generate_shop_inventory(tier):
    from spacewar.components.base import ComponentSlot
    from spacewar.roguelike.loot import _random_component
    items = []
    for _ in range(3 + tier):
        comp = _random_component(tier)
        if comp:
            if comp.slot == ComponentSlot.POWER_SOURCE:
                # Reactors cost no power; price by output instead.
                price = comp.get("power_provided", 24) * 3 + tier * 20
            else:
                price = (comp.power_cost * 15 + tier * 20)
            items.append({"component": comp, "price": price})

    items.append({"type": "material", "material": "common", "amount": 3, "price": 30})
    items.append({"type": "material", "material": "uncommon", "amount": 2, "price": 60 * tier})
    if tier >= 2:
        items.append({"type": "material", "material": "rare", "amount": 1, "price": 150 * tier})
    items.append({"type": "repair", "price": 20 * tier})

    return items


def generate_event(tier):
    events = [
        {
            "text": "You find a damaged satellite broadcasting an old signal.",
            "choices": [
                ("Salvage it", "salvage", {"scrap": 30 * tier, "materials": {"common": 2}}),
                ("Leave it", "nothing", {}),
            ],
        },
        {
            "text": "A merchant hails you offering a trade.",
            "choices": [
                ("Trade 50 scrap for materials",
                 "trade", {"cost_scrap": 50, "materials": {"uncommon": 1 + tier // 2}}),
                ("Decline", "nothing", {}),
            ],
        },
        {
            "text": "You detect a faint energy signature from a nearby wreck.",
            "choices": [
                ("Investigate (risky)", "risk",
                 {"good": {"scrap": 60 * tier, "materials": {"rare": 1}},
                  "bad": {"hull_damage": 15 * tier},
                  "chance": 0.6}),
                ("Move on", "nothing", {}),
            ],
        },
        {
            "text": "An allied ship offers field repairs in exchange for scrap.",
            "choices": [
                (f"Pay {40 * tier} scrap for repairs",
                 "repair", {"cost_scrap": 40 * tier, "heal_hull": 20, "heal_shields": 30}),
                ("Decline", "nothing", {}),
            ],
        },
    ]
    return random.choice(events)
