using System;
using System.Collections.Generic;
using System.Numerics;

namespace SpaceWar.Core
{
    /// <summary>
    /// Represents a hexagonal grid system using the original Python implementation's approach
    /// </summary>
    public class HexGrid
    {
        /// <summary>
        /// Number of rows in the grid
        /// </summary>
        public int Rows { get; }

        /// <summary>
        /// Number of columns in the grid
        /// </summary>
        public int Columns { get; }

        /// <summary>
        /// Creates a new hex grid with the specified dimensions
        /// </summary>
        /// <param name="rows">Number of rows</param>
        /// <param name="columns">Number of columns</param>
        public HexGrid(int rows, int columns)
        {
            Rows = rows;
            Columns = columns;
        }

        /// <summary>
        /// Represents a hex in the grid
        /// </summary>
        public struct Hex
        {
            /// <summary>
            /// Row coordinate (1-based)
            /// </summary>
            public int Row { get; }

            /// <summary>
            /// Column coordinate (1-based)
            /// </summary>
            public int Column { get; }

            /// <summary>
            /// Creates a new hex with the specified coordinates
            /// </summary>
            /// <param name="row">Row coordinate (1-based)</param>
            /// <param name="column">Column coordinate (1-based)</param>
            public Hex(int row, int column)
            {
                Row = row;
                Column = column;
            }
        }

        /// <summary>
        /// Converts hex coordinates to screen coordinates, matching the original Python implementation
        /// </summary>
        /// <param name="row">Row (1-based)</param>
        /// <param name="column">Column (1-based)</param>
        /// <returns>Screen coordinates (x, y)</returns>
        public Vector2 HexToCoords(int row, int column)
        {
            // Exact implementation from the Python code:
            // return (14*column + ((row-1) % 2)*7 - 9, 8+10*row)
            return new Vector2(
                14 * column + ((row - 1) % 2) * 7 - 9,
                8 + 10 * row
            );
        }

        /// <summary>
        /// Converts screen coordinates to hex coordinates, matching the original Python implementation
        /// </summary>
        /// <param name="position">Screen coordinates (x, y)</param>
        /// <returns>Hex coordinates (row, column) or null if outside the grid</returns>
        public (int Row, int Column)? CoordsToHex(Vector2 position)
        {
            float x = position.X;
            float y = position.Y;

            // Exact implementation from the Python code
            if (x < 2 || y < 17 || x > 155 || y > 156)
            {
                return null;
            }
            else if (x < 9 && (y - 17) % 20 >= 10)
            {
                return null;
            }
            else if ((y - 17) % 20 < 10)
            {
                return ((int)(y - 17) / 10 + 1, (int)(x - 2) / 14 + 1);
            }
            else
            {
                return ((int)(y - 17) / 10 + 1, (int)(x - 9) / 14 + 1);
            }
        }

        /// <summary>
        /// Calculates the distance between two hex coordinates, matching the original Python implementation
        /// </summary>
        /// <param name="hex1">First hex coordinates (row, column)</param>
        /// <param name="hex2">Second hex coordinates (row, column)</param>
        /// <returns>Distance in hex units</returns>
        public int HexDistance((int Row, int Column) hex1, (int Row, int Column) hex2)
        {
            // Exact implementation from the Python code:
            // hex1 = hex1[0], hex1[1] - (hex1[0] + 1) // 2
            // hex1 += 0 - hex1[0] - hex1[1],
            // hex2 = hex2[0], hex2[1] - (hex2[0] + 1) // 2
            // hex2 += 0 - hex2[0] - hex2[1],
            // return max(abs(hex1[0] - hex2[0]), abs(hex1[1] - hex2[1]), abs(hex1[2] - hex2[2]))
            
            // Convert to cube coordinates
            var cube1 = AxialToCube(hex1.Row, hex1.Column);
            var cube2 = AxialToCube(hex2.Row, hex2.Column);

            // Calculate distance
            return Math.Max(
                Math.Max(
                    Math.Abs(cube1.X - cube2.X),
                    Math.Abs(cube1.Y - cube2.Y)
                ),
                Math.Abs(cube1.Z - cube2.Z)
            );
        }

        /// <summary>
        /// Converts axial coordinates to cube coordinates, matching the original Python implementation
        /// </summary>
        /// <param name="row">Row (1-based)</param>
        /// <param name="column">Column (1-based)</param>
        /// <returns>Cube coordinates (x, y, z)</returns>
        private (int X, int Y, int Z) AxialToCube(int row, int column)
        {
            // Exact implementation from the Python code
            int x = row;
            int z = column - (row + 1) / 2;
            int y = -x - z;
            return (x, y, z);
        }

        /// <summary>
        /// Gets all valid hex coordinates in the grid
        /// </summary>
        /// <returns>Array of valid hexes</returns>
        public Hex[] GetAllHexes()
        {
            var hexes = new List<Hex>();
            
            for (int row = 1; row <= Rows; row++)
            {
                int maxColumns = GetMaxColumnsForRow(row);
                
                for (int column = 1; column <= maxColumns; column++)
                {
                    hexes.Add(new Hex(row, column));
                }
            }
            
            return hexes.ToArray();
        }

        /// <summary>
        /// Gets the maximum number of columns for a specific row
        /// </summary>
        /// <param name="row">Row number (1-based)</param>
        /// <returns>Maximum number of columns for the row</returns>
        public int GetMaxColumnsForRow(int row)
        {
            // In the original Python code, the pattern is:
            // Row 1: 11 columns
            // Row 2: 10 columns
            // Row 3: 11 columns
            // etc.
            int maxColumns = (row % 2 == 1) ? 11 : 10;
            return Math.Min(maxColumns, Columns);
        }

        /// <summary>
        /// Converts row, column coordinates to q, r coordinates
        /// </summary>
        /// <param name="row">Row (1-based)</param>
        /// <param name="column">Column (1-based)</param>
        /// <returns>Hex with q, r coordinates</returns>
        public Hex RowColumnToHex(int row, int column)
        {
            // Convert 1-based row, column to 0-based q, r
            return new Hex(column - 1, row - 1);
        }

        /// <summary>
        /// Converts q, r coordinates to row, column coordinates
        /// </summary>
        /// <param name="q">Q coordinate</param>
        /// <param name="r">R coordinate</param>
        /// <returns>Row, column coordinates (1-based)</returns>
        public (int Row, int Column) HexToRowColumn(int q, int r)
        {
            // Convert 0-based q, r to 1-based row, column
            return (r + 1, q + 1);
        }
    }
} 