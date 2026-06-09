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

TIER_RACES = {
    1: ["federation", "klingon", "tholian", "dominion", "borg"],
    2: ["earth", "minbari", "narn", "centauri", "shadow"],
    3: ["terran", "psiloth", "zlorg", "wental", "riftbound"],
}

ENVIRONMENTS = {
    "clear": {"asteroids": (0, 2), "nebula_red": 0, "nebula_green": 0, "nebula_purple": 0},
    "asteroid_field": {"asteroids": (6, 12), "nebula_red": 0, "nebula_green": 0, "nebula_purple": 0},
    "red_nebula": {"asteroids": (1, 4), "nebula_red": 2, "nebula_green": 0, "nebula_purple": 0},
    "green_nebula": {"asteroids": (1, 3), "nebula_red": 0, "nebula_green": 2, "nebula_purple": 0},
    "purple_nebula": {"asteroids": (0, 2), "nebula_red": 0, "nebula_green": 0, "nebula_purple": 2},
    "mixed_hazard": {"asteroids": (3, 6), "nebula_red": 1, "nebula_green": 1, "nebula_purple": 1},
    "dense_field": {"asteroids": (8, 15), "nebula_red": 1, "nebula_green": 0, "nebula_purple": 1},
}


def generate_battle_config(tier, node_type=NodeType.BATTLE):
    races = TIER_RACES.get(tier, TIER_RACES[1])
    ranks = TIER_RANKS.get(tier, TIER_RANKS[1])

    if node_type == NodeType.BOSS:
        boss_rank = BOSS_RANKS[tier]
        boss_race = random.choice(races)
        enemies = [(boss_rank, boss_race)]
        if tier >= 2:
            enemies.append((random.choice(ranks), random.choice(races)))
        if tier == 3:
            enemies.append((random.choice(ranks), random.choice(races)))
        env = "mixed_hazard" if tier >= 2 else "clear"
    elif node_type == NodeType.ELITE:
        count = random.randint(*TIER_ENEMY_COUNTS[tier])
        elite_ranks = ranks[-1:] if ranks else [RANKS[0]]
        enemies = [(random.choice(elite_ranks), random.choice(races))
                    for _ in range(count)]
        env = random.choice(list(ENVIRONMENTS.keys()))
    else:
        count = random.randint(*TIER_ENEMY_COUNTS[tier])
        enemies = [(random.choice(ranks), random.choice(races))
                    for _ in range(count)]
        env = random.choice(list(ENVIRONMENTS.keys()))

    return {
        "enemies": enemies,
        "environment": env,
        "tier": tier,
        "is_boss": node_type == NodeType.BOSS,
    }


def generate_shop_inventory(tier):
    from spacewar.roguelike.loot import _random_component
    items = []
    for _ in range(3 + tier):
        comp = _random_component(tier)
        if comp:
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
