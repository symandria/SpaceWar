import math

import pygame

from spacewar.config.constants import SCREEN_SIZE
from spacewar.entities.ship import Ship
from spacewar.entities.torpedo import Torpedo
from spacewar.entities.mine import Mine
from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.weapons import WeaponType, WEAPON_STATS


class CombatSystem:
    def __init__(self, asset_loader, theme_loader):
        self._asset_loader = asset_loader
        self._theme_loader = theme_loader

    def _get_weapon_type(self, ship, action):
        if action == "phaser" or action == "weapon_1":
            comp = ship.loadout.get_weapon(1)
        elif action == "torpedo" or action == "weapon_2":
            comp = ship.loadout.get_weapon(2)
        else:
            return None
        if comp is None:
            return None
        wtype_str = comp.get("weapon_type", "lazers")
        try:
            return WeaponType(wtype_str)
        except ValueError:
            return None

    def _get_ambush_multiplier(self, who):
        if who.loadout.has_special("ambush") and who.was_cloaked:
            if not who.cloaked:
                who.was_cloaked = False
            return 3
        return 1

    def _get_phaser_color(self, who, step=0):
        races = self._theme_loader.active_races
        if who.type in races:
            color = self._theme_loader.get_phaser_color(who.type)
        else:
            color = self._theme_loader.get_phaser_color("sentry")
        if isinstance(color[0], (list, tuple)):
            color = color[step % len(color)]
        return color

    def _get_torpedo_color(self, who):
        races = self._theme_loader.active_races
        if who.type in races:
            return self._theme_loader.get_torpedo_color(who.type)
        return self._theme_loader.get_torpedo_color("sentry")

    def _check_range(self, who, target_hex, weapon_type):
        stats = WEAPON_STATS[weapon_type]
        if stats.get("range_fixed") and weapon_type == WeaponType.SHOCKWAVE:
            return True
        ship_hex = HexGrid.coords_to_hex(who.pos)
        dist = HexGrid.hex_distance(ship_hex, target_hex)
        comp = who.loadout.get_weapon(1) if who.action in ("phaser", "weapon_1") \
            else who.loadout.get_weapon(2)
        weapon_range = stats["max_range"]
        if comp:
            weapon_range = max(weapon_range, comp.get("weapon_range", weapon_range))
        return dist <= weapon_range

    def fire_weapon(self, who, target_hex, step, ships, torpedoes, mines,
                    match_stats, team_game, player, phaser_hit_this_turn):
        wtype = self._get_weapon_type(who, who.action)
        if wtype is None:
            return None, phaser_hit_this_turn

        if not self._check_range(who, target_hex, wtype):
            return None, phaser_hit_this_turn

        if wtype == WeaponType.LAZERS:
            return self.fire_hitscan(who, target_hex, step, ships, torpedoes,
                                    match_stats, team_game, player,
                                    phaser_hit_this_turn, wtype)
        elif wtype == WeaponType.DISRUPTORS:
            return self.fire_hitscan(who, target_hex, step, ships, torpedoes,
                                    match_stats, team_game, player,
                                    phaser_hit_this_turn, wtype)
        elif wtype == WeaponType.POINT_LAZERS:
            return self.fire_point_lazers(who, target_hex, ships,
                                         match_stats, team_game, player)
        elif wtype == WeaponType.SHOCKWAVE:
            self.fire_shockwave(who, ships, match_stats, team_game, player)
            return None, phaser_hit_this_turn
        elif wtype == WeaponType.TORPEDOES:
            self.fire_projectile(who, target_hex, torpedoes, match_stats,
                                player, wtype)
            return None, phaser_hit_this_turn
        elif wtype == WeaponType.HE_TORPEDO:
            self.fire_projectile(who, target_hex, torpedoes, match_stats,
                                player, wtype)
            return None, phaser_hit_this_turn
        elif wtype == WeaponType.MINES:
            self.place_mine(who, target_hex, mines)
            return None, phaser_hit_this_turn

        return None, phaser_hit_this_turn

    def fire_hitscan(self, who, target_hex, step, ships, torpedoes,
                     match_stats, team_game, player, phaser_hit_this_turn,
                     weapon_type=WeaponType.LAZERS):
        self._asset_loader.play_sound("phaser")
        color = self._get_phaser_color(who, step)
        stats = WEAPON_STATS[weapon_type]
        damage_per_hit = stats["damage_per_hit"](who.weapon_power)

        where = HexGrid.hex_to_coords(*target_hex)
        where = where[0] + 4, where[1] + 4
        origin = int(who.pos[0]) + 4, int(who.pos[1]) + 4
        dx, dy = where[0] - origin[0], where[1] - origin[1]
        if abs(dx) <= 0.01 and abs(dy) <= 0.01:
            dx = 100
        while 0 < where[0] < SCREEN_SIZE[0] and 0 < where[1] < SCREEN_SIZE[1]:
            where = where[0] + dx, where[1] + dy

        temp = pygame.surface.Surface(SCREEN_SIZE)
        pygame.draw.line(temp, (255, 255, 255), origin, where, 2)
        temp.set_colorkey((0, 0, 0))
        mask = pygame.mask.from_surface(temp)

        cpoint = None
        for target in ships:
            if target == who:
                continue
            tmask = target.mask
            if mask.overlap(tmask, tuple(map(int, target.pos))):
                omask = mask.overlap_mask(tmask, tuple(map(int, target.pos)))
                points = list(set(omask.outline()))
                for p in points:
                    dist = math.hypot(origin[0] - p[0], origin[1] - p[1])
                    if cpoint is None or dist < cpoint[0]:
                        cpoint = dist, p, target

        for torp in torpedoes:
            omask = mask.overlap_mask(torp.mask, torp.rect.topleft)
            points = list(set(omask.outline()))
            for p in points:
                dist = math.hypot(origin[0] - p[0], origin[1] - p[1])
                if cpoint is None or dist < cpoint[0]:
                    cpoint = dist, p, torp

        if cpoint is not None:
            cpoint_pos, what = cpoint[1], cpoint[2]
            if isinstance(what, Ship):
                damage_multiplier = self._get_ambush_multiplier(who)
                was_dead = what.is_dead()
                what.apply_damage(damage_per_hit * damage_multiplier)
                if who == player and what.is_dead() and not was_dead:
                    match_stats[player]["kills-" + what.type] += 1
                if team_game and who.type == what.type:
                    match_stats[who]["teamdamage"] -= damage_per_hit * damage_multiplier
                else:
                    match_stats[who]["damage"] += damage_per_hit * damage_multiplier
                if who == player and not phaser_hit_this_turn:
                    match_stats[player]["phasers hit"] += 1
                    phaser_hit_this_turn = True
            else:
                what.deactivate()
                if what in torpedoes:
                    torpedoes.remove(what)
            return (color, origin, cpoint_pos, 2), phaser_hit_this_turn
        else:
            return (color, origin, where, 2), phaser_hit_this_turn

    def fire_phaser(self, who, target_hex, step, ships, torpedoes,
                    match_stats, team_game, player, phaser_hit_this_turn):
        return self.fire_hitscan(who, target_hex, step, ships, torpedoes,
                                match_stats, team_game, player,
                                phaser_hit_this_turn, WeaponType.LAZERS)

    def fire_point_lazers(self, who, target_hex, ships, match_stats,
                          team_game, player):
        self._asset_loader.play_sound("phaser")
        color = self._get_phaser_color(who)
        damage = WEAPON_STATS[WeaponType.POINT_LAZERS]["damage_per_hit"](who.weapon_power)
        damage *= self._get_ambush_multiplier(who)
        origin = int(who.pos[0]) + 4, int(who.pos[1]) + 4

        closest = None
        closest_dist = float('inf')
        for target in ships:
            if target == who:
                continue
            thex = HexGrid.coords_to_hex(target.pos)
            dist = HexGrid.hex_distance(target_hex, thex)
            if dist == 0:
                closest = target
                break
            if dist < closest_dist:
                closest_dist = dist
                closest = target

        endpoint = HexGrid.hex_to_coords(*target_hex)
        endpoint = endpoint[0] + 4, endpoint[1] + 4

        if closest and HexGrid.coords_to_hex(closest.pos) == target_hex:
            was_dead = closest.is_dead()
            closest.apply_damage(damage)
            if who == player and closest.is_dead() and not was_dead:
                match_stats[player]["kills-" + closest.type] += 1
            if team_game and who.type == closest.type:
                match_stats[who]["teamdamage"] -= damage
            else:
                match_stats[who]["damage"] += damage
            endpoint = int(closest.pos[0]) + 4, int(closest.pos[1]) + 4

        return (color, origin, endpoint, 1), False

    def fire_shockwave(self, who, ships, match_stats, team_game, player):
        self._asset_loader.play_sound("hit")
        damage = WEAPON_STATS[WeaponType.SHOCKWAVE]["damage_per_hit"](who.weapon_power)
        damage *= self._get_ambush_multiplier(who)
        radius = WEAPON_STATS[WeaponType.SHOCKWAVE]["aoe_radius"]
        ship_hex = HexGrid.coords_to_hex(who.pos)

        for target in ships:
            if target == who:
                continue
            thex = HexGrid.coords_to_hex(target.pos)
            if HexGrid.hex_distance(ship_hex, thex) <= radius:
                was_dead = target.is_dead()
                target.apply_damage(damage)
                if who == player and target.is_dead() and not was_dead:
                    match_stats[player]["kills-" + target.type] += 1
                if team_game and who.type == target.type:
                    match_stats[who]["teamdamage"] -= damage
                else:
                    match_stats[who]["damage"] += damage

    def fire_projectile(self, who, target_hex, torpedoes, match_stats,
                        player, weapon_type=WeaponType.TORPEDOES):
        self._asset_loader.play_sound("torpedo")
        color = self._get_torpedo_color(who)
        stats = WEAPON_STATS[weapon_type]
        damage = stats["damage_per_hit"](who.weapon_power)
        damage *= self._get_ambush_multiplier(who)
        speed = stats.get("speed", 3.0)

        where = HexGrid.hex_to_coords(*target_hex)
        where = where[0] + 4, where[1] + 4
        if who == player:
            match_stats[player]["torpedoes shot"] += 1
        torp = Torpedo(
            (int(who.pos[0]) + 4, int(who.pos[1]) + 4),
            where, who, damage, color,
        )
        if speed != 3.0:
            dist = math.hypot(torp.dx, torp.dy)
            if dist > 0:
                torp.dx = (torp.dx / dist) * speed
                torp.dy = (torp.dy / dist) * speed
        if weapon_type == WeaponType.HE_TORPEDO:
            torp.he_torpedo = True
            torp.arm_distance = stats.get("arm_distance", 2)
            torp.aoe_radius = stats.get("aoe_radius", 1)
            torp.origin_hex = HexGrid.coords_to_hex(who.pos)
            torp.traveled = 0
        torpedoes.append(torp)

    def fire_torpedo(self, who, target_hex, torpedoes, match_stats, player):
        self.fire_projectile(who, target_hex, torpedoes, match_stats,
                             player, WeaponType.TORPEDOES)

    def place_mine(self, who, target_hex, mines):
        pos = HexGrid.hex_to_coords(*target_hex)
        pos = pos[0] + 4, pos[1] + 4
        damage = WEAPON_STATS[WeaponType.MINES]["damage_per_hit"](who.weapon_power)
        damage *= self._get_ambush_multiplier(who)
        mine = Mine(pos, who, damage)
        mines.append(mine)

    def update_torpedoes(self, torpedoes, ships, match_stats, team_game, player):
        for torp in torpedoes[:]:
            if not torp.active:
                continue
            torp.advance()
            is_he = getattr(torp, 'he_torpedo', False)
            if is_he:
                torp.traveled = getattr(torp, 'traveled', 0) + 1

            hit = False
            for target in ships:
                if target == torp.firer:
                    continue
                tmask = target.mask
                offset = (int(torp.rect.left - target.pos[0]),
                          int(torp.rect.top - target.pos[1]))
                if tmask.overlap(torp.mask, offset):
                    if is_he and torp.traveled < torp.arm_distance * 10:
                        continue
                    self._asset_loader.play_sound("hit")
                    if is_he:
                        self._detonate_he(torp, ships, match_stats,
                                          team_game, player)
                    else:
                        if torp.firer == player:
                            match_stats[player]["torpedoes hit"] += 1
                        was_dead = target.is_dead()
                        target.apply_damage(torp.power)
                        if torp.firer == player and target.is_dead() and not was_dead:
                            match_stats[player]["kills-" + target.type] += 1
                        if team_game and torp.firer.type == target.type:
                            match_stats[torp.firer]["teamdamage"] -= torp.power
                        else:
                            match_stats[torp.firer]["damage"] += torp.power
                    torp.deactivate()
                    if torp in torpedoes:
                        torpedoes.remove(torp)
                    hit = True
                    break
            if not hit:
                for other in torpedoes:
                    if other == torp or not other.active:
                        continue
                    if torp.rect.colliderect(other.rect):
                        self._asset_loader.play_sound("hit")
                        other.deactivate()
                        if other in torpedoes:
                            torpedoes.remove(other)
                        torp.deactivate()
                        if torp in torpedoes:
                            torpedoes.remove(torp)
                        hit = True
                        break
            if not hit and torp.is_off_screen():
                torp.deactivate()
                if torp in torpedoes:
                    torpedoes.remove(torp)

    def update_mines(self, mines, ships, match_stats, team_game, player,
                     asset_loader):
        for mine in mines[:]:
            if not mine.active:
                continue
            for target in ships:
                if target == mine.firer:
                    continue
                offset = (int(mine.rect.left - target.pos[0]),
                          int(mine.rect.top - target.pos[1]))
                if target.mask.overlap(mine.mask, offset):
                    asset_loader.play_sound("explode")
                    was_dead = target.is_dead()
                    target.apply_damage(mine.power)
                    if mine.firer == player and target.is_dead() and not was_dead:
                        match_stats[player]["kills-" + target.type] += 1
                    if team_game and mine.firer.type == target.type:
                        match_stats[mine.firer]["teamdamage"] -= mine.power
                    else:
                        match_stats[mine.firer]["damage"] += mine.power
                    mine.detonate()
                    mines.remove(mine)
                    break

    def _detonate_he(self, torp, ships, match_stats, team_game, player):
        torp_hex = HexGrid.coords_to_hex(torp.pos)
        if torp_hex is None:
            return
        radius = getattr(torp, 'aoe_radius', 1)
        for target in ships:
            thex = HexGrid.coords_to_hex(target.pos)
            if HexGrid.hex_distance(torp_hex, thex) <= radius:
                was_dead = target.is_dead()
                target.apply_damage(torp.power)
                if torp.firer == player and target.is_dead() and not was_dead:
                    match_stats[player]["kills-" + target.type] += 1
                if team_game and torp.firer.type == target.type:
                    match_stats[torp.firer]["teamdamage"] -= torp.power
                else:
                    match_stats[torp.firer]["damage"] += torp.power
