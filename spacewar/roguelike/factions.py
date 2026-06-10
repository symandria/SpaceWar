"""Factions that populate roguelike zones.

Pirates come in two sub-factions - clans that work together and lone
wolves that trust nobody - and a region only ever hosts one of the two.
Two alien factions gravitate toward sensor anomalies and protect them.
The Colonial Mining Guild is neutral: its mining ships slowly work the
asteroid fields under escort, trade their cargo at fair prices, and
only fight back if provoked.

Classic races provide the ship sprites; the faction is gameplay data
layered on top.
"""
import random


# Each faction flies one unique ship type (borrowed from any theme's
# asset pool) so players can identify it on sight, and a weapon set
# matching its temperament. See docs/FACTIONS.md for the full guide.
FACTIONS = {
    "pirates_band": {
        "label": "Crimson Pact",
        # Rust-orange narn raider: torpedo + HE-torpedo barrages,
        # overtuned engines, ablative plating. Brawlers.
        "races": ("narn",),
        "phaser_color": (220, 50, 50),
        "cooperative": True,
        "reckless": True,        # little self-preservation in flight
        "avoid_hazards": False,
        "protect_anomalies": False,
        "neutral": False,
    },
    "pirates_lone": {
        "label": "Free Raiders",
        # Yellow psiloth saucer: cloaking device, disruptors and
        # torpedoes. Solitary ambush hunters.
        "races": ("psiloth",),
        "phaser_color": (255, 160, 0),
        "cooperative": False,    # every raider for themselves
        "reckless": True,
        "avoid_hazards": False,
        "protect_anomalies": False,
        "neutral": False,
    },
    "vethari": {
        "label": "Vethari Conclave",
        # Black shadow spider-ship: cloak, teleport, regenerating
        # shields, disruptors + shockwave. Native magenta beams.
        "races": ("shadow",),
        "phaser_color": None,    # keep the shadow's pulsing magenta
        "cooperative": True,
        "reckless": False,
        "avoid_hazards": True,   # shun damaging space unless fighting
        "protect_anomalies": True,
        "neutral": False,
    },
    "korthax": {
        "label": "Korthax Swarm",
        # Red zlorg swarm-bug: fast, shockwave + HE torpedo, dives in
        # close. Native rainbow beams.
        "races": ("zlorg",),
        "phaser_color": None,
        "cooperative": True,
        "reckless": False,
        "avoid_hazards": True,
        "protect_anomalies": True,
        "neutral": False,
    },
    "colonial": {
        "label": "Colonial Mining Guild",
        # Grey-red terran workhorse: lazers + point lazers behind
        # ablative shields. Defensive escorts, sky-blue beams.
        "races": ("terran",),
        "phaser_color": (80, 170, 255),
        "cooperative": True,
        "reckless": False,
        "avoid_hazards": True,   # always, in and out of combat
        "protect_anomalies": False,
        "neutral": True,
    },
}

PIRATE_SUBFACTIONS = ("pirates_band", "pirates_lone")
ALIEN_FACTIONS = ("vethari", "korthax")
BOSS_FACTIONS = ("unique",) + PIRATE_SUBFACTIONS + ALIEN_FACTIONS


def apply_faction(ship, faction_key):
    data = FACTIONS.get(faction_key)
    if not data:
        return
    ship.faction = faction_key
    ship.faction_coop = data["cooperative"]
    ship.reckless = data["reckless"]
    ship.avoid_hazards = data["avoid_hazards"]
    ship.protect_anomalies = data["protect_anomalies"]
    if data.get("phaser_color"):
        ship.phaser_color = data["phaser_color"]
    if data["neutral"]:
        ship.neutral = True
        ship.hostile = False


def random_faction_race(faction_key):
    data = FACTIONS.get(faction_key)
    if not data:
        return None
    return random.choice(data["races"])


def pick_region_factions(env_data, has_anomalies):
    """Choose the (at most 2) factions present in a region.

    Only one pirate sub-faction exists per region. Aliens are more
    likely where anomalies form. Colonials only settle where there
    are asteroids to mine.
    """
    pirate_sub = random.choice(PIRATE_SUBFACTIONS)
    alien_weight = 4 if has_anomalies else 1
    pool = [pirate_sub] + list(ALIEN_FACTIONS)
    weights = [4, alien_weight, alien_weight]
    primary = random.choices(pool, weights=weights, k=1)[0]
    chosen = [primary]

    minable = (env_data.get("harvestable") and
               env_data.get("asteroids", (0, 0))[1] > 0)
    if random.random() < 0.5:
        secondary_pool = [f for f in pool if f != primary]
        if minable:
            secondary_pool.append("colonial")
        chosen.append(random.choice(secondary_pool))
    return chosen


def are_allied(a, b):
    """Same cooperative faction = allies. Lone-wolf pirates are allied
    with nobody, not even each other."""
    fa = getattr(a, 'faction', None)
    fb = getattr(b, 'faction', None)
    if fa is None or fb is None or fa != fb:
        return False
    return (getattr(a, 'faction_coop', True) and
            getattr(b, 'faction_coop', True))
