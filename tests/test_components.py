from spacewar.components.base import Component, ComponentSlot
from spacewar.components.ship_loadout import ShipLoadout
from spacewar.components.defaults import (
    build_default_loadout, basic_engine, basic_shields, basic_hull,
    basic_lazers, basic_torpedoes, basic_stealth, basic_sensors,
    basic_power_source, no_special, teleportation_special, ambush_special,
    phasing_special,
)
from spacewar.components.registry import ComponentRegistry


class TestComponent:
    def test_create_component(self):
        c = Component(ComponentSlot.ENGINE, "Test Engine", 3, max_speed=5)
        assert c.slot == ComponentSlot.ENGINE
        assert c.name == "Test Engine"
        assert c.power_cost == 3
        assert c.get("max_speed") == 5
        assert c.get("missing", 99) == 99

    def test_all_slots_exist(self):
        expected = {"engine", "sensors", "shields", "hull", "weapon_1",
                    "weapon_2", "special", "special_2", "power_source",
                    "stealth", "tractor"}
        actual = {s.value for s in ComponentSlot}
        assert actual == expected


class TestShipLoadout:
    def test_default_loadout_is_valid(self, default_loadout):
        assert default_loadout.is_valid()
        assert default_loadout.power_budget() == 24
        assert default_loadout.total_power_cost() == 18

    def test_headroom_is_33_percent(self, default_loadout):
        cost = default_loadout.total_power_cost()
        budget = default_loadout.power_budget()
        headroom = (budget - cost) / cost
        assert headroom >= 0.30

    def test_all_slots_filled(self, default_loadout):
        for slot in ComponentSlot:
            if slot == ComponentSlot.SPECIAL_2:
                continue  # second special bay starts empty
            assert default_loadout.get_component(slot) is not None, \
                f"Slot {slot.value} is empty"

    def test_get_stat(self, default_loadout):
        assert default_loadout.get_stat(ComponentSlot.ENGINE, "max_speed") == 5
        assert default_loadout.get_stat(ComponentSlot.ENGINE, "acceleration") == 2
        assert default_loadout.get_stat(ComponentSlot.SHIELDS, "strength") == 100
        assert default_loadout.get_stat(ComponentSlot.HULL, "strength") == 50

    def test_equip_replaces(self, default_loadout):
        old = default_loadout.get_component(ComponentSlot.ENGINE)
        new_engine = basic_engine(acceleration=4)
        default_loadout.equip(new_engine)
        assert default_loadout.get_stat(ComponentSlot.ENGINE, "acceleration") == 4
        assert default_loadout.get_component(ComponentSlot.ENGINE) is new_engine

    def test_can_equip_checks_budget(self, default_loadout):
        expensive = Component(ComponentSlot.ENGINE, "Huge Engine", 50, max_speed=10)
        assert not default_loadout.can_equip(expensive)
        cheap = Component(ComponentSlot.ENGINE, "Tiny Engine", 1, max_speed=3)
        assert default_loadout.can_equip(cheap)

    def test_has_special(self, default_loadout):
        assert not default_loadout.has_special("teleportation")
        default_loadout.equip(teleportation_special())
        assert default_loadout.has_special("teleportation")

    def test_weapon_slots(self, default_loadout):
        w1 = default_loadout.get_weapon(1)
        w2 = default_loadout.get_weapon(2)
        assert w1.get("weapon_type") == "lazers"
        assert w2.get("weapon_type") == "torpedoes"


class TestRaceSpecials:
    def test_cloaking_race(self):
        loadout = build_default_loadout(["cloaking"])
        assert loadout.get_stat(ComponentSlot.STEALTH, "active_cloak") is True

    def test_teleportation_race(self):
        loadout = build_default_loadout(["teleportation"])
        assert loadout.has_special("teleportation")
        special = loadout.get_component(ComponentSlot.SPECIAL)
        assert special.get("teleport_range") == 10
        assert special.get("recharge") == 3

    def test_ablative_race(self):
        loadout = build_default_loadout(["ablative"])
        assert loadout.get_stat(ComponentSlot.SHIELDS, "active_dr") == 50

    def test_acceleration_race(self):
        loadout = build_default_loadout(["acceleration"])
        assert loadout.get_stat(ComponentSlot.ENGINE, "acceleration") == 3

    def test_regeneration_race(self):
        loadout = build_default_loadout(["regeneration"])
        assert loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen") == 10

    def test_regen_5_race(self):
        loadout = build_default_loadout(["regen_5"])
        assert loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen") == 5

    def test_regen_10_race(self):
        loadout = build_default_loadout(["regen_10"])
        assert loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen") == 10

    def test_combined_specials(self):
        loadout = build_default_loadout(["cloaking", "teleportation", "regeneration"])
        assert loadout.get_stat(ComponentSlot.STEALTH, "active_cloak") is True
        assert loadout.has_special("teleportation")
        assert loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen") == 10
        assert loadout.is_valid()


class TestComponentRegistry:
    def test_register_and_retrieve(self):
        reg = ComponentRegistry()
        eng = basic_engine()
        reg.register(eng)
        available = reg.get_available(ComponentSlot.ENGINE)
        assert len(available) == 1
        assert available[0] is eng

    def test_get_by_name(self):
        reg = ComponentRegistry()
        reg.register(basic_engine())
        reg.register(basic_engine(acceleration=4))
        found = reg.get_by_name(ComponentSlot.ENGINE, "Basic Engine")
        assert found is not None
        assert found.get("max_speed") == 5
