using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using SpaceWar.Core;
using System;

namespace SpaceWar.UI
{
    /// <summary>
    /// View model for any game object that can be placed on the hex grid
    /// </summary>
    public class GameObjectViewModel
    {
        // The texture of the game object
        private readonly Texture2D _texture;
        
        // The hex grid position
        private int _row;
        private int _column;
        
        // The rotation in degrees (0, 60, 120, 180, 240, 300)
        private int _rotation;
        
        // The origin point for rotation (center of the texture)
        private Vector2 _origin;
        
        /// <summary>
        /// Gets the current row position
        /// </summary>
        public int Row => _row;
        
        /// <summary>
        /// Gets the current column position
        /// </summary>
        public int Column => _column;
        
        /// <summary>
        /// Gets the current rotation in degrees
        /// </summary>
        public int Rotation => _rotation;
        
        /// <summary>
        /// Creates a new game object view model
        /// </summary>
        /// <param name="texture">The texture to display</param>
        /// <param name="row">Initial row position (1-based)</param>
        /// <param name="column">Initial column position (1-based)</param>
        /// <param name="rotation">Initial rotation in degrees</param>
        public GameObjectViewModel(Texture2D texture, int row, int column, int rotation)
        {
            _texture = texture;
            _row = row;
            _column = column;
            _rotation = NormalizeRotation(rotation);
            
            // Set the origin to the center of the texture
            _origin = new Vector2(_texture.Width / 2f, _texture.Height / 2f);
        }
        
        /// <summary>
        /// Moves the object to a new hex position
        /// </summary>
        /// <param name="row">New row position (1-based)</param>
        /// <param name="column">New column position (1-based)</param>
        public void MoveTo(int row, int column)
        {
            _row = row;
            _column = column;
        }
        
        /// <summary>
        /// Rotates the object to a new direction
        /// </summary>
        /// <param name="rotation">New rotation in degrees</param>
        public void RotateTo(int rotation)
        {
            _rotation = NormalizeRotation(rotation);
        }
        
        /// <summary>
        /// Normalizes the rotation to one of the six hex directions (0, 60, 120, 180, 240, 300)
        /// </summary>
        /// <param name="rotation">Rotation in degrees</param>
        /// <returns>Normalized rotation in degrees</returns>
        private int NormalizeRotation(int rotation)
        {
            // Ensure rotation is positive
            rotation = ((rotation % 360) + 360) % 360;
            
            // Round to the nearest 60 degrees
            int normalizedRotation = (int)Math.Round(rotation / 60.0) * 60;
            
            // Handle the special case of 360 degrees
            if (normalizedRotation == 360)
                normalizedRotation = 0;
                
            return normalizedRotation;
        }
        
        /// <summary>
        /// Draws the game object on the hex grid
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to draw with</param>
        /// <param name="hexGridRenderer">The hex grid renderer</param>
        public void Draw(SpriteBatch spriteBatch, HexGridRenderer hexGridRenderer)
        {
            // Get the screen position from the hex grid renderer - this returns the center of the hex
            Vector2 position = hexGridRenderer.HexToScreenCoords(_row, _column);
            
            // Calculate a scale factor that makes the object fit within the hex
            // The original PNG files are small, so we need to scale them up to be visible
            // but not so large that they overlap neighboring hexes
            float hexSize = 10 * hexGridRenderer.ScaleFactor; // Approximate hex radius in pixels
            float objectScale = hexSize / Math.Max(_texture.Width, _texture.Height);
            
            // Reduce the scale by 15% as requested
            objectScale *= 0.85f;
            
            // Draw the texture with rotation
            spriteBatch.Draw(
                _texture,
                position,
                null,
                Color.White, // Use original colors from the texture
                MathHelper.ToRadians(_rotation),
                _origin, // This ensures the texture is centered at the position
                objectScale,
                SpriteEffects.None,
                0f
            );
            
            // Debug outline removed as requested
        }
    }
} 