import random

import pygame

from spacewar.states.state_machine import GameState, StateID
from spacewar.roguelike.encounters import (
    NodeType, NODE_ICONS, generate_battle_config, generate_shop_inventory,
    generate_event, ENVIRONMENTS,
)
from spacewar.roguelike.loot import generate_salvage_loot, apply_loot, format_loot
from spacewar.rendering.hex_grid import HexGrid


class RoguelikeMapState(GameState):
    def enter(self):
        g = self.game
        run = g.active_run
        if not run or not run.alive:
            return

        if run.sector_map.is_tier_complete():
            if not run.advance_tier():
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    f"VICTORY!\n\nYou conquered all 3 tiers!\n"
                    f"Battles: {run.battles_won} | Kills: {run.total_kills}\n"
                    f"Scrap: {run.inventory.scrap}",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
                return

        self._show_map_menu()

    def _show_map_menu(self):
        g = self.game
        run = g.active_run
        available = run.sector_map.get_available_nodes()

        NODE_DESCRIPTIONS = {
            NodeType.REST: "Recover hull and shields",
            NodeType.EVENT: "Unknown signal detected",
        }
        buttons = []
        for node in available:
            icon = NODE_ICONS.get(node.node_type, "?")
            if node.environment:
                # Terrain is the headline; enemies are a given.
                terrain = ENVIRONMENTS.get(
                    node.environment, {}).get("label", "Unknown Space")
                label = f"[{icon}] {terrain}"
                if node.node_type == NodeType.ELITE:
                    label += " - elite hostiles"
                elif node.node_type == NodeType.BOSS:
                    label += " - BOSS"
            else:
                desc = NODE_DESCRIPTIONS.get(node.node_type, "")
                label = f"[{icon}] {node.node_type.value.title()} - {desc}"
            buttons.append((label, _NodeAction(g, node)))

        buttons.append(("--- Ship ---", _ViewShipAction(g)))
        buttons.append(("Inventory", _InventoryAction(g)))
        buttons.append(("Upgrades", _UpgradeMenuAction(g)))
        buttons.append(("Abandon Run", _AbandonAction(g)))

        g.selection_list = g.make_selection_list(
            run.get_status_text(), *buttons)

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP:
            return None
        g = self.game
        if g.message_box:
            g.message_box = None
            if g.active_run and g.active_run.victory:
                g.active_run = None
                from spacewar.menus.main_menu import MainMenu
                g.selection_list = MainMenu(g)()
                return StateID.MAIN_MENU
            if g.active_run and not g.active_run.alive:
                g.active_run = None
                from spacewar.menus.main_menu import MainMenu
                g.selection_list = MainMenu(g)()
                return StateID.MAIN_MENU
            self._show_map_menu()
            return None
        if g.selection_list:
            for button in g.selection_list:
                if button.rect.collidepoint(event.pos):
                    result = button.callback()
                    if result is None and g.selection_list:
                        pass
                    elif isinstance(result, StateID):
                        return result
                    else:
                        g.selection_list = result
                    return None
            return None
        return None

    def update(self):
        return None

    def render(self):
        g = self.game
        g.screen.fill(g.settings.background)
        pygame.transform.scale(g.screen, g.settings.window_size, g.display)
        if g.selection_list:
            g.selection_list.render(g.display)
        if g.message_box:
            g.message_box.render(g.display)


class RoguelikeNodeState(GameState):
    def enter(self):
        pass

    def handle_event(self, event):
        g = self.game
        if event.type != pygame.MOUSEBUTTONUP:
            return None
        if g.message_box:
            g.message_box = None
            return StateID.ROGUELIKE_MAP
        if g.selection_list:
            for button in g.selection_list:
                if button.rect.collidepoint(event.pos):
                    result = button.callback()
                    if isinstance(result, StateID):
                        return result
                    g.selection_list = result
                    return None
        return StateID.ROGUELIKE_MAP

    def update(self):
        return None

    def render(self):
        g = self.game
        g.screen.fill(g.settings.background)
        pygame.transform.scale(g.screen, g.settings.window_size, g.display)
        if g.selection_list:
            g.selection_list.render(g.display)
        if g.message_box:
            g.message_box.render(g.display)


# --- Menu action classes ---

class _MenuActionBase:
    def __init__(self, game):
        self.game = game

    def _make_list(self, title, *buttons):
        return self.game.make_selection_list(title, *buttons)


class _NodeAction(_MenuActionBase):
    def __init__(self, game, node):
        super().__init__(game)
        self.node = node

    def __call__(self):
        g = self.game
        run = g.active_run
        run.sector_map.move_to(self.node)

        if self.node.node_type in (NodeType.BATTLE, NodeType.ELITE, NodeType.BOSS):
            config = generate_battle_config(
                run.current_tier, self.node.node_type,
                races=g.theme_loader.active_races,
                environment=self.node.environment)
            _start_roguelike_battle(g, run, config)
            return StateID.BATTLE_IDLE

        elif self.node.node_type == NodeType.SHOP:
            items = generate_shop_inventory(run.current_tier)
            g.roguelike_shop_items = items
            return _show_shop(g, run, items)

        elif self.node.node_type == NodeType.SALVAGE:
            loot = generate_salvage_loot(run.current_tier)
            apply_loot(loot, run.inventory)
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                f"Salvage!\n\n{format_loot(loot)}",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
            return StateID.ROGUELIKE_MAP

        elif self.node.node_type == NodeType.REST:
            hull_heal, shield_heal = run.rest()
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                f"Rest Stop\n\nHull restored: +{hull_heal}\n"
                f"Shields restored: +{shield_heal}\n\n"
                f"Hull: {run.hull}/{run.max_hull}\n"
                f"Shields: {run.shields}/{run.max_shields}",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
            return StateID.ROGUELIKE_MAP

        elif self.node.node_type == NodeType.EVENT:
            event = generate_event(run.current_tier)
            return _show_event(g, run, event)

        return StateID.ROGUELIKE_MAP


class _ViewShipAction(_MenuActionBase):
    def __call__(self):
        g = self.game
        run = g.active_run
        from spacewar.components.base import ComponentSlot
        from spacewar.systems.weapons import WeaponType, WEAPON_STATS

        lines = [f"=== {run.race.title()} ==="]
        lines.append(f"Hull: {run.hull}/{run.max_hull}  "
                     f"Shields: {run.shields}/{run.max_shields}")
        lines.append(f"Weapon Power: {run.weapon_power}  "
                     f"Power: {run.loadout.total_power_cost()}"
                     f"/{run.loadout.power_budget()}")

        eng = run.loadout.get_component(ComponentSlot.ENGINE)
        if eng:
            lines.append(f"Engine: Spd {eng.get('max_speed',5)} "
                        f"Accel {eng.get('acceleration',2)} "
                        f"Turn {eng.get('turning_degrees',90)}deg")

        sens = run.loadout.get_component(ComponentSlot.SENSORS)
        if sens:
            lines.append(f"Sensors: {sens.get('vision_forward',10)}F "
                        f"/ {sens.get('vision_backward',5)}R")

        for slot_num, slot in [(1, ComponentSlot.WEAPON_1), (2, ComponentSlot.WEAPON_2)]:
            comp = run.loadout.get_component(slot)
            if comp:
                wtype_str = comp.get("weapon_type", "?")
                try:
                    wt = WeaponType(wtype_str)
                    stats = WEAPON_STATS[wt]
                    dmg = stats["damage_per_hit"](run.weapon_power) * stats["hits"]
                    name = stats["display_name"]
                except (ValueError, KeyError):
                    name = wtype_str.replace("_", " ").title()
                    dmg = "?"
                lvl = getattr(comp, 'upgrade_level', 0)
                lvl_str = f"+{lvl}" if lvl > 0 else ""
                lines.append(f"W{slot_num}: {name}{lvl_str} "
                            f"dmg:{dmg} rng:{comp.get('weapon_range',0)}")

        specials = run.loadout.get_specials()
        for i, special in enumerate(specials, 1):
            lines.append(f"Special {i}: {special.name}")

        stealth = run.loadout.get_component(ComponentSlot.STEALTH)
        if stealth:
            # Stealth modules in special bays stack with the plating.
            total_passive = sum(
                c.get("passive_stealth", 0) or 0 for c in run.loadout)
            total_ambush = sum(
                c.get("ambush_bonus", 0) or 0 for c in run.loadout)
            parts = [f"Passive {total_passive}"]
            if stealth.get("active_cloak"):
                parts.append("Cloak ready")
            if total_ambush > 0:
                parts.append(f"Ambush +{total_ambush}%")
            lines.append(f"Stealth: {', '.join(parts)}")

        title = "\n".join(lines)
        buttons = []
        for slot_num, slot in [(1, ComponentSlot.WEAPON_1),
                               (2, ComponentSlot.WEAPON_2)]:
            comp = run.loadout.get_component(slot)
            if comp and comp.get("weapon_type") in BEAM_WEAPON_TYPES:
                current = _beam_color_name(comp.get("phaser_color"))
                buttons.append((f"W{slot_num} Beam Color: {current}",
                                _BeamColorMenu(g, slot)))
        buttons.append(("Back", _BackToMap(g)))
        return self._make_list(title, *buttons)


# Energy weapons whose beam color the player may retune.
BEAM_WEAPON_TYPES = ("lazers", "point_lazers", "disruptors")

BEAM_COLORS = [
    ("Red", (255, 0, 0)),
    ("Crimson", (220, 50, 60)),
    ("Orange", (255, 140, 0)),
    ("Gold", (255, 210, 0)),
    ("Green", (0, 220, 0)),
    ("Cyan", (0, 220, 220)),
    ("Blue", (70, 130, 255)),
    ("Magenta", (255, 0, 255)),
    ("White", (255, 255, 255)),
]


def _beam_color_name(rgb):
    if rgb is None:
        return "Default"
    for name, color in BEAM_COLORS:
        if tuple(color) == tuple(rgb):
            return name
    return "Custom"


class _BeamColorMenu(_MenuActionBase):
    def __init__(self, game, slot):
        super().__init__(game)
        self.slot = slot

    def __call__(self):
        g = self.game
        run = g.active_run
        comp = run.loadout.get_component(self.slot)
        if comp is None:
            return _ViewShipAction(g)()
        buttons = []
        for name, color in BEAM_COLORS:
            buttons.append((name, _SetBeamColor(g, self.slot, color)))
        buttons.append(("Default (race color)",
                        _SetBeamColor(g, self.slot, None)))
        buttons.append(("Back", _ViewShipAction(g)))
        return self._make_list(
            f"Beam color for {comp.name}", *buttons)


class _SetBeamColor(_MenuActionBase):
    def __init__(self, game, slot, color):
        super().__init__(game)
        self.slot = slot
        self.color = color

    def __call__(self):
        g = self.game
        comp = g.active_run.loadout.get_component(self.slot)
        if comp is not None:
            if self.color is None:
                comp.stats.pop("phaser_color", None)
            else:
                comp.stats["phaser_color"] = self.color
        return _ViewShipAction(g)()


class _InventoryAction(_MenuActionBase):
    def __call__(self):
        g = self.game
        run = g.active_run
        inv = run.inventory

        lines = [f"=== Inventory ==="]
        lines.append(f"Scrap: {inv.scrap}")
        mat_parts = [f"{v} {k}" for k, v in inv.materials.items() if v > 0]
        if mat_parts:
            lines.append(" | ".join(mat_parts))
        else:
            lines.append("No materials")
        lines.append(f"\nStored Parts: {len(inv.components)}")

        slots = {}
        for comp in inv.components:
            slot_name = comp.slot.value.replace("_", " ").title()
            if slot_name not in slots:
                slots[slot_name] = []
            slots[slot_name].append(comp.name)
        for slot_name, names in slots.items():
            lines.append(f"  {slot_name}: {', '.join(names)}")

        title = "\n".join(lines)
        buttons = []
        if inv.components:
            buttons.append(("Equip Component", _EquipMenuAction(g)))
        buttons.append(("Back", _BackToMap(g)))
        return self._make_list(title, *buttons)


class _EquipMenuAction(_MenuActionBase):
    def __call__(self):
        g = self.game
        run = g.active_run
        buttons = []
        for comp in run.inventory.components:
            slot_name = comp.slot.value.replace("_", " ").title()
            current = run.loadout.get_component(comp.slot)
            current_name = current.name if current else "Empty"
            label = f"{comp.name} [{slot_name}] (replaces: {current_name})"
            if not run.loadout.can_equip(comp):
                label += " [no power]"
            buttons.append((label, _EquipAction(g, comp)))
        buttons.append(("Back", _InventoryAction(g)))
        header = (f"Equip Component\nPower: {run.loadout.total_power_cost()}"
                  f"/{run.loadout.power_budget()}")
        return self._make_list(header, *buttons)


class _EquipAction(_MenuActionBase):
    def __init__(self, game, component):
        super().__init__(game)
        self.component = component

    def __call__(self):
        g = self.game
        run = g.active_run
        from spacewar.ui.messagebox import Messagebox
        if run.equip_component(self.component):
            g.message_box = Messagebox(
                f"Equipped: {self.component.name}",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        else:
            g.message_box = Messagebox(
                f"Not enough power for {self.component.name}!\n"
                f"Power: {run.loadout.total_power_cost()}"
                f"/{run.loadout.power_budget()}\n"
                f"Upgrade your power source to increase the budget.",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        return _EquipMenuAction(g)()


class _UpgradeMenuAction(_MenuActionBase):
    def __call__(self):
        g = self.game
        run = g.active_run
        from spacewar.roguelike.upgrades import (
            get_upgrade_level, can_upgrade, get_upgrade_cost_text,
            COMPONENT_STAT_STEPS, MAX_UPGRADE_LEVEL, _stat_allowed,
        )
        from spacewar.menus.component_menu import SLOT_ORDER, SLOT_LABELS

        inv = run.inventory
        mat_str = " | ".join(f"{v} {k}" for k, v in inv.materials.items() if v > 0)
        header = f"=== Upgrades ===\nScrap: {inv.scrap}"
        if mat_str:
            header += f"\n{mat_str}"

        buttons = []
        for slot in SLOT_ORDER:
            comp = run.loadout.get_component(slot)
            steps = COMPONENT_STAT_STEPS.get(slot)
            if not comp or not steps:
                continue
            # Fixed gear (teleporters, phasing, empty bays) has no
            # upgradeable stats; don't list it.
            if not any(_stat_allowed(comp, stat) for stat in steps):
                continue
            lvl = get_upgrade_level(comp)
            label = SLOT_LABELS.get(slot, slot.value)
            if lvl >= MAX_UPGRADE_LEVEL:
                buttons.append((f"{label}: {comp.name} [MAX]", _UpgradeMenuAction(g)))
            else:
                cost = get_upgrade_cost_text(comp)
                upgradeable = can_upgrade(comp, run.inventory)
                if upgradeable:
                    label_text = (f"{label}: {comp.name} -> Lv{lvl+1} "
                                  f"(+1 stat) [{cost}]")
                else:
                    label_text = f"{label}: {comp.name} Lv{lvl} (need: {cost})"
                buttons.append((
                    label_text,
                    _DoUpgrade(g, comp) if upgradeable else _UpgradeMenuAction(g),
                ))

        buttons.append(("Back", _BackToMap(g)))
        return self._make_list(header, *buttons)


class _DoUpgrade(_MenuActionBase):
    def __init__(self, game, component):
        super().__init__(game)
        self.component = component

    def __call__(self):
        g = self.game
        run = g.active_run
        from spacewar.roguelike.upgrades import upgrade_component
        if upgrade_component(self.component, run.inventory):
            run._refresh_max_stats()
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                f"Upgraded: {self.component.name}",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        return _UpgradeMenuAction(g)()


class _AbandonAction(_MenuActionBase):
    def __call__(self):
        g = self.game
        return self._make_list(
            "Abandon this run?",
            ("Yes, abandon", _ConfirmAbandon(g)),
            ("No, continue", _BackToMap(g)),
        )


class _ConfirmAbandon(_MenuActionBase):
    def __call__(self):
        g = self.game
        g.active_run = None
        from spacewar.menus.main_menu import MainMenu
        g.selection_list = MainMenu(g)()
        return StateID.MAIN_MENU


class _BackToMap(_MenuActionBase):
    def __call__(self):
        g = self.game
        g.state_machine.transition_to(StateID.ROGUELIKE_MAP)
        return None


# --- Helper functions ---

def _build_rank_stats(rank):
    from spacewar.config.constants import RANKS, STATS
    points = RANKS.index(rank) * 5 if rank in RANKS else 0
    stats = {s: d["min"] for s, d in STATS.items()}
    while points > 0:
        available = [s for s, d in STATS.items() if stats[s] < d["max"]]
        if not available:
            break
        upgrade = random.choice(available)
        stats[upgrade] += STATS[upgrade]["step"]
        points -= 1
    return stats


def _spawn_roguelike_enemy(game, b, spec, pos, index=0, aggro=False):
    """Spawn one AI ship from a (rank, race[, faction]) spec."""
    from spacewar.entities.ship import Ship
    from spacewar.systems.scoring import ScoringSystem
    from spacewar.components.race_configs import build_race_loadout

    rank, race = spec[0], spec[1]
    faction = spec[2] if len(spec) > 2 else None
    if not game.theme_loader.ensure_race_loaded(race):
        race = random.choice(game.theme_loader.active_races)
    stats = _build_rank_stats(rank)
    e_loadout = build_race_loadout(race)
    enemy = Ship(
        race, HexGrid.hex_to_coords(*pos), 0,
        rank, f"Enemy {index + 1}", f"Ship {index + 1}",
        stats["shields"], stats["weapon power"],
        stats["engine"], loadout=e_loadout,
        pixel_perfect=game.settings.pixel_perfect,
    )
    enemy.aggro = aggro
    if faction:
        from spacewar.roguelike.factions import apply_faction
        apply_faction(enemy, faction)
    enemy.rotate(0, game.theme_loader.ships)
    b.ships.append(enemy)
    b.match_stats[enemy] = ScoringSystem.init_ai_stats()
    b.total_combat_spawns = getattr(b, 'total_combat_spawns', 0) + 1
    return enemy


def _random_edge_hex(b):
    from spacewar.config import constants
    from spacewar.config.constants import max_col
    occupied = {HexGrid.coords_to_hex(s.pos) for s in b.ships}
    for _ in range(30):
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            row, col = 1, random.randint(1, max_col(1))
        elif edge == "bottom":
            row = constants.GRID_ROWS
            col = random.randint(1, max_col(row))
        elif edge == "left":
            row, col = random.randint(1, constants.GRID_ROWS), 1
        else:
            row = random.randint(1, constants.GRID_ROWS)
            col = max_col(row)
        if (row, col) not in occupied:
            return row, col
    return 1, 1


def _free_hex_near(b, anchor, occupied, max_radius=4):
    from spacewar.config import constants
    from spacewar.config.constants import max_col
    for radius in range(1, max_radius + 1):
        candidates = []
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r, c = anchor[0] + dr, anchor[1] + dc
                if r < 1 or r > constants.GRID_ROWS or \
                        c < 1 or c > max_col(r):
                    continue
                if (r, c) in occupied:
                    continue
                if HexGrid.hex_distance(anchor, (r, c)) == radius:
                    candidates.append((r, c))
        if candidates:
            return random.choice(candidates)
    return None


def _spawn_colonials(game, b, occupied):
    """A colonial mining barge plus one escort, parked near the ore."""
    from spacewar.entities.ship import Ship
    from spacewar.systems.scoring import ScoringSystem
    from spacewar.components.base import Component, ComponentSlot
    from spacewar.components.race_configs import build_race_loadout
    from spacewar.roguelike.factions import apply_faction, FACTIONS

    resource_asts = [a for a in b.asteroids if a.resource]
    if not resource_asts:
        return
    race = FACTIONS["colonial"]["races"][0]
    if not game.theme_loader.ensure_race_loaded(race):
        race = game.theme_loader.active_races[0]
    anchor = random.choice(resource_asts).hex_pos

    miner_hex = _free_hex_near(b, anchor, occupied)
    if miner_hex is None:
        return
    occupied.add(miner_hex)
    miner_loadout = build_race_loadout(race)
    miner_loadout.equip(Component(
        ComponentSlot.ENGINE, "Barge Drive", 2,
        max_speed=1, acceleration=1, turning_degrees=90,
        maneuvering_points=1))
    miner_loadout.equip(Component(
        ComponentSlot.HULL, "Reinforced Cargo Hull", 2,
        strength=120, collision_damage=25))
    miner = Ship(
        race, HexGrid.hex_to_coords(*miner_hex), 0,
        'cadet', "Guild Foreman", "Mining Barge",
        150, 5, 1, loadout=miner_loadout,
        pixel_perfect=game.settings.pixel_perfect,
    )
    miner.is_miner = True
    miner.cargo = {"scrap": 0, "materials": {}}
    miner.aggro = False
    apply_faction(miner, "colonial")
    miner.rotate(0, game.theme_loader.ships)
    b.ships.append(miner)
    b.match_stats[miner] = ScoringSystem.init_ai_stats()

    defender_hex = _free_hex_near(b, miner_hex, occupied)
    if defender_hex is None:
        return
    occupied.add(defender_hex)
    stats = _build_rank_stats("lieutenant")
    defender = Ship(
        race, HexGrid.hex_to_coords(*defender_hex), 0,
        'lieutenant', "Guild Escort", "Guild Defender",
        stats["shields"], stats["weapon power"],
        stats["engine"], loadout=build_race_loadout(race),
        pixel_perfect=game.settings.pixel_perfect,
    )
    defender.aggro = False
    defender.guard_target = miner
    apply_faction(defender, "colonial")
    defender.rotate(0, game.theme_loader.ships)
    b.ships.append(defender)
    b.match_stats[defender] = ScoringSystem.init_ai_stats()


def maybe_spawn_reinforcement(game):
    """Zones stay alive: while fewer than 3 hostiles roam the map,
    every 3-7 turns there is a 33% chance another foe warps in at a
    random edge."""
    b = game.battle
    config = game.roguelike_battle_config or {}
    if not b or game.active_run is None or config.get("is_boss"):
        return
    turn = getattr(b, 'turn_count', 0)
    nxt = getattr(b, 'next_spawn_turn', None)
    if nxt is None or turn < nxt:
        return
    b.next_spawn_turn = turn + random.randint(3, 7)

    # Hard cap: no zone produces more than 6 combat enemies in total
    # (mining ships and shops are exempt and never spawn here anyway).
    if getattr(b, 'total_combat_spawns', 0) >= 6:
        return

    alive = [s for s in b.ships
             if s != b.player and not s.is_dead()
             and not getattr(s, 'is_shop', False)
             and not getattr(s, 'is_miner', False)
             and not getattr(s, 'is_turret', False)]
    if len(alive) >= 3 or random.random() >= 0.33:
        return

    pending = getattr(b, 'pending_enemies', None)
    if pending:
        spec = pending.pop()
    else:
        from spacewar.roguelike.encounters import TIER_RANKS, BASE_RACES
        from spacewar.roguelike.factions import random_faction_race
        ranks = TIER_RANKS.get(b.tier, TIER_RANKS[1])
        hostile = [f for f in config.get("factions", ()) if f != "colonial"]
        faction = random.choice(hostile) if hostile else None
        race = random_faction_race(faction) if faction else None
        if race is None:
            races = [e[1] for e in config.get("enemies", ())] or \
                list(BASE_RACES)
            race = random.choice(races)
        spec = (random.choice(ranks), race, faction)
    pos = _random_edge_hex(b)
    _spawn_roguelike_enemy(game, b, spec, pos,
                           index=len(b.ships), aggro=False)


def _start_roguelike_battle(game, run, config):
    import random
    from spacewar.entities.ship import Ship
    from spacewar.systems.scoring import ScoringSystem
    from spacewar.systems.harvest import roll_asteroid_resource
    from spacewar.ui.command_box import CommandBox
    from spacewar.components.base import Component, ComponentSlot
    from spacewar.components.race_configs import build_race_loadout
    from spacewar.config import constants
    from spacewar.config.constants import RANKS, STATS, max_col
    from spacewar.entities.map_object import Asteroid, NebulaTile, Anomaly
    from spacewar.roguelike.encounters import generate_shop_inventory

    game.init_battle(config.get("map_size", "2x2"))
    b = game.battle
    b.tier = config.get("tier", run.current_tier)

    player = Ship(
        run.race, HexGrid.hex_to_coords(3, 3), 180,
        'cadet', 'Player', 'Ship',
        run.shields, run.weapon_power, 5,
        loadout=run.loadout, human=True,
        pixel_perfect=game.settings.pixel_perfect,
    )
    player.hull = run.hull
    player.rotate(180, game.theme_loader.ships)
    b.player = player
    b.home_player = player
    b.ships.append(player)
    b.match_stats[player] = ScoringSystem.init_player_stats(
        player, game.theme_loader.active_races, game.theme_loader.has_sentry())

    game.command_box = CommandBox(
        game.display, game.infofont,
        game.settings.foreground, game.settings.background, game.text_manager)

    positions = [
        (constants.GRID_ROWS - 2, constants.GRID_COLS_EVEN - 2),
        (2, constants.GRID_COLS_ODD - 2),
        (constants.GRID_ROWS - 2, 2),
        (constants.GRID_ROWS // 2, constants.GRID_COLS_EVEN - 2),
    ]

    if config.get("is_boss"):
        # Boss fights are player-relative: a lone boss at twice the
        # player's power, or a teamed pair at the player's power level.
        boss_mode = config.get("boss_mode") or "duel"
        mult = 2 if boss_mode == "duel" else 1
        for i, spec in enumerate(config["enemies"]):
            rank, race = spec[0], spec[1]
            faction = spec[2] if len(spec) > 2 else None
            if not game.theme_loader.ensure_race_loaded(race):
                race = random.choice(game.theme_loader.active_races)
            e_loadout = build_race_loadout(race)
            shields_comp = e_loadout.get_component(ComponentSlot.SHIELDS)
            hull_comp = e_loadout.get_component(ComponentSlot.HULL)
            if shields_comp:
                shields_comp.stats["strength"] = run.max_shields * mult
            if hull_comp:
                hull_comp.stats["strength"] = run.max_hull * mult
            pos = positions[i % len(positions)]
            enemy = Ship(
                race, HexGrid.hex_to_coords(*pos), 0,
                rank, f"Boss {i+1}" if mult == 2 else f"Enemy {i+1}",
                f"Ship {i+1}",
                run.max_shields * mult, run.weapon_power * mult,
                5, loadout=e_loadout,
                pixel_perfect=game.settings.pixel_perfect,
            )
            if faction:
                from spacewar.roguelike.factions import apply_faction
                apply_faction(enemy, faction)
                enemy.neutral = False
                enemy.hostile = True
            enemy.rotate(0, game.theme_loader.ships)
            b.ships.append(enemy)
            b.match_stats[enemy] = ScoringSystem.init_ai_stats()
        if boss_mode == "pair":
            b.team_game = True
    else:
        # Most foes are out there somewhere, not waiting at the gate:
        # 85% of zones start with 1-2 enemies on the map; the rest warp
        # in over time (see maybe_spawn_reinforcement).
        specs = list(config["enemies"])
        random.shuffle(specs)
        initial = []
        if specs and random.random() < 0.85:
            for _ in range(min(len(specs), random.randint(1, 2))):
                initial.append(specs.pop())
        b.pending_enemies = specs
        b.next_spawn_turn = random.randint(3, 7)
        for i, spec in enumerate(initial):
            _spawn_roguelike_enemy(
                game, b, spec, positions[i % len(positions)], index=i)

    env_name = config.get("environment", "clear")
    env = ENVIRONMENTS.get(env_name, ENVIRONMENTS["clear"])
    b.zone_effect = env.get("zone_effect")
    occupied = {HexGrid.coords_to_hex(s.pos) for s in b.ships}
    occupied.discard(None)

    ast_min, ast_max = env.get("asteroids", (0, 0))
    for _ in range(random.randint(ast_min, ast_max)):
        for _ in range(20):
            row = random.randint(3, constants.GRID_ROWS - 2)
            col = random.randint(2, max_col(row) - 1)
            if (row, col) not in occupied:
                b.asteroids.append(Asteroid((row, col)))
                occupied.add((row, col))
                break

    # Harvestable resources: every terrain except open space, capped
    # at 20 spots per map.
    if env.get("harvestable") and b.asteroids:
        candidates = list(b.asteroids)
        random.shuffle(candidates)
        count = min(20, max(1, len(candidates) // 3))
        for ast in candidates[:count]:
            ast.resource = roll_asteroid_resource(b.tier)

    # The Colonial Mining Guild works asteroid-rich regions: a slow
    # mining barge under escort, neutral until provoked.
    if config.get("colonial"):
        _spawn_colonials(game, b, occupied)

    nebula_kind = env.get("nebula")
    for _ in range(env.get("clusters", 0)):
        ntype = nebula_kind
        if nebula_kind == "mixed":
            ntype = random.choice([NebulaTile.RED, NebulaTile.GREEN,
                                   NebulaTile.PURPLE, NebulaTile.ION,
                                   NebulaTile.PLASMA, NebulaTile.GRAVITY,
                                   NebulaTile.STATIC, NebulaTile.TACHYON])
        center_row = random.randint(5, constants.GRID_ROWS - 4)
        center_col = random.randint(3, max_col(center_row) - 2)
        cluster_hexes = []
        radius = env.get("cluster_radius", 1)  # 0 = a single tile
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r, c = center_row + dr, center_col + dc
                if r < 1 or r > constants.GRID_ROWS or c < 1 or c > max_col(r):
                    continue
                if (r, c) in occupied:
                    continue
                neb = NebulaTile((r, c), ntype)
                b.nebulae.append(neb)
                b.nebulae_by_hex[(r, c)] = neb
                occupied.add((r, c))
                cluster_hexes.append((r, c))
        if cluster_hexes and random.random() < env.get("anomaly_chance", 0):
            b.anomalies.append(Anomaly(
                random.choice(cluster_hexes),
                quality=env.get("anomaly_quality", 1)))

    # Debris rings and warship graveyards are littered with derelict
    # hulls ripe for tractor-beam salvage.
    wreck_min, wreck_max = env.get("wrecks", (0, 0))
    if wreck_max:
        from spacewar.entities.wreck import Wreck
        for _ in range(random.randint(wreck_min, wreck_max)):
            for _ in range(20):
                row = random.randint(3, constants.GRID_ROWS - 2)
                col = random.randint(2, max_col(row) - 1)
                if (row, col) not in occupied:
                    b.wrecks.append(Wreck((row, col), "derelict", "cadet"))
                    occupied.add((row, col))
                    break

    # Automated defense zones: ancient turrets that fire on anything
    # their sensors can reach. They never move.
    turret_min, turret_max = env.get("turrets", (0, 0))
    for _ in range(random.randint(turret_min, turret_max) if turret_max else 0):
        for _ in range(30):
            row = random.randint(5, constants.GRID_ROWS - 4)
            col = random.randint(3, max_col(row) - 2)
            if (row, col) in occupied:
                continue
            turret_loadout = build_race_loadout("sentry")
            turret_loadout.equip(Component(
                ComponentSlot.SHIELDS, "Turret Shields", 0,
                strength=150 + 50 * b.tier, passive_regen=10,
                active_regen_mult=1.0, active_dr=0))
            turret = Ship(
                "sentry", HexGrid.hex_to_coords(row, col), 0,
                RANKS[0], "", "Defense Turret",
                150 + 50 * b.tier, 8 + 4 * b.tier, 0,
                loadout=turret_loadout,
                pixel_perfect=game.settings.pixel_perfect,
            )
            turret.is_turret = True
            turret.hostile = True
            turret.rotate(0, game.theme_loader.ships)
            b.ships.append(turret)
            b.match_stats[turret] = ScoringSystem.init_ai_stats()
            occupied.add((row, col))
            break

    # Neutral trading post on roughly a third of maps.
    if random.random() < 0.33:
        for _ in range(30):
            row = random.randint(5, constants.GRID_ROWS - 4)
            col = random.randint(3, max_col(row) - 2)
            if (row, col) in occupied:
                continue
            shop_loadout = build_race_loadout("sentry")
            shop_loadout.equip(Component(
                ComponentSlot.SHIELDS, "Trading Post Shields", 0,
                strength=600, passive_regen=20,
                active_regen_mult=1.0, active_dr=0))
            shop_loadout.equip(Component(
                ComponentSlot.HULL, "Trading Post Hull", 0,
                strength=300, collision_damage=50))
            shop = Ship(
                "sentry", HexGrid.hex_to_coords(row, col), 0,
                RANKS[0], "", "Trading Post",
                600, 25, 0, loadout=shop_loadout,
                pixel_perfect=game.settings.pixel_perfect,
            )
            shop.is_shop = True
            shop.hostile = False
            shop.shop_items = generate_shop_inventory(b.tier)
            shop.rotate(0, game.theme_loader.ships)
            b.ships.append(shop)
            b.match_stats[shop] = ScoringSystem.init_ai_stats()
            occupied.add((row, col))
            break

    game.roguelike_battle_config = config
    game.instant_action = True
    game.selection_list = None
    game.message_box = None


def _show_shop(game, run, items):
    buttons = []
    for i, item in enumerate(items):
        if "component" in item:
            comp = item["component"]
            slot_name = comp.slot.value.replace("_", " ").title()
            affordable = run.inventory.scrap >= item["price"]
            tag = "" if affordable else " [!]"
            label = f"{comp.name} [{slot_name}] - {item['price']}s{tag}"
            buttons.append((label, _BuyComponent(game, i)))
        elif item.get("type") == "material":
            mat = item["material"]
            affordable = run.inventory.scrap >= item["price"]
            tag = "" if affordable else " [!]"
            label = f"{item['amount']}x {mat.title()} - {item['price']}s{tag}"
            buttons.append((label, _BuyMaterial(game, i)))
        elif item.get("type") == "repair":
            needs_repair = run.hull < run.max_hull or run.shields < run.max_shields
            affordable = run.inventory.scrap >= item["price"]
            tag = " [full hp]" if not needs_repair else ("" if affordable else " [!]")
            label = f"Full Repair - {item['price']}s{tag}"
            buttons.append((label, _BuyRepair(game, i)))

    buttons.append(("Leave Shop", _BackToMap(game)))
    game.selection_list = game.make_selection_list(
        f"=== Shop ===\nScrap: {run.inventory.scrap}", *buttons)
    return None


class _BuyComponent(_MenuActionBase):
    def __init__(self, game, index):
        super().__init__(game)
        self.index = index

    def __call__(self):
        g = self.game
        run = g.active_run
        items = g.roguelike_shop_items
        item = items[self.index]
        if run.inventory.spend_scrap(item["price"]):
            run.inventory.add_component(item["component"])
            items.pop(self.index)
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                f"Purchased: {item['component'].name}",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        else:
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                "Not enough scrap!",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        return _show_shop(g, run, items)


class _BuyMaterial(_MenuActionBase):
    def __init__(self, game, index):
        super().__init__(game)
        self.index = index

    def __call__(self):
        g = self.game
        run = g.active_run
        items = g.roguelike_shop_items
        item = items[self.index]
        if run.inventory.spend_scrap(item["price"]):
            run.inventory.add_material(item["material"], item["amount"])
            items.pop(self.index)
        else:
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                "Not enough scrap!",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        return _show_shop(g, run, items)


class _BuyRepair(_MenuActionBase):
    def __init__(self, game, index):
        super().__init__(game)
        self.index = index

    def __call__(self):
        g = self.game
        run = g.active_run
        items = g.roguelike_shop_items
        item = items[self.index]
        if run.inventory.spend_scrap(item["price"]):
            run.apply_repair()
            items.pop(self.index)
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                f"Fully repaired!\nHull: {run.hull}/{run.max_hull}\n"
                f"Shields: {run.shields}/{run.max_shields}",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        else:
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                "Not enough scrap!",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
        return _show_shop(g, run, items)


def _show_event(game, run, event):
    buttons = []
    for choice_text, choice_type, choice_data in event["choices"]:
        buttons.append((choice_text, _EventChoice(game, choice_type, choice_data)))
    game.selection_list = game.make_selection_list(event["text"], *buttons)
    return None


class _EventChoice(_MenuActionBase):
    def __init__(self, game, choice_type, data):
        super().__init__(game)
        self.choice_type = choice_type
        self.data = data

    def __call__(self):
        import random
        g = self.game
        run = g.active_run
        from spacewar.ui.messagebox import Messagebox

        if self.choice_type == "nothing":
            return StateID.ROGUELIKE_MAP

        elif self.choice_type == "salvage":
            run.inventory.add_scrap(self.data.get("scrap", 0))
            for mat, amount in self.data.get("materials", {}).items():
                run.inventory.add_material(mat, amount)
            from spacewar.roguelike.loot import format_loot
            g.message_box = Messagebox(
                f"Salvage collected!\n{format_loot(self.data)}",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
            return StateID.ROGUELIKE_MAP

        elif self.choice_type == "trade":
            cost = self.data.get("cost_scrap", 0)
            if run.inventory.spend_scrap(cost):
                for mat, amount in self.data.get("materials", {}).items():
                    run.inventory.add_material(mat, amount)
                g.message_box = Messagebox(
                    "Trade complete!",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
            else:
                g.message_box = Messagebox(
                    "Not enough scrap!",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
            return StateID.ROGUELIKE_MAP

        elif self.choice_type == "risk":
            chance = self.data.get("chance", 0.5)
            if random.random() < chance:
                good = self.data.get("good", {})
                run.inventory.add_scrap(good.get("scrap", 0))
                for mat, amount in good.get("materials", {}).items():
                    run.inventory.add_material(mat, amount)
                from spacewar.roguelike.loot import format_loot
                loot_text = format_loot({
                    "scrap": good.get("scrap", 0),
                    "materials": good.get("materials", {}),
                    "components": []})
                g.message_box = Messagebox(
                    f"Lucky find!\n{loot_text}",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
            else:
                bad = self.data.get("bad", {})
                dmg = bad.get("hull_damage", 0)
                run.take_hull_damage(dmg)
                if run.alive:
                    text = (f"Trap! Hull damage: {dmg}\n"
                            f"Hull: {run.hull}/{run.max_hull}")
                else:
                    text = (f"Trap! Hull damage: {dmg}\n\n"
                            f"Your ship was destroyed.\n"
                            f"Battles won: {run.battles_won}\n"
                            f"Total kills: {run.total_kills}")
                g.message_box = Messagebox(
                    text, g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
            return StateID.ROGUELIKE_MAP

        elif self.choice_type == "repair":
            cost = self.data.get("cost_scrap", 0)
            if run.inventory.spend_scrap(cost):
                run.heal_partial(
                    self.data.get("heal_hull", 0),
                    self.data.get("heal_shields", 0))
                g.message_box = Messagebox(
                    f"Repairs complete!\nHull: {run.hull}/{run.max_hull}\n"
                    f"Shields: {run.shields}/{run.max_shields}",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
            else:
                g.message_box = Messagebox(
                    "Not enough scrap!",
                    g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
            return StateID.ROGUELIKE_MAP

        return StateID.ROGUELIKE_MAP
