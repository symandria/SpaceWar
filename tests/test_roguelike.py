import pytest
import pygame
from spacewar.roguelike.run import Run
from spacewar.roguelike.inventory import Inventory
from spacewar.roguelike.sector_map import SectorMap
from spacewar.roguelike.encounters import (
    NodeType, generate_battle_config, generate_shop_inventory, generate_event,
    TIER_RANKS, TIER_ENEMY_COUNTS, BOSS_RANKS,
)
from spacewar.roguelike.loot import (
    generate_battle_loot, generate_salvage_loot, apply_loot, format_loot,
)
from spacewar.roguelike.upgrades import (
    get_upgrade_level, can_upgrade, upgrade_component, get_upgrade_cost_text,
)
from spacewar.components.defaults import basic_engine
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.states.resolution_states import GameOverState, TurnResolutionState
from spacewar.states.state_machine import StateID
from spacewar.systems.scoring import ScoringSystem


def _implied_points(comp, base_stats):
    """How many upgrade points the component's stats represent over a
    baseline, derived from the step/cost table."""
    from spacewar.roguelike.upgrades import COMPONENT_STAT_STEPS
    total = 0
    for stat, (step, cost) in COMPONENT_STAT_STEPS[comp.slot].items():
        delta = comp.stats.get(stat, 0) - base_stats.get(stat, 0)
        assert delta % step == 0, f"{stat} delta {delta} not a multiple of {step}"
        total += (delta // step) * cost
    return total


class _DummySettings:
    foreground = (255, 255, 255)
    background = (0, 0, 0)


class _DummyTextManager:
    def load(self, key):
        values = {
            "after-battle-report-player": "{winning_faction} wins\n{quote}",
            "after-battle-report-other": "{winning_faction} wins\n{quote}",
            "after-battle-report-draw": "{winning_faction}\n{quote}",
            "faction-name-federation": "Federation",
            "victory-quote-federation": "Victory",
            "rank-cadet": "Cadet",
            "statistics-ship": "{name} {extras} {total}",
            "statistics-sentry": "{name} {extras} {total}",
            "extras-you": "you",
            "extras-human": "human",
            "extras-dead": " dead",
        }
        return values.get(key, key)


class _InactiveResolver:
    is_active = False

    def tick(self, battle):
        return []


class _Battle:
    def __init__(self, player, enemies=None):
        self.ships = [player] + list(enemies or [])
        self.dead_ships = []
        self.match_stats = {}
        self.team_game = False
        self.home_player = player
        self.player = player


def _make_roguelike_ship(race="federation"):
    ship = Ship(race, HexGrid.hex_to_coords(7, 5), 180,
                "cadet", "Captain", "Ship", 100, 10, 5,
                human=True, pixel_perfect=False)
    ship.image = pygame.Surface((9, 9))
    return ship


class _DummyThemeLoader:
    themes = {}
    active_theme = None
    active_races = ()


def _make_game_for_resolution(battle):
    class Game:
        pass

    game = Game()
    game.battle = battle
    game.infofont = pygame.font.SysFont("Courier New", 12)
    game.display = pygame.display.get_surface()
    game.settings = _DummySettings()
    game.text_manager = _DummyTextManager()
    game.turn_resolver = _InactiveResolver()
    game.scoring_system = ScoringSystem()
    game.theme_loader = _DummyThemeLoader()
    game.instant_action = True
    game.player_character = None
    game.active_run = None
    game.message_box = None
    game.selection_list = None

    from spacewar.ui.selection_list import SelectionList

    def make_selection_list(title, *buttons):
        return SelectionList(
            title, game.infofont, game.settings.foreground,
            game.settings.background, game.display.get_width(), *buttons)

    game.make_selection_list = make_selection_list
    return game


class TestInventory:
    def test_scrap(self):
        inv = Inventory()
        inv.add_scrap(100)
        assert inv.scrap == 100
        assert inv.spend_scrap(60)
        assert inv.scrap == 40
        assert not inv.spend_scrap(50)

    def test_materials(self):
        inv = Inventory()
        inv.add_material("common", 5)
        assert inv.has_materials("common", 5)
        assert not inv.has_materials("common", 6)
        assert inv.spend_material("common", 3)
        assert inv.materials["common"] == 2

    def test_components(self):
        inv = Inventory()
        eng = basic_engine()
        inv.add_component(eng)
        assert len(inv.components) == 1
        from spacewar.components.base import ComponentSlot
        found = inv.get_components_for_slot(ComponentSlot.ENGINE)
        assert len(found) == 1
        assert inv.remove_component(eng)
        assert len(inv.components) == 0

    def test_serialization(self):
        inv = Inventory()
        inv.add_scrap(50)
        inv.add_material("rare", 2)
        data = inv.to_dict()
        assert data["scrap"] == 50
        assert data["materials"]["rare"] == 2


class TestSectorMap:
    def test_generate_creates_nodes(self):
        sm = SectorMap()
        sm.generate(1)
        assert len(sm.nodes) > 0
        assert sm.current_node is not None

    def test_has_boss_node(self):
        sm = SectorMap()
        sm.generate(1)
        boss_nodes = [n for n in sm.nodes.values() if n.node_type == NodeType.BOSS]
        assert len(boss_nodes) >= 1

    def test_available_nodes(self):
        sm = SectorMap()
        sm.generate(1)
        available = sm.get_available_nodes()
        assert len(available) > 0

    def test_move_to(self):
        sm = SectorMap()
        sm.generate(1)
        available = sm.get_available_nodes()
        node = available[0]
        sm.move_to(node)
        assert sm.current_node == node
        assert node.completed

    def test_tier_complete_after_boss(self):
        sm = SectorMap()
        sm.generate(1)
        boss = [n for n in sm.nodes.values() if n.node_type == NodeType.BOSS][0]
        sm.move_to(boss)
        assert sm.is_tier_complete()

    def test_generates_for_each_tier(self):
        for tier in range(1, 4):
            sm = SectorMap()
            sm.generate(tier)
            assert len(sm.nodes) >= 3


class TestEncounters:
    def test_battle_config_tier1(self):
        config = generate_battle_config(1)
        assert "enemies" in config
        assert len(config["enemies"]) >= 1
        assert config["tier"] == 1

    def test_battle_config_boss(self):
        config = generate_battle_config(2, NodeType.BOSS)
        assert config["is_boss"]
        assert config["boss_mode"] in ("duel", "pair")
        if config["boss_mode"] == "duel":
            assert len(config["enemies"]) == 1
            assert config["enemies"][0][0] == BOSS_RANKS[2]
        else:
            assert len(config["enemies"]) == 2
            # Teamed pair shares one race.
            assert config["enemies"][0][1] == config["enemies"][1][1]

    def test_shop_inventory(self):
        items = generate_shop_inventory(1)
        assert len(items) > 0
        has_repair = any(i.get("type") == "repair" for i in items)
        assert has_repair

    def test_event_has_choices(self):
        event = generate_event(1)
        assert "text" in event
        assert "choices" in event
        assert len(event["choices"]) >= 2


class TestLoot:
    def test_battle_loot_has_scrap(self):
        loot = generate_battle_loot(1, 2, True)
        assert loot["scrap"] > 0

    def test_battle_loot_scales_with_tier(self):
        loot1 = generate_battle_loot(1, 1, True)
        loot3 = generate_battle_loot(3, 1, True)
        assert loot3["scrap"] > loot1["scrap"]

    def test_salvage_loot(self):
        loot = generate_salvage_loot(2)
        assert loot["scrap"] > 0

    def test_apply_loot_to_inventory(self):
        inv = Inventory()
        loot = {"scrap": 50, "materials": {"common": 3}, "components": []}
        apply_loot(loot, inv)
        assert inv.scrap == 50
        assert inv.materials["common"] == 3

    def test_format_loot(self):
        loot = {"scrap": 50, "materials": {"common": 3}, "components": []}
        text = format_loot(loot)
        assert "50" in text
        assert "Common" in text


class TestUpgrades:
    def test_initial_level_zero(self):
        eng = basic_engine()
        assert get_upgrade_level(eng) == 0

    def test_upgrade_increases_level(self):
        eng = basic_engine()
        inv = Inventory()
        inv.add_scrap(500)
        inv.add_material("common", 10)
        inv.add_material("uncommon", 10)
        inv.add_material("rare", 10)
        assert upgrade_component(eng, inv)
        assert get_upgrade_level(eng) == 1

    def test_upgrade_adds_one_stat_point(self):
        eng = basic_engine()
        base = dict(eng.stats)
        inv = Inventory()
        inv.add_scrap(500)
        inv.add_material("common", 10)
        upgrade_component(eng, inv)
        assert _implied_points(eng, base) == 1

    def test_max_level_three(self):
        eng = basic_engine()
        inv = Inventory()
        inv.add_scrap(2000)
        inv.add_material("common", 50)
        inv.add_material("uncommon", 50)
        inv.add_material("rare", 50)
        assert upgrade_component(eng, inv)
        assert upgrade_component(eng, inv)
        assert upgrade_component(eng, inv)
        assert not upgrade_component(eng, inv)
        assert get_upgrade_level(eng) == 3

    def test_cost_text(self):
        eng = basic_engine()
        text = get_upgrade_cost_text(eng)
        assert "common" in text
        assert "scrap" in text

    def test_failed_upgrade_does_not_spend_partial_materials(self):
        eng = basic_engine()
        inv = Inventory()
        inv.add_scrap(500)
        inv.add_material("common", 10)
        inv.add_material("uncommon", 2)

        assert upgrade_component(eng, inv)
        assert upgrade_component(eng, inv)
        assert inv.materials["uncommon"] == 0

        assert not upgrade_component(eng, inv)
        assert inv.scrap == 350
        assert inv.materials["common"] == 5
        assert inv.materials["uncommon"] == 0
        assert inv.materials["rare"] == 0
        assert get_upgrade_level(eng) == 2


class TestRun:
    def test_create_run(self):
        run = Run("federation")
        assert run.alive
        assert not run.victory
        assert run.current_tier == 1
        assert run.hull > 0
        assert run.shields > 0

    def test_advance_tier(self):
        run = Run("federation")
        run.sector_map.move_to(
            [n for n in run.sector_map.nodes.values()
             if n.node_type == NodeType.BOSS][0])
        assert run.advance_tier()
        assert run.current_tier == 2

    def test_final_tier_victory(self):
        run = Run("federation")
        run.current_tier = 3
        run.sector_map.generate(3)
        run.sector_map.move_to(
            [n for n in run.sector_map.nodes.values()
             if n.node_type == NodeType.BOSS][0])
        assert not run.advance_tier()
        assert run.victory

    def test_battle_results_with_loot(self):
        run = Run("federation")
        loot = run.apply_battle_results(True, 2, 40, 80)
        assert loot is not None
        assert run.hull == 40
        # Shields recharge fully between nodes; hull damage persists.
        assert run.shields == run.max_shields
        assert run.inventory.scrap > 0

    def test_death_on_hull_zero(self):
        run = Run("federation")
        run.apply_battle_results(False, 0, -1, 0)
        assert not run.alive

    def test_rest_heals(self):
        run = Run("federation")
        run.hull = 20
        run.shields = 30
        hull_heal, shield_heal = run.rest()
        assert run.hull > 20
        assert run.shields > 30

    def test_rest_reports_actual_healing_at_cap(self):
        run = Run("federation")
        run.hull = run.max_hull - 1
        run.shields = run.max_shields - 2
        hull_heal, shield_heal = run.rest()
        assert hull_heal == 1
        assert shield_heal == 2
        assert run.hull == run.max_hull
        assert run.shields == run.max_shields

    def test_equip_component(self):
        run = Run("federation")
        eng = basic_engine(acceleration=5)
        run.inventory.add_component(eng)
        run.equip_component(eng)
        from spacewar.components.base import ComponentSlot
        assert run.loadout.get_stat(ComponentSlot.ENGINE, "acceleration") == 5

    def test_status_text(self):
        run = Run("federation")
        text = run.get_status_text()
        assert "Tier" in text
        assert "Hull" in text
        assert "Scrap" in text


class TestRoguelikeBattleResolution:
    def test_game_over_transition_preserves_home_player(self):
        player = _make_roguelike_ship()
        battle = _Battle(player)
        battle.match_stats[player] = ScoringSystem.init_player_stats(
            player, ("federation",), False)
        game = _make_game_for_resolution(battle)

        result = TurnResolutionState(game).update()

        assert result == StateID.GAME_OVER
        assert game.battle.home_player is player

    def test_won_battle_applies_surviving_player_stats_to_run(self):
        run = Run("federation")
        player = _make_roguelike_ship()
        player.hull = 37
        player.shields = 42

        battle = _Battle(player)
        battle.match_stats[player] = ScoringSystem.init_player_stats(
            player, ("federation",), False)

        game = _make_game_for_resolution(battle)
        game.active_run = run

        event = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(1, 1), button=1)
        result = GameOverState(game).handle_event(event)

        assert result == StateID.ROGUELIKE_MAP
        assert run.alive
        assert run.battles_won == 1
        assert run.hull == 37
        assert run.shields == run.max_shields  # recharged between nodes
        assert run.inventory.scrap > 0

    def test_defeat_returns_to_main_menu_with_buttons(self):
        run = Run("federation")
        player = _make_roguelike_ship()
        player.hull = -10

        battle = _Battle(player)
        battle.ships = []
        battle.dead_ships = [player]
        battle.match_stats[player] = ScoringSystem.init_player_stats(
            player, ("federation",), False)

        game = _make_game_for_resolution(battle)
        game.active_run = run

        event = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(1, 1), button=1)
        result = GameOverState(game).handle_event(event)

        assert result == StateID.MAIN_MENU
        assert game.active_run is None
        assert game.selection_list is not None
        assert game.message_box is not None


class TestEncounterRaces:
    @staticmethod
    def _spec_race_ok(spec, races):
        """Faction ships keep their cross-theme signature sprite;
        anything faction-less must come from the allowed races."""
        from spacewar.roguelike.factions import FACTIONS
        rank, race, faction = spec[0], spec[1], spec[2]
        if faction:
            return race in FACTIONS[faction]["races"] or race in races
        return race in races

    def test_battle_config_restricted_to_available_races(self):
        races = ("federation", "klingon")
        for tier in (1, 2, 3):
            for ntype in (NodeType.BATTLE, NodeType.ELITE, NodeType.BOSS):
                config = generate_battle_config(tier, ntype, races=races)
                for spec in config["enemies"]:
                    assert self._spec_race_ok(spec, races)

    def test_battle_config_defaults_to_classic_races(self):
        from spacewar.roguelike.encounters import BASE_RACES
        for tier in (1, 2, 3):
            config = generate_battle_config(tier, NodeType.BATTLE)
            for spec in config["enemies"]:
                assert self._spec_race_ok(spec, BASE_RACES)

    def test_battle_config_excludes_sentry(self):
        races = ("sentry", "federation")
        for _ in range(30):
            config = generate_battle_config(1, NodeType.BATTLE, races=races)
            for spec in config["enemies"]:
                assert spec[1] != "sentry"


class TestSectorMapBoss:
    def test_exactly_one_boss_node(self):
        for tier in range(1, 4):
            for _ in range(10):
                sm = SectorMap()
                sm.generate(tier)
                bosses = [n for n in sm.nodes.values()
                          if n.node_type == NodeType.BOSS]
                assert len(bosses) == 1


class TestRunHullEdgeCases:
    def test_survives_battle_at_zero_hull(self):
        run = Run("federation")
        loot = run.apply_battle_results(True, 1, 0, 0)
        assert run.alive
        assert loot is not None
        assert run.hull == 0

    def test_death_clamps_negative_stats(self):
        run = Run("federation")
        run.apply_battle_results(False, 0, -20, -5)
        assert not run.alive
        assert run.hull == 0
        assert run.shields == 0

    def test_take_hull_damage_exact_zero_survives(self):
        run = Run("federation")
        run.take_hull_damage(run.hull)
        assert run.alive
        assert run.hull == 0

    def test_take_hull_damage_overkill_dies(self):
        run = Run("federation")
        run.take_hull_damage(run.hull + 1)
        assert not run.alive
        assert run.hull == 0


class TestEquipPowerBudget:
    def test_equip_rejects_over_power_budget(self):
        from spacewar.components.base import Component, ComponentSlot
        run = Run("federation")
        hog = Component(ComponentSlot.ENGINE, "Power Hog", 99, max_speed=9)
        run.inventory.add_component(hog)
        assert not run.equip_component(hog)
        assert hog in run.inventory.components
        assert run.loadout.get_component(ComponentSlot.ENGINE).name != "Power Hog"

    def test_equip_menu_action_reports_power_failure(self):
        from spacewar.components.base import Component, ComponentSlot
        from spacewar.states.roguelike_states import _EquipAction
        run = Run("federation")
        battle = _Battle(_make_roguelike_ship())
        game = _make_game_for_resolution(battle)
        game.active_run = run
        hog = Component(ComponentSlot.ENGINE, "Power Hog", 99, max_speed=9)
        run.inventory.add_component(hog)
        result = _EquipAction(game, hog)()
        assert game.message_box is not None
        assert hog in run.inventory.components
        assert result is not None  # refreshed equip menu

    def test_equip_within_budget_swaps_components(self):
        run = Run("federation")
        eng = basic_engine(acceleration=5)
        run.inventory.add_component(eng)
        assert run.equip_component(eng)
        assert eng not in run.inventory.components
        from spacewar.components.base import ComponentSlot
        old = run.inventory.get_components_for_slot(ComponentSlot.ENGINE)
        assert len(old) == 1


class TestItemization:
    def test_power_scales_50_percent_per_tier_above_base(self):
        from spacewar.roguelike.loot import power_cost_for_tier
        assert power_cost_for_tier(4, 1) == 6   # 4 * 1.5
        assert power_cost_for_tier(4, 2) == 9   # 4 * 2.25
        assert power_cost_for_tier(4, 3) == 14  # 4 * 3.375

    def test_base_points_by_tier(self):
        from spacewar.roguelike.loot import base_points_for_tier
        assert base_points_for_tier(1) == 2
        assert base_points_for_tier(2) == 6
        assert base_points_for_tier(3) == 10

    def test_drops_carry_tier_base_points(self):
        from spacewar.components.base import ComponentSlot
        from spacewar.components import defaults as d
        from spacewar.roguelike.loot import _random_component, base_points_for_tier
        from spacewar.systems.weapons import WeaponType, WEAPON_STATS

        base_lookup = {
            ComponentSlot.ENGINE: d.basic_engine().stats,
            ComponentSlot.SENSORS: d.basic_sensors().stats,
            ComponentSlot.SHIELDS: d.basic_shields().stats,
            ComponentSlot.HULL: d.basic_hull().stats,
            ComponentSlot.STEALTH: d.basic_stealth().stats,
            ComponentSlot.POWER_SOURCE: d.basic_power_source().stats,
        }
        for tier in (1, 2, 3):
            for _ in range(30):
                comp = _random_component(tier)
                if comp.slot == ComponentSlot.SPECIAL:
                    continue  # specials have no stat steps to allocate
                if comp.slot in (ComponentSlot.WEAPON_1, ComponentSlot.WEAPON_2):
                    wtype = WeaponType(comp.get("weapon_type"))
                    base = {"weapon_range": WEAPON_STATS[wtype]["max_range"]}
                else:
                    base = base_lookup[comp.slot]
                assert _implied_points(comp, base) == base_points_for_tier(tier), \
                    f"tier {tier} {comp.name} has wrong point total"

    def test_allocation_respects_caps(self):
        from spacewar.roguelike.upgrades import allocate_upgrade_points
        from spacewar.components.defaults import basic_shields
        eng = basic_engine()
        allocate_upgrade_points(eng, 100)
        assert eng.get("acceleration") <= 6
        assert eng.get("turning_degrees") <= 360
        sh = basic_shields()
        allocate_upgrade_points(sh, 100)
        assert sh.get("active_dr") <= 50

    def test_no_range_fixed_weapon_drops(self):
        from spacewar.components.base import ComponentSlot
        from spacewar.roguelike.loot import _random_component
        for _ in range(200):
            comp = _random_component(1)
            if comp.slot in (ComponentSlot.WEAPON_1, ComponentSlot.WEAPON_2):
                assert comp.get("weapon_type") not in ("shockwave", "mines")

    def test_reactor_shop_price_not_trivial(self):
        from spacewar.components.base import ComponentSlot
        from spacewar.roguelike.encounters import generate_shop_inventory
        found = 0
        for _ in range(60):
            for item in generate_shop_inventory(1):
                comp = item.get("component")
                if comp and comp.slot == ComponentSlot.POWER_SOURCE:
                    found += 1
                    assert item["price"] >= 80
        assert found > 0


class TestShopAndEvents:
    def _game_with_run(self):
        run = Run("federation")
        battle = _Battle(_make_roguelike_ship())
        game = _make_game_for_resolution(battle)
        game.active_run = run
        return game, run

    def test_buy_component(self):
        from spacewar.states.roguelike_states import _BuyComponent
        from spacewar.roguelike.encounters import generate_shop_inventory
        game, run = self._game_with_run()
        items = generate_shop_inventory(1)
        game.roguelike_shop_items = items
        idx = next(i for i, it in enumerate(items) if "component" in it)
        comp = items[idx]["component"]
        run.inventory.add_scrap(items[idx]["price"])
        _BuyComponent(game, idx)()
        assert comp in run.inventory.components
        assert run.inventory.scrap == 0
        assert comp not in [it.get("component") for it in items]

    def test_buy_component_insufficient_scrap(self):
        from spacewar.states.roguelike_states import _BuyComponent
        from spacewar.roguelike.encounters import generate_shop_inventory
        game, run = self._game_with_run()
        items = generate_shop_inventory(1)
        game.roguelike_shop_items = items
        idx = next(i for i, it in enumerate(items) if "component" in it)
        count = len(items)
        _BuyComponent(game, idx)()
        assert len(items) == count  # nothing removed
        assert not run.inventory.components
        assert game.message_box is not None

    def test_buy_repair_restores_ship(self):
        from spacewar.states.roguelike_states import _BuyRepair
        from spacewar.roguelike.encounters import generate_shop_inventory
        game, run = self._game_with_run()
        items = generate_shop_inventory(1)
        game.roguelike_shop_items = items
        idx = next(i for i, it in enumerate(items) if it.get("type") == "repair")
        run.hull = 5
        run.shields = 5
        run.inventory.add_scrap(items[idx]["price"])
        _BuyRepair(game, idx)()
        assert run.hull == run.max_hull
        assert run.shields == run.max_shields

    def test_event_trade_insufficient_scrap(self):
        from spacewar.states.roguelike_states import _EventChoice
        game, run = self._game_with_run()
        result = _EventChoice(game, "trade",
                              {"cost_scrap": 50,
                               "materials": {"uncommon": 1}})()
        assert result == StateID.ROGUELIKE_MAP
        assert run.inventory.scrap == 0
        assert run.inventory.materials["uncommon"] == 0
        assert game.message_box is not None

    def test_event_risk_death_shows_destroyed(self, monkeypatch):
        import spacewar.states.roguelike_states  # noqa: F401
        from spacewar.states.roguelike_states import _EventChoice
        import random as _random
        game, run = self._game_with_run()
        monkeypatch.setattr(_random, "random", lambda: 1.0)  # force bad roll
        result = _EventChoice(game, "risk",
                              {"good": {"scrap": 10},
                               "bad": {"hull_damage": 9999},
                               "chance": 0.6})()
        assert result == StateID.ROGUELIKE_MAP
        assert not run.alive
        assert run.hull == 0
