import pygame

from spacewar.rendering.hex_grid import HexGrid
from spacewar.states.state_machine import GameState, StateID


def _hotkey_action(game, event_key):
    """Map battle hotkeys to actions. Returns (handled, next_state)."""
    b = game.battle
    player = b.player
    if not player:
        return False, None
    if event_key == pygame.K_1 and player.loadout.get_weapon(1):
        player.action = "weapon_1"
        b.selected = player
        return True, StateID.TARGET_SELECT
    if event_key == pygame.K_2 and player.loadout.get_weapon(2):
        player.action = "weapon_2"
        b.selected = player
        return True, StateID.TARGET_SELECT
    if event_key == pygame.K_c and player.active_cloak:
        player.action = None if player.action == "cloak" else "cloak"
        return True, None
    if event_key == pygame.K_t and player.loadout.has_tractor():
        player.action = "tractor_beam"
        b.selected = player
        return True, StateID.TARGET_SELECT
    if event_key == pygame.K_r:
        player.action = None if player.action == "regen_shields" \
            else "regen_shields"
        return True, None
    if event_key == pygame.K_p and player.active_dr > 0:
        player.action = None if player.action == "power_shields" \
            else "power_shields"
        return True, None
    return False, None


def _hud_click(game, pos):
    """Apply a click on a HUD action row. Returns (handled, next_state)."""
    action_id = game.battle_hud.hit_test(pos)
    if action_id is None:
        return False, None
    b = game.battle
    player = b.player
    if not player:
        return True, None
    if action_id in ("weapon_1", "weapon_2", "tractor_beam"):
        player.action = action_id
        b.selected = player
        return True, StateID.TARGET_SELECT
    player.action = None if player.action == action_id else action_id
    return True, None


def _stellar_description(game, battle, thex):
    """Description of the stellar object at a hex, if the player's
    sensors can currently see it."""
    player = battle.player
    if not player:
        return None
    clear, shaded = game.visibility_system.compute_visibility(player)
    if thex not in clear and thex not in shaded:
        return None

    from spacewar.entities.map_object import (
        NEBULA_DESCRIPTIONS, OBJECT_DESCRIPTIONS,
    )
    for anomaly in getattr(battle, 'anomalies', ()):
        if anomaly.hex_pos == thex and not anomaly.looted:
            return OBJECT_DESCRIPTIONS["anomaly"]
    for mine in battle.mines:
        if mine.active and mine.hex_pos == thex:
            return OBJECT_DESCRIPTIONS["mine"]
    for wreck in battle.wrecks:
        if wreck.hex_pos == thex and not wreck.salvaged:
            return OBJECT_DESCRIPTIONS["wreck"]
    for ast in battle.asteroids:
        if ast.hex_pos == thex and not ast.is_dead():
            return OBJECT_DESCRIPTIONS["asteroid"]
    neb = battle.nebulae_by_hex.get(thex)
    if neb is not None:
        return NEBULA_DESCRIPTIONS.get(neb.nebula_type)
    return None


def _open_battle_shop(game, shop):
    """Neutral trading post: browse and buy without spending the turn."""
    from spacewar.ui.messagebox import Messagebox
    run = game.active_run
    if run is None:
        game.message_box = Messagebox(
            "The trading post has nothing for you.",
            game.infofont, game.display.get_width(),
            game.settings.foreground, game.settings.background)
        return

    def rebuild():
        items = shop.shop_items
        buttons = []
        for i, item in enumerate(items):
            if "component" in item:
                comp = item["component"]
                slot_name = comp.slot.value.replace("_", " ").title()
                tag = "" if run.inventory.scrap >= item["price"] else " [!]"
                buttons.append((
                    f"{comp.name} [{slot_name}] - {item['price']}s{tag}",
                    _buy(i)))
            elif item.get("type") == "material":
                tag = "" if run.inventory.scrap >= item["price"] else " [!]"
                buttons.append((
                    f"{item['amount']}x {item['material'].title()} - "
                    f"{item['price']}s{tag}",
                    _buy(i)))
            elif item.get("type") == "repair":
                buttons.append((
                    f"Full Repair - {item['price']}s", _buy(i)))
        buttons.append(("Close", lambda: None))
        return game.make_selection_list(
            f"=== Trading Post ===\nScrap: {run.inventory.scrap}", *buttons)

    def _buy(index):
        def callback():
            items = shop.shop_items
            item = items[index]
            if not run.inventory.spend_scrap(item["price"]):
                game.message_box = Messagebox(
                    "Not enough scrap!",
                    game.infofont, game.display.get_width(),
                    game.settings.foreground, game.settings.background)
                return rebuild()
            if "component" in item:
                run.inventory.add_component(item["component"])
            elif item.get("type") == "material":
                run.inventory.add_material(item["material"], item["amount"])
            elif item.get("type") == "repair":
                player = game.battle.player
                if player:
                    player.hull = player.max_hull
                    player.shields = player.max_shields
            items.pop(index)
            return rebuild()
        return callback

    game.selection_list = rebuild()


def _open_miner_trade(game, miner):
    """Mining barges sell their cargo at fair market prices when you
    pull alongside and hail them."""
    from spacewar.ui.messagebox import Messagebox
    run = game.active_run
    if run is None:
        game.message_box = Messagebox(
            "The mining barge ignores your hail.",
            game.infofont, game.display.get_width(),
            game.settings.foreground, game.settings.background)
        return

    tier = getattr(game.battle, 'tier', 1)
    prices = {"common": 10, "uncommon": 30 * tier, "rare": 150 * tier}

    def rebuild():
        cargo = getattr(miner, 'cargo', None) or {"materials": {}}
        buttons = []
        for mat, amount in cargo.get("materials", {}).items():
            if amount <= 0:
                continue
            price = prices.get(mat, 50)
            tag = "" if run.inventory.scrap >= price else " [!]"
            buttons.append((
                f"Buy 1 {mat.title()} - {price}s ({amount} held){tag}",
                _buy(mat, price)))
        if not buttons:
            buttons.append(("Hold is empty - check back later",
                            lambda: None))
        buttons.append(("Close", lambda: None))
        return game.make_selection_list(
            f"=== Mining Barge ===\nScrap: {run.inventory.scrap}",
            *buttons)

    def _buy(mat, price):
        def callback():
            cargo = miner.cargo
            if cargo["materials"].get(mat, 0) <= 0:
                return rebuild()
            if not run.inventory.spend_scrap(price):
                game.message_box = Messagebox(
                    "Not enough scrap!",
                    game.infofont, game.display.get_width(),
                    game.settings.foreground, game.settings.background)
                return rebuild()
            cargo["materials"][mat] -= 1
            run.inventory.add_material(mat, 1)
            return rebuild()
        return callback

    game.selection_list = rebuild()


class BattleIdleState(GameState):
    def enter(self):
        g = self.game
        b = g.battle
        # Reaching the right edge of the map is how you leave a
        # roguelike zone; offer the choice at the start of the turn.
        if not b or not b.player or not g.active_run:
            return
        phex = HexGrid.coords_to_hex(b.player.pos)
        if not phex:
            return
        from spacewar.config.constants import max_col
        if phex[1] < max_col(phex[0]):
            return
        config = g.roguelike_battle_config or {}
        if config.get("is_boss"):
            # No fleeing a boss arena while the boss still lives.
            hostiles = [
                s for s in b.ships
                if s != b.player and not (getattr(s, 'is_shop', False) and
                                          not getattr(s, 'hostile', False))
            ]
            if hostiles:
                return
        turn = getattr(b, 'turn_count', 0)
        if getattr(b, 'exit_prompt_turn', None) == turn:
            return
        b.exit_prompt_turn = turn

        def leave():
            g.leave_zone_requested = True
            return None

        g.selection_list = g.make_selection_list(
            "You have reached the edge of the zone.\n"
            "Would you like to leave this zone?",
            ("Leave zone", leave),
            ("Stay", lambda: None),
        )

    def update(self):
        g = self.game
        if getattr(g, 'leave_zone_requested', False):
            g.leave_zone_requested = False
            from spacewar.ui.messagebox import Messagebox
            g.message_box = Messagebox(
                "You disengage and leave the zone.",
                g.infofont, g.display.get_width(),
                g.settings.foreground, g.settings.background)
            return StateID.GAME_OVER
        return None

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
            handled, next_state = _hotkey_action(g, event.key)
            if handled:
                return next_state

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

        handled, next_state = _hud_click(g, event.pos)
        if handled:
            return next_state

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
                    if getattr(ship, 'is_shop', False) and \
                            not getattr(ship, 'hostile', False) and b.player:
                        phex = HexGrid.coords_to_hex(b.player.pos)
                        if phex and HexGrid.hex_distance(phex, thex) <= 2:
                            _open_battle_shop(g, ship)
                        else:
                            from spacewar.ui.messagebox import Messagebox
                            g.message_box = Messagebox(
                                "Move within 2 hexes to dock with the "
                                "trading post.",
                                g.infofont, g.display.get_width(),
                                g.settings.foreground, g.settings.background)
                        return None
                    if getattr(ship, 'is_miner', False) and \
                            not getattr(ship, 'hostile', False) and b.player:
                        phex = HexGrid.coords_to_hex(b.player.pos)
                        if phex and HexGrid.hex_distance(phex, thex) <= 1:
                            _open_miner_trade(g, ship)
                        else:
                            from spacewar.ui.messagebox import Messagebox
                            g.message_box = Messagebox(
                                "Move alongside the mining barge "
                                "(1 hex) to trade.",
                                g.infofont, g.display.get_width(),
                                g.settings.foreground, g.settings.background)
                        return None
                    if b.selected == ship:
                        b.selected = None
                        b.info_target = None
                    else:
                        b.selected = ship
                        b.info_target = ship
                    return None
            description = _stellar_description(g, b, thex)
            if description:
                from spacewar.ui.messagebox import Messagebox
                g.message_box = Messagebox(
                    description, g.infofont, g.display.get_width(),
                    g.settings.foreground, g.settings.background)
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
            handled, next_state = _hotkey_action(g, event.key)
            if handled:
                return next_state

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

        handled, next_state = _hud_click(g, event.pos)
        if handled:
            return next_state

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
            elif player.action and player.action not in ("self-destruct", "regen_shields", "power_shields", "cloak") and not player.target:
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
                b.player.action in ("phaser", "torpedo", "weapon_1", "weapon_2",
                                    "tractor_beam"):
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
            if b.player.active_cloak:
                cloak_label = "Decloak" if b.player.cloaked else "Cloak"
                buttons.append((cloak_label, action_callback("cloak")))
            if b.player.loadout.has_tractor():
                buttons.append(("Tractor Beam", action_callback("tractor_beam")))
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
