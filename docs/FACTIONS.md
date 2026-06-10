# Faction Guide

Reference for everything faction-related in the roguelike mode. Code
lives in `spacewar/roguelike/factions.py`; behavior is enforced in
`spacewar/systems/ai.py` (movement, targeting, leashes),
`spacewar/systems/turn_resolution.py` (mining, provocation), and
`spacewar/states/roguelike_states.py` (spawning).

## Design rules

- A region hosts **at most 2 factions**, picked by
  `pick_region_factions()` when the battle config is generated.
- Only **one pirate sub-faction** ever appears in a region.
- Ships of the same faction are **allied** - except lone-wolf pirates,
  who are allied with nobody, not even each other (`are_allied()`).
- Different factions fight **each other**, not just the player.
- Every faction flies a **unique signature ship** borrowed from the
  dormant theme asset pools (babylon5, sbiti), so the player can read
  a contact's faction at a glance. Classic races stay reserved for the
  player and "unique" bosses.
- Faction ships keep their race's loadout from
  `RACE_COMPONENT_OVERRIDES`, so the weapon set is part of the
  faction's identity.
- Sprites are loaded on demand via
  `ThemeLoader.ensure_race_loaded(race)` - factions work regardless of
  which theme is active.

## The factions

| Faction key    | Label                 | Ship (theme)       | Weapons                    | Beam color        | Temperament |
|----------------|-----------------------|--------------------|----------------------------|-------------------|-------------|
| `pirates_band` | Crimson Pact          | narn (babylon5)    | Torpedoes + HE torpedo     | Crimson (220,50,50) | Cooperative pirates. Reckless flying, no retreat, ignore hazards. |
| `pirates_lone` | Free Raiders          | psiloth (sbiti)    | Disruptors + torpedoes, cloak | Orange (255,160,0) | Lone wolves: allied with nobody; a region has them **or** the Pact, never both. Reckless. |
| `vethari`      | Vethari Conclave      | shadow (babylon5)  | Disruptors + shockwave, cloak + teleport + regen | Native pulsing magenta | Anomaly guardians. Idle ships orbit unlooted anomalies; avoid damaging space unless in combat. |
| `korthax`      | Korthax Swarm         | zlorg (sbiti)      | Shockwave + HE torpedo, fast engines | Native rainbow | Anomaly guardians; close-range swarmers. Avoid damaging space unless in combat. |
| `colonial`     | Colonial Mining Guild | terran (sbiti)     | Lazers + point lazers, ablative shields | Sky blue (80,170,255) | **Neutral.** Mines asteroids; trades; fights only when provoked. Avoids hazards and mines always, and routes around the player's hex. |

## Faction selection per region

- Pirates weight 4; each alien faction weight 1, raised to 4 in
  regions with anomalies (`anomaly_chance > 0`).
- 50% chance of a second faction; the second pick can be the Colonial
  Guild **only in minable regions** (harvestable terrain with
  asteroids).
- Open space ("clear") is never minable, so no colonials there.

## Colonial Mining Guild specifics

- Spawns as a **Mining Barge** (`ship.is_miner = True`, slow Barge
  Drive, reinforced hull, no aggression) plus one **Guild Defender**
  escort. Neither counts against the 6-spawn combat cap.
- The barge crawls 1 hex/turn toward the nearest resource asteroid and
  strips it at end of turn into `ship.cargo`
  (`TurnResolver._process_miners`).
- **Trading:** click the barge while within 1 hex to buy its cargo at
  fair market prices (common 10, uncommon 30 x tier, rare 150 x tier
  scrap) - no turn cost.
- **Destruction:** the barge's cargo spills into its wreck; salvage
  the wreck with a tractor beam to take everything it mined.
- **Provocation:** shooting any colonial flips the whole guild hostile
  at end of turn (`neutral` + `shot_recently` -> faction-wide
  `hostile`/`aggro`).
- The defender stays leashed within **10 hexes** of its barge unless
  another defender is already within that range
  (`DEFENDER_LEASH` in `ai.py`).

## Bosses

- `generate_battle_config(NodeType.BOSS)` rolls a `boss_faction` from
  `BOSS_FACTIONS = ("unique", pirates..., aliens...)`.
- "unique" bosses are factionless and use a classic race.
- A **lone-wolf pirate boss always fights 1v1** (duel mode, 2x player
  power); other factions roll duel (1v1 at 2x) or pair (2v1 teamed at
  1x player power).

## Beam colors

- Color priority when firing energy weapons:
  1. the weapon component's `phaser_color` stat (player-tunable),
  2. `ship.phaser_color` (set by `apply_faction`),
  3. the race's theme data (`.ship` file, may be a per-tick list).
- Players retune beam colors from the roguelike **Ship menu** ("W1/W2
  Beam Color") for lazers, point lazers, and disruptors
  (`BEAM_COLORS` in `roguelike_states.py`).

## Adding a faction

1. Add an entry to `FACTIONS` with a unique race that has a sprite
   (`data/themes/*/<race>.ship`) and a loadout in
   `RACE_COMPONENT_OVERRIDES`.
2. Decide flags: `cooperative`, `reckless`, `avoid_hazards`,
   `protect_anomalies`, `neutral`, `phaser_color`.
3. If it should appear in regions, wire it into
   `pick_region_factions()`; if boss-eligible, add it to
   `BOSS_FACTIONS`.
4. `tests/test_factions.py` enforces sprite uniqueness, loadout
   presence, and on-disk assets.
