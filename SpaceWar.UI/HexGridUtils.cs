using Microsoft.Xna.Framework;
using System;
using System.Collections.Generic;

namespace SpaceWar.UI
{
    /// <summary>
    /// Utility class for hex grid calculations.
    /// </summary>
    public static class HexGridUtils
    {
        // Hex grid layout constants
        private const float HEX_WIDTH_MULTIPLIER = 0.866f; // sqrt(3)/2

        /// <summary>
        /// Calculates the screen position of a hex cell.
        /// </summary>
        /// <param name="row">The row of the hex cell.</param>
        /// <param name="column">The column of the hex cell.</param>
        /// <param name="hexSize">The size of the hex cell (distance from center to corner).</param>
        /// <param name="offsetX">The X offset for the grid.</param>
        /// <param name="offsetY">The Y offset for the grid.</param>
        /// <returns>The screen position of the hex cell.</returns>
        public static Vector2 HexToScreen(int row, int column, float hexSize, float offsetX, float offsetY)
        {
            // Using axial coordinates (q, r) where q = column and r = row
            // For odd rows, shift columns to the right by half a hex
            float x = hexSize * 2 * HEX_WIDTH_MULTIPLIER * (column + 0.5f * (row % 2)) + offsetX;
            float y = hexSize * 1.5f * row + offsetY;
            
            return new Vector2(x, y);
        }

        /// <summary>
        /// Calculates the hex cell coordinates from a screen position.
        /// </summary>
        /// <param name="screenPosition">The screen position.</param>
        /// <param name="hexSize">The size of the hex cell (distance from center to corner).</param>
        /// <param name="offsetX">The X offset for the grid.</param>
        /// <param name="offsetY">The Y offset for the grid.</param>
        /// <param name="rows">The number of rows in the grid.</param>
        /// <param name="columns">The number of columns in the grid.</param>
        /// <returns>The hex cell coordinates or null if not on a valid hex.</returns>
        public static (int Row, int Column)? ScreenToHex(Vector2 screenPosition, float hexSize, float offsetX, float offsetY, int rows, int columns)
        {
            // Adjust for offset
            float x = screenPosition.X - offsetX;
            float y = screenPosition.Y - offsetY;
            
            // Convert to fractional hex coordinates
            float q = (x / (hexSize * 2 * HEX_WIDTH_MULTIPLIER));
            float r = (y / (hexSize * 1.5f));
            
            // Convert to axial coordinates
            int row = (int)Math.Round(r);
            
            // Adjust q based on row parity
            if (row % 2 == 1)
            {
                q -= 0.5f;
            }
            
            int column = (int)Math.Round(q);
            
            // Check if the coordinates are valid
            if (row >= 0 && row < rows && column >= 0 && column < columns)
            {
                return (row, column);
            }
            
            return null;
        }

        /// <summary>
        /// Calculates the distance between two hex cells.
        /// </summary>
        /// <param name="row1">The row of the first hex cell.</param>
        /// <param name="column1">The column of the first hex cell.</param>
        /// <param name="row2">The row of the second hex cell.</param>
        /// <param name="column2">The column of the second hex cell.</param>
        /// <returns>The distance between the two hex cells.</returns>
        public static int HexDistance(int row1, int column1, int row2, int column2)
        {
            // Convert to cube coordinates
            (int x1, int y1, int z1) = AxialToCube(row1, column1);
            (int x2, int y2, int z2) = AxialToCube(row2, column2);
            
            // Calculate distance
            return (Math.Abs(x1 - x2) + Math.Abs(y1 - y2) + Math.Abs(z1 - z2)) / 2;
        }

        /// <summary>
        /// Converts axial coordinates to cube coordinates.
        /// </summary>
        /// <param name="row">The row (r in axial coordinates).</param>
        /// <param name="column">The column (q in axial coordinates).</param>
        /// <returns>The cube coordinates (x, y, z).</returns>
        private static (int x, int y, int z) AxialToCube(int row, int column)
        {
            int x = column - (row - (row & 1)) / 2;
            int z = row;
            int y = -x - z;
            return (x, y, z);
        }

        /// <summary>
        /// Gets all hex cells within a certain range of a center hex.
        /// </summary>
        /// <param name="centerRow">The row of the center hex.</param>
        /// <param name="centerColumn">The column of the center hex.</param>
        /// <param name="range">The range.</param>
        /// <param name="rows">The number of rows in the grid.</param>
        /// <param name="columns">The number of columns in the grid.</param>
        /// <returns>A list of hex cells within the range.</returns>
        public static List<(int Row, int Column)> GetHexesInRange(int centerRow, int centerColumn, int range, int rows, int columns)
        {
            List<(int Row, int Column)> result = new List<(int Row, int Column)>();
            
            // Convert center to cube coordinates
            (int cx, int cy, int cz) = AxialToCube(centerRow, centerColumn);
            
            // Iterate through all possible cube coordinates within range
            for (int dx = -range; dx <= range; dx++)
            {
                for (int dy = Math.Max(-range, -dx - range); dy <= Math.Min(range, -dx + range); dy++)
                {
                    int dz = -dx - dy;
                    
                    // Convert back to axial
                    int row = cz + dz;
                    int column = cx + dx + (row - (row & 1)) / 2;
                    
                    // Check if the coordinates are valid
                    if (row >= 0 && row < rows && column >= 0 && column < columns)
                    {
                        result.Add((row, column));
                    }
                }
            }
            
            return result;
        }

        /// <summary>
        /// Gets all hex cells within a range band (from minRange to maxRange) of a center hex.
        /// </summary>
        /// <param name="centerRow">The row of the center hex.</param>
        /// <param name="centerColumn">The column of the center hex.</param>
        /// <param name="minRange">The minimum range (inclusive).</param>
        /// <param name="maxRange">The maximum range (inclusive).</param>
        /// <param name="rows">The number of rows in the grid.</param>
        /// <param name="columns">The number of columns in the grid.</param>
        /// <returns>A list of hex cells within the range band.</returns>
        public static List<(int Row, int Column)> GetHexesInRangeBand(int centerRow, int centerColumn, int minRange, int maxRange, int rows, int columns)
        {
            List<(int Row, int Column)> result = new List<(int Row, int Column)>();
            
            // Convert center to cube coordinates
            (int cx, int cy, int cz) = AxialToCube(centerRow, centerColumn);
            
            // Iterate through all possible cube coordinates within maxRange
            for (int dx = -maxRange; dx <= maxRange; dx++)
            {
                for (int dy = Math.Max(-maxRange, -dx - maxRange); dy <= Math.Min(maxRange, -dx + maxRange); dy++)
                {
                    int dz = -dx - dy;
                    
                    // Calculate distance in cube coordinates
                    int distance = (Math.Abs(dx) + Math.Abs(dy) + Math.Abs(dz)) / 2;
                    
                    // Check if distance is within the range band
                    if (distance >= minRange && distance <= maxRange)
                    {
                        // Convert back to axial
                        int row = cz + dz;
                        int column = cx + dx + (row - (row & 1)) / 2;
                        
                        // Check if the coordinates are valid
                        if (row >= 0 && row < rows && column >= 0 && column < columns)
                        {
                            result.Add((row, column));
                        }
                    }
                }
            }
            
            return result;
        }

        /// <summary>
        /// Gets the neighbors of a hex cell.
        /// </summary>
        /// <param name="row">The row of the hex cell.</param>
        /// <param name="column">The column of the hex cell.</param>
        /// <param name="rows">The number of rows in the grid.</param>
        /// <param name="columns">The number of columns in the grid.</param>
        /// <returns>A list of neighboring hex cells.</returns>
        public static List<(int Row, int Column)> GetNeighbors(int row, int column, int rows, int columns)
        {
            // Neighbor offsets for even and odd rows
            int[][] evenOffsets = new int[][]
            {
                new int[] { -1, -1 }, // Top-left
                new int[] { -1, 0 },  // Top-right
                new int[] { 0, -1 },  // Left
                new int[] { 0, 1 },   // Right
                new int[] { 1, -1 },  // Bottom-left
                new int[] { 1, 0 }    // Bottom-right
            };
            
            int[][] oddOffsets = new int[][]
            {
                new int[] { -1, 0 },  // Top-left
                new int[] { -1, 1 },  // Top-right
                new int[] { 0, -1 },  // Left
                new int[] { 0, 1 },   // Right
                new int[] { 1, 0 },   // Bottom-left
                new int[] { 1, 1 }    // Bottom-right
            };
            
            List<(int Row, int Column)> neighbors = new List<(int Row, int Column)>();
            int[][] offsets = (row % 2 == 0) ? evenOffsets : oddOffsets;
            
            foreach (int[] offset in offsets)
            {
                int newRow = row + offset[0];
                int newColumn = column + offset[1];
                
                if (newRow >= 0 && newRow < rows && newColumn >= 0 && newColumn < columns)
                {
                    neighbors.Add((newRow, newColumn));
                }
            }
            
            return neighbors;
        }
    }
} 