import pytest
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
        assert len(config["enemies"]) >= 1
        rank = config["enemies"][0][0]
        assert rank == BOSS_RANKS[2]

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

    def test_upgrade_improves_stats(self):
        eng = basic_engine()
        old_speed = eng.get("max_speed")
        inv = Inventory()
        inv.add_scrap(500)
        inv.add_material("common", 10)
        upgrade_component(eng, inv)
        assert eng.get("max_speed") > old_speed

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
        assert run.shields == 80
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
