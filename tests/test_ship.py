from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.components.base import ComponentSlot


class TestShipCreation:
    def test_default_stats(self, default_ship):
        assert default_ship.max_shields == 100
        assert default_ship.max_hull == 50
        assert default_ship.shields == 100
        assert default_ship.hull == 50
        assert default_ship.engine == 5
        assert default_ship.weapon_power == 10
        assert default_ship.phasers == 20
        assert default_ship.torpedoes == 30

    def test_component_derived_stats(self, default_ship):
        assert default_ship.acceleration == 2
        assert default_ship.turning_degrees == 90
        assert default_ship.maneuvering_points == 1
        assert default_ship.vision_forward == 10
        assert default_ship.vision_backward == 5
        assert default_ship.cloak_detection == 0
        assert default_ship.passive_regen == 5
        assert default_ship.active_dr == 0
        assert default_ship.collision_damage == 25
        assert not default_ship.active_cloak
        assert default_ship.passive_stealth == 0

    def test_cloaking_ship_has_cloak(self, cloaking_ship):
        assert cloaking_ship.active_cloak is True
        assert "cloaking" in cloaking_ship.specials

    def test_teleport_ship_has_teleport(self, teleport_ship):
        assert teleport_ship.loadout.has_special("teleportation")
        assert "teleportation" in teleport_ship.specials
        assert teleport_ship.passive_regen == 10

    def test_ablative_ship_has_dr(self, ablative_ship):
        assert ablative_ship.active_dr == 50
        assert "ablative" in ablative_ship.specials


class TestDamageSystem:
    def test_damage_hits_shields_first(self, default_ship):
        default_ship.apply_damage(30)
        assert default_ship.shields == 70
        assert default_ship.hull == 50

    def test_damage_overflow_to_hull(self, default_ship):
        default_ship.apply_damage(120)
        assert default_ship.shields == 0
        assert default_ship.hull == 30

    def test_kill_requires_hull_depletion(self, default_ship):
        default_ship.apply_damage(100)
        assert not default_ship.is_dead()
        assert default_ship.shields == 0
        assert default_ship.hull == 50

    def test_kill_on_hull_zero(self, default_ship):
        default_ship.apply_damage(151)
        assert default_ship.is_dead()
        assert default_ship.hull < 0

    def test_full_damage_through_shields_and_hull(self, default_ship):
        default_ship.apply_damage(80)
        assert default_ship.shields == 20
        assert default_ship.hull == 50
        default_ship.apply_damage(50)
        assert default_ship.shields == 0
        assert default_ship.hull == 20
        default_ship.apply_damage(25)
        assert default_ship.hull == -5
        assert default_ship.is_dead()

    def test_cloaked_takes_double_damage(self, cloaking_ship):
        cloaking_ship.cloaked = True
        cloaking_ship.apply_damage(30)
        assert cloaking_ship.shields == 40  # 30*2=60 damage

    def test_dr_reduces_damage_with_power_shields(self, ablative_ship):
        ablative_ship.action = "power_shields"
        ablative_ship.apply_damage(100)
        # DR 50%: 100 * (100-50)/100 = 50 damage
        assert ablative_ship.shields == 50
        assert ablative_ship.hull == 50

    def test_dr_inactive_when_attacking(self, ablative_ship):
        ablative_ship.action = "weapon_1"
        ablative_ship.apply_damage(100)
        assert ablative_ship.shields == 0
        assert ablative_ship.hull == 50

    def test_dr_inactive_when_no_action(self, ablative_ship):
        ablative_ship.action = None
        ablative_ship.apply_damage(100)
        assert ablative_ship.shields == 0
        assert ablative_ship.hull == 50

    def test_self_destruct_kills_via_hull(self, default_ship):
        default_ship.hull = -1
        assert default_ship.is_dead()


class TestMovement:
    def test_valid_destination_default(self, default_ship):
        ship_hex = HexGrid.coords_to_hex(default_ship.pos)
        assert default_ship.get_valid_destination(
            ship_hex[0] + 1, ship_hex[1], False)

    def test_too_far_destination_rejected(self, default_ship):
        assert not default_ship.get_valid_destination(14, 10, False)

    def test_interpolation(self, default_ship):
        start = default_ship.pos
        target = (start[0] + 28, start[1] + 14)
        default_ship.interpolate_toward(target, 2)
        assert default_ship.pos[0] > start[0]
        assert default_ship.pos[1] > start[1]
