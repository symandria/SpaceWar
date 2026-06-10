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
            NodeType.BATTLE: "Combat encounter",
            NodeType.ELITE: "Tough fight, better loot",
            NodeType.SHOP: "Buy parts and repairs",
            NodeType.SALVAGE: "Search wreckage for parts",
            NodeType.REST: "Recover hull and shields",
            NodeType.EVENT: "Unknown signal detected",
            NodeType.BOSS: "BOSS - Tier guardian",
        }
        buttons = []
        for node in available:
            icon = NODE_ICONS.get(node.node_type, "?")
            desc = NODE_DESCRIPTIONS.get(node.node_type, "")
            label = f"[{icon}] {node.node_type.value.title()} - {desc}"
            if node.completed:
                label = f"[{icon}] {node.node_type.value.title()} (done)"
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
                races=g.theme_loader.active_races)
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

        special = run.loadout.get_component(ComponentSlot.SPECIAL)
        if special and special.get("ability_type"):
            lines.append(f"Special: {special.name}")

        stealth = run.loadout.get_component(ComponentSlot.STEALTH)
        if stealth and stealth.get("active_cloak"):
            lines.append("Cloaking: Active")

        title = "\n".join(lines)
        return self._make_list(title, ("Back", _BackToMap(g)))


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
        from spacewar.roguelike.upgrades import get_upgrade_level, can_upgrade, get_upgrade_cost_text, UPGRADE_MULTIPLIERS
        from spacewar.menus.component_menu import SLOT_ORDER, SLOT_LABELS

        inv = run.inventory
        mat_str = " | ".join(f"{v} {k}" for k, v in inv.materials.items() if v > 0)
        header = f"=== Upgrades ===\nScrap: {inv.scrap}"
        if mat_str:
            header += f"\n{mat_str}"

        buttons = []
        for slot in SLOT_ORDER:
            comp = run.loadout.get_component(slot)
            if not comp:
                continue
            lvl = get_upgrade_level(comp)
            label = SLOT_LABELS.get(slot, slot.value)
            if lvl >= 3:
                buttons.append((f"{label}: {comp.name} [MAX]", _UpgradeMenuAction(g)))
            else:
                cost = get_upgrade_cost_text(comp)
                upgradeable = can_upgrade(comp, run.inventory)
                next_mult = UPGRADE_MULTIPLIERS.get(lvl + 1, 1.0)
                preview = f"x{next_mult}"
                if upgradeable:
                    label_text = f"{label}: {comp.name} -> Lv{lvl+1} ({preview}) [{cost}]"
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

def _start_roguelike_battle(game, run, config):
    import random
    from spacewar.entities.ship import Ship
    from spacewar.systems.scoring import ScoringSystem
    from spacewar.ui.command_box import CommandBox
    from spacewar.components.race_configs import build_race_loadout
    from spacewar.config.constants import GRID_ROWS, GRID_COLS_ODD, GRID_COLS_EVEN, RANKS, STATS, max_col
    from spacewar.entities.map_object import Asteroid, NebulaTile

    game.init_battle()
    b = game.battle

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
        (GRID_ROWS - 2, GRID_COLS_EVEN - 2),
        (2, GRID_COLS_ODD - 2),
        (GRID_ROWS - 2, 2),
    ]
    for i, (rank, race) in enumerate(config["enemies"]):
        points = RANKS.index(rank) * 5 if rank in RANKS else 0
        stats = {s: d["min"] for s, d in STATS.items()}
        while points > 0:
            available = [s for s, d in STATS.items() if stats[s] < d["max"]]
            if not available:
                break
            upgrade = random.choice(available)
            stats[upgrade] += STATS[upgrade]["step"]
            points -= 1

        e_loadout = build_race_loadout(race)
        pos = positions[i % len(positions)]
        enemy = Ship(
            race, HexGrid.hex_to_coords(*pos), 0,
            rank, f"Enemy {i+1}", f"Ship {i+1}",
            stats["shields"], stats["weapon power"],
            stats["engine"], loadout=e_loadout,
            pixel_perfect=game.settings.pixel_perfect,
        )
        enemy.rotate(0, game.theme_loader.ships)
        b.ships.append(enemy)
        b.match_stats[enemy] = ScoringSystem.init_ai_stats()

    env_name = config.get("environment", "clear")
    env = ENVIRONMENTS.get(env_name, ENVIRONMENTS["clear"])
    occupied = {HexGrid.coords_to_hex(s.pos) for s in b.ships}
    occupied.discard(None)

    ast_min, ast_max = env.get("asteroids", (0, 0))
    for _ in range(random.randint(ast_min, ast_max)):
        for _ in range(20):
            row = random.randint(3, GRID_ROWS - 2)
            col = random.randint(2, max_col(row) - 1)
            if (row, col) not in occupied:
                b.asteroids.append(Asteroid((row, col)))
                occupied.add((row, col))
                break

    for neb_type_key, count in [("nebula_red", env.get("nebula_red", 0)),
                                 ("nebula_green", env.get("nebula_green", 0)),
                                 ("nebula_purple", env.get("nebula_purple", 0))]:
        ntype = neb_type_key.split("_")[1]
        for _ in range(count):
            center_row = random.randint(5, GRID_ROWS - 4)
            center_col = random.randint(3, max_col(center_row) - 2)
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    r, c = center_row + dr, center_col + dc
                    if r < 1 or r > GRID_ROWS or c < 1 or c > max_col(r):
                        continue
                    if (r, c) in occupied:
                        continue
                    neb = NebulaTile((r, c), ntype)
                    b.nebulae.append(neb)
                    b.nebulae_by_hex[(r, c)] = neb
                    occupied.add((r, c))

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
