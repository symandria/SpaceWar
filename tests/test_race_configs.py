from spacewar.components.race_configs import build_race_loadout, RACE_COMPONENT_OVERRIDES
from spacewar.components.base import ComponentSlot


class TestRaceLoadouts:
    def test_all_races_build_valid_loadout(self):
        for race in RACE_COMPONENT_OVERRIDES:
            loadout = build_race_loadout(race)
            assert loadout.is_valid(), f"{race} loadout invalid"

    def test_federation_has_dr(self):
        loadout = build_race_loadout("federation")
        assert loadout.get_stat(ComponentSlot.SHIELDS, "active_dr") == 50

    def test_klingon_has_cloak(self):
        loadout = build_race_loadout("klingon")
        assert loadout.get_stat(ComponentSlot.STEALTH, "active_cloak") is True

    def test_tholian_has_high_accel(self):
        loadout = build_race_loadout("tholian")
        assert loadout.get_stat(ComponentSlot.ENGINE, "acceleration") == 3

    def test_borg_has_teleportation(self):
        loadout = build_race_loadout("borg")
        assert loadout.has_special("teleportation")
        special = loadout.get_component(ComponentSlot.SPECIAL)
        assert special.get("teleport_range") == 10
        assert special.get("recharge") == 3

    def test_borg_has_regen(self):
        loadout = build_race_loadout("borg")
        assert loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen") == 10

    def test_dominion_has_regen(self):
        loadout = build_race_loadout("dominion")
        assert loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen") == 10

    def test_shadow_has_cloak_teleport_regen(self):
        loadout = build_race_loadout("shadow")
        assert loadout.get_stat(ComponentSlot.STEALTH, "active_cloak") is True
        assert loadout.has_special("teleportation")
        assert loadout.get_stat(ComponentSlot.SHIELDS, "passive_regen") == 10

    def test_unknown_race_gets_default(self):
        loadout = build_race_loadout("unknown_race")
        assert loadout.is_valid()
        assert loadout.get_stat(ComponentSlot.SHIELDS, "active_dr") == 0
        assert loadout.get_stat(ComponentSlot.STEALTH, "active_cloak") is False

    def test_sentry_gets_default(self):
        loadout = build_race_loadout("sentry")
        assert loadout.is_valid()

    def test_all_loadouts_have_weapons(self):
        for race in RACE_COMPONENT_OVERRIDES:
            loadout = build_race_loadout(race)
            w1 = loadout.get_weapon(1)
            w2 = loadout.get_weapon(2)
            assert w1 is not None, f"{race} missing weapon 1"
            assert w2 is not None, f"{race} missing weapon 2"

    def test_all_loadouts_within_power_budget(self):
        for race in RACE_COMPONENT_OVERRIDES:
            loadout = build_race_loadout(race)
            assert loadout.total_power_cost() <= loadout.power_budget(), \
                f"{race}: cost {loadout.total_power_cost()} > budget {loadout.power_budget()}"
