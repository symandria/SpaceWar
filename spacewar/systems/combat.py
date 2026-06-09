import math

import pygame

from spacewar.entities.ship import Ship
from spacewar.entities.torpedo import Torpedo
from spacewar.rendering.hex_grid import HexGrid


class CombatSystem:
    def __init__(self, asset_loader, theme_loader):
        self._asset_loader = asset_loader
        self._theme_loader = theme_loader

    def fire_phaser(self, who, target_hex, step, ships, torpedoes,
                    match_stats, team_game, player, phaser_hit_this_turn):
        self._asset_loader.play_sound("phaser")
        races = self._theme_loader.active_races
        if who.type in races:
            color = self._theme_loader.get_phaser_color(who.type)
        else:
            color = self._theme_loader.get_phaser_color("sentry")
        if isinstance(color[0], (list, tuple)):
            color = color[step]

        where = HexGrid.hex_to_coords(*target_hex)
        where = where[0] + 4, where[1] + 4
        origin = int(who.pos[0]) + 4, int(who.pos[1]) + 4
        dx, dy = where[0] - origin[0], where[1] - origin[1]
        if abs(dx) <= 0.01 and abs(dy) <= 0.01:
            dx = 100
        while 0 < where[0] < 160 and 0 < where[1] < 160:
            where = where[0] + dx, where[1] + dy

        temp = pygame.surface.Surface((160, 160))
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
                before = what.shields
                damage_multiplier = 1
                if "ambush" in who.specials and who.was_cloaked:
                    damage_multiplier = 3
                    if not who.cloaked:
                        who.was_cloaked = False
                if "phaser_focus" in who.specials:
                    damage_multiplier *= 2
                what.apply_damage((who.phasers // 3) * damage_multiplier)
                if who == player and what.shields < 0 and before >= 0:
                    match_stats[player]["kills-" + what.type] += 1
                damage = before - what.shields
                if team_game and who.type == what.type:
                    match_stats[who]["teamdamage"] -= damage
                else:
                    match_stats[who]["damage"] += damage
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

    def fire_torpedo(self, who, target_hex, torpedoes, match_stats, player):
        self._asset_loader.play_sound("torpedo")
        races = self._theme_loader.active_races
        if who.type in races:
            color = self._theme_loader.get_torpedo_color(who.type)
        else:
            color = self._theme_loader.get_torpedo_color("sentry")
        where = HexGrid.hex_to_coords(*target_hex)
        where = where[0] + 4, where[1] + 4
        if who == player:
            match_stats[player]["torpedoes shot"] += 1
        damage_multiplier = 1
        if "ambush" in who.specials and who.was_cloaked:
            damage_multiplier = 3
            if not who.cloaked:
                who.was_cloaked = False
        torpedoes.append(Torpedo(
            (int(who.pos[0]) + 4, int(who.pos[1]) + 4),
            where, who, who.torpedoes * damage_multiplier, color,
        ))

    def update_torpedoes(self, torpedoes, ships, match_stats, team_game, player):
        for torp in torpedoes[:]:
            if not torp.active:
                continue
            torp.advance()
            hit = False
            for target in ships:
                if target == torp.firer:
                    continue
                tmask = target.mask
                offset = (int(torp.rect.left - target.pos[0]),
                          int(torp.rect.top - target.pos[1]))
                if tmask.overlap(torp.mask, offset):
                    self._asset_loader.play_sound("hit")
                    if torp.firer == player:
                        match_stats[player]["torpedoes hit"] += 1
                    before = target.shields
                    target.apply_damage(torp.power)
                    if torp.firer == player and target.shields < 0 and before >= 0:
                        match_stats[player]["kills-" + target.type] += 1
                    damage = before - target.shields
                    if team_game and torp.firer.type == target.type:
                        match_stats[torp.firer]["teamdamage"] -= damage
                    else:
                        match_stats[torp.firer]["damage"] += damage
                    torp.deactivate()
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
