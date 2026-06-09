from spacewar.rendering.hex_grid import HexGrid


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

        self.move_time = 0
        self.dying = []
        self.phaser_hit_this_turn = False

    @property
    def is_active(self):
        return self.move_time != 0

    def begin_turn(self, battle, sprite_lookup):
        self._ai.decide_actions(battle.ships, battle.player, battle.team_game)
        self.move_time = 90
        self.dying = []
        self.phaser_hit_this_turn = False

        self._teleportation.setup(battle.ships, sprite_lookup)

        for ship in battle.ships:
            if not ship.teleport_target:
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
                if ship.action == "torpedo":
                    self._combat.fire_torpedo(
                        ship, ship.target, battle.torpedoes,
                        battle.match_stats, battle.player)
        elif self.move_time == 80:
            self._teleportation.snap_positions(battle.ships)
        elif self.move_time == 70:
            self._teleportation.clear_flags(battle.ships)
        elif self._is_phaser_frame():
            if self.move_time == 63:
                self.phaser_hit_this_turn = False
            step = (self.move_time // 9) - 3
            for ship in battle.ships:
                if ship.action == "phaser":
                    phaser_data, self.phaser_hit_this_turn = \
                        self._combat.fire_phaser(
                            ship, ship.target, step,
                            battle.ships, battle.torpedoes,
                            battle.match_stats, battle.team_game,
                            battle.player, self.phaser_hit_this_turn)
                    draw_phasers.append(phaser_data)
        elif self.move_time == 1:
            for ship in battle.ships:
                if ship.action == "self-destruct":
                    ship.hull = -1

        if self.move_time > 0:
            self._combat.update_torpedoes(
                battle.torpedoes, battle.ships,
                battle.match_stats, battle.team_game, battle.player)

        self.move_time -= 1

        if self.move_time == 0:
            self._collision.reset()
            self._regeneration.apply_end_of_turn(battle.ships)
            self.dying = self._death.detect_and_cascade(
                battle.ships, battle.match_stats, battle.team_game)
            if self.dying:
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

    def _is_phaser_frame(self):
        return (self.move_time % 9 == 0 and
                3 <= self.move_time // 9 <= 7)
