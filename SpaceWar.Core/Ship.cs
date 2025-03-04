using System;
using System.Numerics;

namespace SpaceWar.Core
{
    /// <summary>
    /// Represents a ship in the game
    /// </summary>
    public class Ship
    {
        /// <summary>
        /// The type of ship (e.g., "federation", "klingon", etc.)
        /// </summary>
        public string Type { get; }
        
        /// <summary>
        /// The position of the ship on the hex grid (row, column)
        /// </summary>
        public (int Row, int Column) Position { get; private set; }
        
        /// <summary>
        /// The rotation angle of the ship in degrees (0, 60, 120, 180, 240, 300)
        /// </summary>
        public int Rotation { get; private set; }
        
        /// <summary>
        /// Creates a new ship
        /// </summary>
        /// <param name="type">The type of ship</param>
        /// <param name="row">The row position on the hex grid (1-based)</param>
        /// <param name="column">The column position on the hex grid (1-based)</param>
        /// <param name="rotation">The rotation angle in degrees (0, 60, 120, 180, 240, 300)</param>
        public Ship(string type, int row, int column, int rotation)
        {
            Type = type;
            Position = (row, column);
            Rotation = NormalizeRotation(rotation);
        }
        
        /// <summary>
        /// Moves the ship to a new position on the hex grid
        /// </summary>
        /// <param name="row">The new row position (1-based)</param>
        /// <param name="column">The new column position (1-based)</param>
        public void MoveTo(int row, int column)
        {
            Position = (row, column);
        }
        
        /// <summary>
        /// Rotates the ship to a new angle
        /// </summary>
        /// <param name="rotation">The new rotation angle in degrees</param>
        public void RotateTo(int rotation)
        {
            Rotation = NormalizeRotation(rotation);
        }
        
        /// <summary>
        /// Normalizes the rotation angle to one of the six hex directions (0, 60, 120, 180, 240, 300)
        /// </summary>
        /// <param name="rotation">The rotation angle in degrees</param>
        /// <returns>The normalized rotation angle</returns>
        private int NormalizeRotation(int rotation)
        {
            // Ensure the rotation is positive
            rotation = ((rotation % 360) + 360) % 360;
            
            // Round to the nearest 60 degrees
            int normalizedRotation = (int)Math.Round(rotation / 60.0) * 60;
            
            // Handle the special case of 360 degrees
            if (normalizedRotation == 360)
            {
                normalizedRotation = 0;
            }
            
            return normalizedRotation;
        }
    }
} 