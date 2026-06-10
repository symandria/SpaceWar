import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
pygame.display.init()
pygame.display.set_mode((160, 160))
pygame.font.init()

import pytest
from spacewar.entities.ship import Ship
from spacewar.rendering.hex_grid import HexGrid
from spacewar.components.base import Component, ComponentSlot
from spacewar.components.defaults import build_default_loadout
from spacewar.components.ship_loadout import ShipLoadout


@pytest.fixture(autouse=True)
def reset_map_size():
    """Battles can resize the global hex board; keep every test on
    the default 2x2 board unless it resizes explicitly."""
    from spacewar.config import constants
    constants.set_map_size(2, 2)
    yield
    constants.set_map_size(2, 2)


@pytest.fixture
def default_ship():
    ship = Ship('test', HexGrid.hex_to_coords(7, 5), 180,
                'cadet', 'Captain', 'TestShip',
                100, 10, 5, specials=[], human=True, pixel_perfect=False)
    return ship


@pytest.fixture
def cloaking_ship():
    ship = Ship('klingon', HexGrid.hex_to_coords(7, 5), 180,
                'cadet', 'Captain', 'CloakShip',
                100, 10, 5, specials=['cloaking'], pixel_perfect=False)
    return ship


@pytest.fixture
def teleport_ship():
    ship = Ship('borg', HexGrid.hex_to_coords(7, 5), 180,
                'cadet', 'Captain', 'BorgShip',
                100, 10, 5, specials=['teleportation', 'regeneration'],
                pixel_perfect=False)
    return ship


@pytest.fixture
def ablative_ship():
    ship = Ship('federation', HexGrid.hex_to_coords(7, 5), 180,
                'cadet', 'Captain', 'FedShip',
                100, 10, 5, specials=['ablative'], pixel_perfect=False)
    return ship


@pytest.fixture
def default_loadout():
    return build_default_loadout()
