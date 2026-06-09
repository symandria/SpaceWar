import pygame

from spacewar.rendering.hex_grid import HexGrid
from spacewar.states.state_machine import GameState, StateID


class BattleIdleState(GameState):
    def handle_event(self, event):
        g = self.game
        b = g.battle

        if event.type == pygame.KEYDOWN:
            if b.player and event.key == pygame.K_m:
                b.selected = b.player
                return StateID.DESTINATION_SELECT
            elif b.player and event.key == pygame.K_w:
                if not b.player.action:
                    b.player.action = "weapon_1"
                b.selected = b.player
                return StateID.TARGET_SELECT
            elif b.player and event.key == pygame.K_RETURN:
                b.selected = b.player
                return StateID.COMMAND_ENTRY

        if event.type != pygame.MOUSEBUTTONUP:
            return None

        if g.message_box:
            g.message_box = None
            return None
        if g.selection_list:
            for button in g.selection_list:
                if button.rect.collidepoint(event.pos):
                    g.selection_list = button.callback()
                    return None
            return None
        screen_pos = (event.pos[0] // g.settings.window_multiplier,
                      event.pos[1] // g.settings.window_multiplier)
        world_pos = g.viewport.screen_to_world(screen_pos)
        thex = HexGrid.coords_to_hex(world_pos)
        if not thex:
            return None
        if b.player and thex == HexGrid.coords_to_hex(b.player.pos):
            if event.button == 1:
                b.selected = b.player
                return StateID.COMMAND_ENTRY
            else:
                b.selected = b.player
                b.info_target = b.player
        else:
            for ship in b.ships:
                if ship == b.player:
                    continue
                if thex == HexGrid.coords_to_hex(ship.pos) and \
                        (not ship.cloaked or not b.player or
                         (b.team_game and ship.type == b.player.type)):
                    if b.selected == ship:
                        b.selected = None
                        b.info_target = None
                    else:
                        b.selected = ship
                        b.info_target = ship
                    break
        return None

    def update(self):
        return None

    def render(self):
        self.game.render_battle()


class CommandEntryState(GameState):
    def enter(self):
        g = self.game
        g.command_box.update(g.battle.player)

    def handle_event(self, event):
        g = self.game
        b = g.battle

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                return StateID.DESTINATION_SELECT
            elif event.key == pygame.K_w:
                if not b.player.action:
                    b.player.action = "weapon_1"
                return StateID.TARGET_SELECT

        if event.type != pygame.MOUSEBUTTONUP:
            return None

        if g.message_box:
            g.message_box = None
            return None
        if g.selection_list:
            for button in g.selection_list:
                if button.rect.collidepoint(event.pos):
                    result = button.callback()
                    g.selection_list = result
                    return None
            return None
        cb = g.command_box
        if cb.cancel_button_rect.collidepoint(event.pos):
            b.selected = None
            return StateID.BATTLE_IDLE
        elif cb.okay_button_rect.collidepoint(event.pos):
            player = b.player
            if not player.movement:
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    g.text_manager.load("no-destination"), g.infofont,
                    g.display.get_width(), g.settings.foreground, g.settings.background)
            elif not player.get_valid_destination(
                    player.movement[0], player.movement[1], bool(player.action)) and \
                    not player.loadout.has_special("teleportation"):
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    g.text_manager.load("invalid-destination"), g.infofont,
                    g.display.get_width(), g.settings.foreground, g.settings.background)
            elif player.action and player.action not in ("self-destruct", "regen_shields", "power_shields") and not player.target:
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    g.text_manager.load("no-target"), g.infofont,
                    g.display.get_width(), g.settings.foreground, g.settings.background)
            else:
                b.selected = None
                g.turn_resolver.begin_turn(b, g.theme_loader.ships)
                return StateID.TURN_RESOLUTION
        elif cb.move_button_rect.collidepoint(event.pos):
            return StateID.DESTINATION_SELECT
        elif cb.act_button_rect.collidepoint(event.pos) and \
                b.player.action in ("phaser", "torpedo", "weapon_1", "weapon_2"):
            return StateID.TARGET_SELECT
        elif cb.action_info_rect.collidepoint(event.pos):
            def action_callback(action):
                def callback():
                    b.player.action = action
                return callback
            w1 = b.player.loadout.get_weapon(1)
            w2 = b.player.loadout.get_weapon(2)
            w1_name = w1.get("weapon_type", "lazers") if w1 else "lazers"
            w2_name = w2.get("weapon_type", "torpedoes") if w2 else "torpedoes"
            buttons = [
                (g.text_manager.load("do nothing"), action_callback(None)),
                (w1_name.replace("_", " ").title(), action_callback("weapon_1")),
                (w2_name.replace("_", " ").title(), action_callback("weapon_2")),
                ("Regen Shields", action_callback("regen_shields")),
            ]
            if b.player.active_dr > 0:
                buttons.append(("Power to Shields", action_callback("power_shields")))
            buttons.append(
                (g.text_manager.load("self-destruct"),
                 action_callback("self-destruct")),
            )
            g.selection_list = g.make_selection_list(
                g.text_manager.load("choose-action"), *buttons)
        return None

    def update(self):
        return None

    def render(self):
        g = self.game
        g.render_battle()
        g.command_box.update(g.battle.player)
        g.command_box.render(g.battle.player.action)


class DestinationSelectState(GameState):
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP:
            return None
        g = self.game
        screen_pos = (event.pos[0] // g.settings.window_multiplier,
                      event.pos[1] // g.settings.window_multiplier)
        world_pos = g.viewport.screen_to_world(screen_pos)
        thex = HexGrid.coords_to_hex(world_pos)
        if thex:
            g.battle.player.movement = thex
            return StateID.COMMAND_ENTRY
        return None

    def update(self):
        return None

    def render(self):
        g = self.game
        g.render_battle(show_invalid_destinations=True)


class TargetSelectState(GameState):
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP:
            return None
        g = self.game
        screen_pos = (event.pos[0] // g.settings.window_multiplier,
                      event.pos[1] // g.settings.window_multiplier)
        world_pos = g.viewport.screen_to_world(screen_pos)
        thex = HexGrid.coords_to_hex(world_pos)
        if thex:
            g.battle.player.target = thex
            return StateID.COMMAND_ENTRY
        return None

    def update(self):
        return None

    def render(self):
        self.game.render_battle()
