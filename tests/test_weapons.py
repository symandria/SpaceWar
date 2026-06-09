from spacewar.systems.weapons import (
    WeaponType, WEAPON_STATS, get_weapon_damage, get_weapon_display_name,
    get_weapon_range,
)


class TestWeaponStats:
    def test_all_weapon_types_have_stats(self):
        for wtype in WeaponType:
            assert wtype in WEAPON_STATS, f"{wtype} missing stats"

    def test_lazers_damage(self):
        damage = get_weapon_damage(WeaponType.LAZERS, 10)
        assert damage > 0
        per_hit = WEAPON_STATS[WeaponType.LAZERS]["damage_per_hit"](10)
        assert damage == per_hit * 5

    def test_torpedoes_damage(self):
        damage = get_weapon_damage(WeaponType.TORPEDOES, 10)
        assert damage == 30  # 10 * 3 * 1 hit

    def test_disruptors_damage(self):
        damage = get_weapon_damage(WeaponType.DISRUPTORS, 10)
        per_hit = WEAPON_STATS[WeaponType.DISRUPTORS]["damage_per_hit"](10)
        assert damage == per_hit * 3

    def test_point_lazers_damage_floor(self):
        damage = get_weapon_damage(WeaponType.POINT_LAZERS, 3)
        assert damage >= 1  # floor at 1

    def test_point_lazers_formula(self):
        damage = get_weapon_damage(WeaponType.POINT_LAZERS, 10)
        assert damage == max(1, int(10 * 0.25))

    def test_shockwave_damage(self):
        damage = get_weapon_damage(WeaponType.SHOCKWAVE, 10)
        assert damage == int(10 * 0.4)

    def test_he_torpedo_damage(self):
        damage = get_weapon_damage(WeaponType.HE_TORPEDO, 10)
        assert damage == int(10 * 0.4)

    def test_mines_damage(self):
        damage = get_weapon_damage(WeaponType.MINES, 10)
        assert damage == int(10 * 1.6)

    def test_weapon_ranges(self):
        assert get_weapon_range(WeaponType.LAZERS) == 15
        assert get_weapon_range(WeaponType.TORPEDOES) == 15
        assert get_weapon_range(WeaponType.DISRUPTORS) == 6
        assert get_weapon_range(WeaponType.POINT_LAZERS) == 15
        assert get_weapon_range(WeaponType.SHOCKWAVE) == 2
        assert get_weapon_range(WeaponType.HE_TORPEDO) == 12
        assert get_weapon_range(WeaponType.MINES) == 0

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
    def test_lazers_approx_1_67x(self):
        wp = 30
        total = get_weapon_damage(WeaponType.LAZERS, wp)
        ratio = total / wp
        assert 1.0 <= ratio <= 2.0

    def test_torpedoes_higher_than_lazers(self):
        wp = 10
        lazer = get_weapon_damage(WeaponType.LAZERS, wp)
        torpedo = get_weapon_damage(WeaponType.TORPEDOES, wp)
        assert torpedo > lazer

    def test_mines_highest_single_hit(self):
        wp = 10
        mine_dmg = get_weapon_damage(WeaponType.MINES, wp)
        for wtype in WeaponType:
            if wtype == WeaponType.MINES:
                continue
            other = get_weapon_damage(wtype, wp)
            if wtype != WeaponType.TORPEDOES:
                assert mine_dmg >= other, \
                    f"Mines ({mine_dmg}) should be >= {wtype.value} ({other})"
