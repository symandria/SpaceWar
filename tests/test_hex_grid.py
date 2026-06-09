from spacewar.rendering.hex_grid import HexGrid
from spacewar.config.constants import GRID_ROWS, GRID_COLS_ODD, GRID_COLS_EVEN, max_col


class TestHexToCoords:
    def test_first_hex(self):
        x, y = HexGrid.hex_to_coords(1, 1)
        assert x == 5
        assert y == 18

    def test_even_row_offset(self):
        x1, _ = HexGrid.hex_to_coords(1, 1)
        x2, _ = HexGrid.hex_to_coords(2, 1)
        assert x2 > x1  # even rows are offset right

    def test_consistent_spacing(self):
        x1, y1 = HexGrid.hex_to_coords(1, 1)
        x2, y2 = HexGrid.hex_to_coords(1, 2)
        assert x2 - x1 == 14  # HEX_SPACING_X

    def test_vertical_spacing(self):
        _, y1 = HexGrid.hex_to_coords(1, 1)
        _, y2 = HexGrid.hex_to_coords(2, 1)
        assert y2 - y1 == 10  # HEX_SPACING_Y


class TestCoordsToHex:
    def test_roundtrip(self):
        for row in range(1, GRID_ROWS + 1):
            for col in range(1, max_col(row) + 1):
                coords = HexGrid.hex_to_coords(row, col)
                center = (coords[0] + 4, coords[1] + 4)
                result = HexGrid.coords_to_hex(center)
                assert result is not None, f"Failed at ({row},{col})"
                assert result == (row, col), \
                    f"Roundtrip failed: ({row},{col}) -> {coords} -> {result}"

    def test_out_of_bounds(self):
        assert HexGrid.coords_to_hex((0, 0)) is None
        assert HexGrid.coords_to_hex((200, 200)) is None
        assert HexGrid.coords_to_hex((-1, 50)) is None


class TestHexDistance:
    def test_same_hex(self):
        assert HexGrid.hex_distance((1, 1), (1, 1)) == 0

    def test_adjacent(self):
        assert HexGrid.hex_distance((1, 1), (1, 2)) == 1
        assert HexGrid.hex_distance((1, 1), (2, 1)) == 1

    def test_symmetric(self):
        d1 = HexGrid.hex_distance((1, 1), (5, 5))
        d2 = HexGrid.hex_distance((5, 5), (1, 1))
        assert d1 == d2

    def test_max_distance(self):
        d = HexGrid.hex_distance((1, 1), (GRID_ROWS, GRID_COLS_ODD))
        assert d > 0


class TestGridConstants:
    def test_max_col_odd_rows(self):
        assert max_col(1) == GRID_COLS_ODD
        assert max_col(3) == GRID_COLS_ODD

    def test_max_col_even_rows(self):
        assert max_col(2) == GRID_COLS_EVEN
        assert max_col(4) == GRID_COLS_EVEN
