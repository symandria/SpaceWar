from spacewar.systems.weapons import (
    WeaponType, WEAPON_STATS, get_weapon_damage, get_weapon_display_name,
    get_weapon_range,
)


class TestWeaponStats:
    def test_all_weapon_types_have_stats(self):
        for wtype in WeaponType:
            assert wtype in WEAPON_STATS, f"{wtype} missing stats"

    # Full-turn damage targets at starter weapon power 10, relative to
    # the torpedo baseline (1x = 40): lazers 66 (1.66x), disruptors 56
    # (1.4x), point lazers 16 (0.4x), shockwave 28 (0.7x), HE torpedo
    # 28 (0.7x), mines 80 (2x). Per-tick damage is rounded up, so
    # multi-tick weapons land slightly above target.

    def test_torpedoes_damage_baseline_40(self):
        assert get_weapon_damage(WeaponType.TORPEDOES, 10) == 40

    def test_lazers_damage_1_66x(self):
        import math
        per_hit = WEAPON_STATS[WeaponType.LAZERS]["damage_per_hit"](10)
        assert per_hit == math.ceil(10 * 6.6 / 5)  # 14
        assert get_weapon_damage(WeaponType.LAZERS, 10) == 70

    def test_disruptors_damage_1_4x(self):
        import math
        # 2 bolts per volley x 3 volleys = 6 hits
        per_hit = WEAPON_STATS[WeaponType.DISRUPTORS]["damage_per_hit"](10)
        assert per_hit == math.ceil(10 * 5.6 / 6)  # 10
        assert get_weapon_damage(WeaponType.DISRUPTORS, 10) == 60
        assert WEAPON_STATS[WeaponType.DISRUPTORS]["hits"] == 6
        assert WEAPON_STATS[WeaponType.DISRUPTORS]["projectile"] is True

    def test_point_lazers_damage_0_4x(self):
        assert get_weapon_damage(WeaponType.POINT_LAZERS, 10) == 16

    def test_point_lazers_damage_floor(self):
        damage = get_weapon_damage(WeaponType.POINT_LAZERS, 0)
        assert damage >= 1  # floor at 1

    def test_shockwave_damage_0_7x(self):
        assert get_weapon_damage(WeaponType.SHOCKWAVE, 10) == 28

    def test_he_torpedo_damage_0_7x(self):
        assert get_weapon_damage(WeaponType.HE_TORPEDO, 10) == 28

    def test_mines_damage_1_5x(self):
        assert get_weapon_damage(WeaponType.MINES, 10) == 60

    def test_weapon_ranges(self):
        assert get_weapon_range(WeaponType.LAZERS) == 15
        assert get_weapon_range(WeaponType.TORPEDOES) == 15
        assert get_weapon_range(WeaponType.DISRUPTORS) == 8
        assert get_weapon_range(WeaponType.POINT_LAZERS) == 15
        assert get_weapon_range(WeaponType.SHOCKWAVE) == 2
        assert get_weapon_range(WeaponType.HE_TORPEDO) == 12
        assert get_weapon_range(WeaponType.MINES) == 1  # drop range

    def test_display_names(self):
        for wtype in WeaponType:
            name = get_weapon_display_name(wtype)
            assert isinstance(name, str)
            assert len(name) > 0

    def test_damage_scales_with_wp(self):
        for wtype in WeaponType:
            d5 = get_weapon_damage(wtype, 5)
            d20 = get_weapon_damage(wtype, 20)
            assert d20 >= d5, f"{wtype} doesn't scale with WP"


class TestWeaponBalance:
    def test_damage_ordering(self):
        # lazers > mines >= disruptors > torpedoes > shockwave/HE > point
        wp = 10
        dmg = {wt: get_weapon_damage(wt, wp) for wt in WeaponType}
        assert dmg[WeaponType.LAZERS] > dmg[WeaponType.MINES]
        assert dmg[WeaponType.MINES] >= dmg[WeaponType.DISRUPTORS]
        assert dmg[WeaponType.DISRUPTORS] > dmg[WeaponType.TORPEDOES]
        assert dmg[WeaponType.TORPEDOES] > dmg[WeaponType.SHOCKWAVE]
        assert dmg[WeaponType.SHOCKWAVE] == dmg[WeaponType.HE_TORPEDO]
        assert dmg[WeaponType.HE_TORPEDO] > dmg[WeaponType.POINT_LAZERS]

    def test_mines_highest_single_hit(self):
        # Among single-strike weapons, mines hit hardest.
        wp = 10
        mine_dmg = get_weapon_damage(WeaponType.MINES, wp)
        for wtype in (WeaponType.TORPEDOES, WeaponType.POINT_LAZERS,
                      WeaponType.SHOCKWAVE, WeaponType.HE_TORPEDO):
            other = get_weapon_damage(wtype, wp)
            assert mine_dmg >= other, \
                f"Mines ({mine_dmg}) should be >= {wtype.value} ({other})"
