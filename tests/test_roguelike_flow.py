"""End-to-end roguelike flow test driving the real Game object headlessly.

Walks the actual state machine with synthetic mouse events: main menu ->
race -> sector map -> battles / shops / events across all three tiers ->
victory -> main menu. Catches integration bugs (missing ship images,
KeyErrors on race lookups, stale menus, soft-locks) that unit tests
cannot see.
"""
import random

import pygame
import pytest

from spacewar.roguelike.encounters import NodeType
from spacewar.states.state_machine import StateID
from spacewar.ui.selection_list import SelectionButton


@pytest.fixture(autouse=True)
def _remember_button_text(monkeypatch):
    orig = SelectionButton.__init__

    def patched(self, text, callback, font, foreground, background):
        orig(self, text, callback, font, foreground, background)
        self.text = text

    monkeypatch.setattr(SelectionButton, "__init__", patched)


def _click_button(game, index=None, text_contains=None):
    game.state_machine.render()  # positions button rects
    buttons = list(game.selection_list)
    if text_contains is not None:
        button = next(b for b in buttons if text_contains in b.text)
    else:
        button = buttons[index]
    event = pygame.event.Event(
        pygame.MOUSEBUTTONUP, pos=button.rect.center, button=1)
    game.state_machine.handle_event(event)


def _dismiss(game):
    event = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(0, 0), button=1)
    game.state_machine.handle_event(event)


def _force_win_battle(game):
    sm = game.state_machine
    b = game.battle

    # Every combatant must come from the active (classic) theme and be
    # fully drawable with faction data.
    for ship in b.ships:
        assert ship.type in game.theme_loader.active_races, \
            f"off-theme race {ship.type!r} in battle"
        assert ship.image is not None, f"no sprite for race {ship.type!r}"
        assert game.theme_loader.get_phaser_color(ship.type) is not None
        assert game.theme_loader.get_torpedo_color(ship.type) is not None

    sm.render()  # battle screen (HUD, minimap, fog) must not crash

    for ship in b.ships:
        if ship is not b.player:
            ship.shields = 0
            ship.hull = -1

    game.turn_resolver.begin_turn(b, game.theme_loader.ships)
    sm.transition_to(StateID.TURN_RESOLUTION)
    for tick in range(5000):
        sm.update()
        if tick % 50 == 0:
            sm.render()
        if sm.current_id != StateID.TURN_RESOLUTION:
            break
    assert sm.current_id == StateID.GAME_OVER

    _dismiss(game)  # clear after-battle report
    _dismiss(game)  # apply run results -> back to sector map
    assert sm.current_id == StateID.ROGUELIKE_MAP


def _handle_node(game, node_type):
    sm = game.state_machine
    if node_type in (NodeType.BATTLE, NodeType.ELITE, NodeType.BOSS):
        assert sm.current_id == StateID.BATTLE_IDLE
        assert game.selection_list is None, "sector menu leaked into battle"
        _force_win_battle(game)
    elif node_type == NodeType.SHOP:
        assert sm.current_id == StateID.ROGUELIKE_MAP
        _click_button(game, text_contains="Leave Shop")
        assert sm.current_id == StateID.ROGUELIKE_MAP
    elif node_type in (NodeType.SALVAGE, NodeType.REST):
        assert game.message_box is not None
        _dismiss(game)
    elif node_type == NodeType.EVENT:
        _click_button(game, index=-1)  # always the safe "decline" choice
        assert sm.current_id == StateID.ROGUELIKE_MAP


def test_full_roguelike_run():
    random.seed(20260609)
    from spacewar.game import Game
    game = Game()
    sm = game.state_machine

    assert sm.current_id == StateID.MAIN_MENU
    # Roguelike goes straight to race selection -- classic is the only
    # real theme, so there is no theme menu.
    _click_button(game, text_contains="Roguelike")
    assert game.theme_loader.active_theme == "classic"
    _click_button(game, index=0)  # race
    assert sm.current_id == StateID.ROGUELIKE_MAP
    run = game.active_run
    assert run is not None and run.alive
    assert run.race in game.theme_loader.active_races

    for safety in range(300):
        if game.active_run is None or game.active_run.victory:
            break
        if game.message_box:
            _dismiss(game)
            continue
        assert sm.current_id == StateID.ROGUELIKE_MAP
        available = run.sector_map.get_available_nodes()
        assert available, "player stranded with no reachable nodes"
        node = available[0]
        _click_button(game, index=0)
        _handle_node(game, node.node_type)
    else:
        pytest.fail("run never finished within safety limit")

    assert run.victory
    assert run.current_tier == 3
    assert run.battles_won >= 3  # at least one boss per tier
    assert run.alive

    # Victory message -> back to a working main menu.
    _dismiss(game)
    assert sm.current_id == StateID.MAIN_MENU
    assert game.active_run is None
    assert game.selection_list is not None
    sm.render()


def test_roguelike_menus_and_shop_purchase():
    random.seed(99)
    from spacewar.game import Game
    game = Game()
    sm = game.state_machine

    _click_button(game, text_contains="Roguelike")
    _click_button(game, index=0)
    run = game.active_run
    assert run is not None

    # Ship overview, inventory and upgrades menus all open and return.
    _click_button(game, text_contains="Ship")
    assert game.selection_list is not None
    _click_button(game, text_contains="Back")
    assert sm.current_id == StateID.ROGUELIKE_MAP

    _click_button(game, text_contains="Inventory")
    _click_button(game, text_contains="Back")
    assert sm.current_id == StateID.ROGUELIKE_MAP

    _click_button(game, text_contains="Upgrades")
    _click_button(game, text_contains="Back")
    assert sm.current_id == StateID.ROGUELIKE_MAP

    # Abandon flow: confirm "No" first, then actually abandon.
    _click_button(game, text_contains="Abandon Run")
    _click_button(game, text_contains="No, continue")
    assert sm.current_id == StateID.ROGUELIKE_MAP
    assert game.active_run is run

    _click_button(game, text_contains="Abandon Run")
    _click_button(game, text_contains="Yes, abandon")
    assert sm.current_id == StateID.MAIN_MENU
    assert game.active_run is None
    assert game.selection_list is not None
