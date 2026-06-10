from spacewar.rendering.hex_grid import HexGrid
from spacewar.systems.harvest import HarvestSystem
from spacewar.systems.map_effects import MapEffectsSystem
from spacewar.systems.weapons import WeaponType


class TurnResolver:
    def __init__(self, movement, collision, combat, ai, teleportation,
                 cloaking, regeneration, death, scoring, asset_loader):
        self._movement = movement
        self._collision = collision
        self._combat = combat
        self._ai = ai
        self._teleportation = teleportation
        self._cloaking = cloaking
        self._regeneration = regeneration
        self._death = death
        self._scoring = scoring
        self._asset_loader = asset_loader
        self._map_effects = MapEffectsSystem()
        self._harvest = HarvestSystem()

        self.move_time = 0
        self.dying = []
        self.phaser_hit_this_turn = False
        self.shockwave_frame = 0

    @property
    def is_active(self):
        return self.move_time != 0

    def _get_weapon_type(self, ship):
        return self._combat._get_weapon_type(ship, ship.action)

    def _is_weapon_action(self, action):
        return action in ("weapon_1", "weapon_2")

    def begin_turn(self, battle, sprite_lookup):
        self._sprite_lookup = sprite_lookup
        battle.turn_count = getattr(battle, 'turn_count', 0) + 1
        self._ai.decide_actions(battle.ships, battle.player,
                                battle.team_game, battle)
        self.move_time = 90
        self.dying = []
        self.phaser_hit_this_turn = False
        self.shockwave_frame = 0

        self._teleportation.setup(battle.ships, sprite_lookup)

        for ship in battle.ships:
            ship.turn_start_hex = HexGrid.coords_to_hex(ship.pos)
            if not ship.teleport_target:
                if ship.move_target:
                    dx = ship.pos[0] - ship.move_target[0]
                    dy = ship.pos[1] - ship.move_target[1]
                    if dx or dy:
                        if dx < 0 and dx < -abs(dy):
                            ship.rotate(270, sprite_lookup)
                        elif dx > 0 and dx > abs(dy):
                            ship.rotate(90, sprite_lookup)
                        elif dy > 0:
                            ship.rotate(0, sprite_lookup)
                        else:
                            ship.rotate(180, sprite_lookup)

            self._regeneration.setup_regen_flag(ship)

        self._cloaking.apply(battle.ships, sprite_lookup)

    def tick(self, battle):
        draw_phasers = []

        if self.move_time > 0:
            self._movement.update(battle.ships, self.move_time)
            self._collision.update(
                battle.ships, battle.match_stats, battle.team_game,
                battle.player, self._asset_loader)

        if self.move_time == 90:
            self._teleportation.play_sound_if_needed(
                battle.ships, self._asset_loader)

        elif self.move_time == 85:
            for ship in battle.ships:
                if not self._is_weapon_action(ship.action):
                    continue
                wtype = self._get_weapon_type(ship)
                if wtype in (WeaponType.TORPEDOES, WeaponType.HE_TORPEDO):
                    self._combat.fire_projectile(
                        ship, ship.target, battle.torpedoes,
                        battle.match_stats, battle.player, wtype)

        elif self.move_time == 80:
            self._teleportation.snap_positions(battle.ships)
            for ship in battle.ships:
                if ship.teleport_target:
                    # Teleporters don't traverse the hexes in between.
                    ship.turn_start_hex = None

        elif self.move_time == 70:
            self._teleportation.clear_flags(battle.ships)

        elif self._is_phaser_frame():
            if self.move_time == 63:
                self.phaser_hit_this_turn = False
            step = (self.move_time // 9) - 3
            for ship in battle.ships:
                if not self._is_weapon_action(ship.action):
                    continue
                wtype = self._get_weapon_type(ship)
                if wtype == WeaponType.LAZERS:
                    phaser_data, self.phaser_hit_this_turn = \
                        self._combat.fire_hitscan(
                            ship, ship.target, step,
                            battle.ships, battle.torpedoes,
                            battle.match_stats, battle.team_game,
                            battle.player, self.phaser_hit_this_turn,
                            WeaponType.LAZERS)
                    if phaser_data:
                        draw_phasers.append(phaser_data)

        elif self.move_time == 20:
            for ship in battle.ships:
                if not self._is_weapon_action(ship.action):
                    continue
                wtype = self._get_weapon_type(ship)
                if wtype == WeaponType.SHOCKWAVE:
                    self._combat.fire_shockwave(
                        ship, battle.ships, battle.match_stats,
                        battle.team_game, battle.player)
                    self.shockwave_frame = 10
                elif wtype == WeaponType.POINT_LAZERS:
                    phaser_data, _ = self._combat.fire_point_lazers(
                        ship, ship.target, battle.ships,
                        battle.match_stats, battle.team_game,
                        battle.player)
                    if phaser_data:
                        draw_phasers.append(phaser_data)

        elif self.move_time == 15:
            for ship in battle.ships:
                if ship.action == "tractor_beam" and ship.target:
                    self._harvest.process(ship, battle, self._asset_loader)

        elif self.move_time == 1:
            for ship in battle.ships:
                if ship.action == "self-destruct":
                    ship.hull = -1
                elif ship.action == "regen_shields":
                    regen_amount = int(ship.weapon_power * ship.active_regen_mult)
                    ship.shields = min(ship.shields + regen_amount, ship.max_shields)

            for ship in battle.ships:
                if self._is_weapon_action(ship.action):
                    wtype = self._get_weapon_type(ship)
                    if wtype == WeaponType.MINES and ship.target:
                        self._combat.place_mine(
                            ship, ship.target, battle.mines)

        if self.move_time in (85, 78, 71):
            # Disruptors: three volleys of paired bolts.
            for ship in battle.ships:
                if not self._is_weapon_action(ship.action):
                    continue
                wtype = self._get_weapon_type(ship)
                if wtype == WeaponType.DISRUPTORS and ship.target:
                    self._combat.fire_disruptor_volley(
                        ship, ship.target, battle.torpedoes,
                        battle.match_stats, battle.player)

        if self.move_time > 0:
            self._combat.update_torpedoes(
                battle.torpedoes, battle.ships,
                battle.match_stats, battle.team_game, battle.player)
            if battle.mines:
                self._combat.update_mines(
                    battle.mines, battle.ships, battle.match_stats,
                    battle.team_game, battle.player, self._asset_loader)

        if self.shockwave_frame > 0:
            self.shockwave_frame -= 1

        self.move_time -= 1

        if self.move_time == 0:
            self._collision.reset()
            self._movement.reset()
            self._regeneration.apply_end_of_turn(battle.ships)
            self._apply_nebula_effects(battle)
            self._teleportation.tick_cooldowns(battle.ships)
            self._process_miners(battle)
            for ship in battle.ships:
                if ship.phasing_cooldown > 0:
                    ship.phasing_cooldown -= 1
                ship.phasing_active = False
                ship.phasing_remaining = 0
                # Neutral shops retaliate once fired upon.
                if getattr(ship, 'is_shop', False) and ship.shot_recently:
                    ship.hostile = True
                # Provoking one colonial provokes the whole guild.
                if getattr(ship, 'neutral', False) and ship.shot_recently \
                        and not getattr(ship, 'hostile', False):
                    faction = getattr(ship, 'faction', None)
                    for s in battle.ships:
                        if getattr(s, 'faction', None) == faction:
                            s.hostile = True
                            s.aggro = True
            self.dying = self._death.detect_and_cascade(
                battle.ships, battle.match_stats, battle.team_game)
            for ship in battle.ships:
                ship.movement = None
                ship.action = None
                ship.target = None
            if self.dying:
                self._death.create_wrecks(self.dying, battle.wrecks)
                self.move_time = -1
                self._asset_loader.play_sound("explode")
            else:
                for ship in battle.ships:
                    if ship.shot_recently:
                        ship.shot_recently = 0

        if -10 <= self.move_time < 0:
            self._death.animate_explosion(self.dying, self.move_time)
        elif self.move_time == -11:
            removed_player = self._death.remove_dead(
                self.dying, battle.ships, battle.dead_ships, battle.player)
            if removed_player:
                battle.player = None
            self.move_time = 0
            for ship in battle.ships:
                if ship.shot_recently:
                    ship.shot_recently -= 1

        return draw_phasers

    def _process_miners(self, battle):
        """Mining ships parked beside a resource asteroid strip it into
        their cargo hold at the end of the turn."""
        for ship in battle.ships:
            if not getattr(ship, 'is_miner', False) or ship.is_dead():
                continue
            mhex = HexGrid.coords_to_hex(ship.pos)
            if mhex is None:
                continue
            for ast in battle.asteroids:
                if not ast.resource or ast.is_dead():
                    continue
                if HexGrid.hex_distance(mhex, ast.hex_pos) > 1:
                    continue
                kind, amount = ast.resource
                cargo = getattr(ship, 'cargo', None)
                if cargo is None:
                    cargo = ship.cargo = {"scrap": 0, "materials": {}}
                if kind == "scrap":
                    cargo["scrap"] += amount
                else:
                    cargo["materials"][kind] = \
                        cargo["materials"].get(kind, 0) + amount
                ast.resource = None
                break

    def _apply_nebula_effects(self, battle):
        self._apply_zone_effects(battle)
        nebulae_by_hex = getattr(battle, 'nebulae_by_hex', None)
        if not nebulae_by_hex:
            return
        sprites = getattr(self, '_sprite_lookup', None)
        for ship in battle.ships:
            start = getattr(ship, 'turn_start_hex', None)
            end = HexGrid.coords_to_hex(ship.pos)
            if start is not None and end is not None and start != end:
                traversed = self._movement.get_hexes_traversed(ship, start, end)
                self._map_effects.apply_movement_effects(
                    ship, [h for h in traversed if h != end], nebulae_by_hex)
            self._map_effects.apply_end_of_turn_effects(
                ship, nebulae_by_hex, sprites)
        self._map_effects.apply_gravity(battle)

    def _apply_zone_effects(self, battle):
        """Map-wide environmental events, independent of nebula tiles."""
        effect = getattr(battle, 'zone_effect', None)
        if effect == "solar_flare":
            # A flare erupts every other turn, battering every ship's
            # shields; an unshielded hull takes the burn directly.
            if getattr(battle, 'turn_count', 0) % 2 == 1:
                for ship in battle.ships:
                    if ship.shields > 0:
                        ship.shields = max(
                            0, ship.shields - int(ship.max_shields * 0.15))
                    else:
                        ship.hull -= max(1, int(ship.max_hull * 0.03))

    def _is_phaser_frame(self):
        return (self.move_time % 9 == 0 and
                3 <= self.move_time // 9 <= 7)
