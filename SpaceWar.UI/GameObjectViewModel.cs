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
        public Texture2D Texture { get; set; }
        
        // The position on the hex grid (can be fractional for smooth movement)
        public Vector2 Position { get; set; }
        
        // The target position for movement
        public Vector2 TargetPosition { get; set; }
        
        // The rotation in radians
        public float Rotation { get; set; }
        
        // The target rotation for smooth rotation
        public float TargetRotation { get; set; }
        
        // The speed of movement (hex cells per second)
        public float Speed { get; set; } = 2.0f;
        
        // Whether the object is currently moving
        public bool IsMoving { get; set; }
        
        // The origin point for rotation (center of the texture)
        private Vector2 _origin;
        
        /// <summary>
        /// Creates a new game object view model with default values
        /// </summary>
        public GameObjectViewModel()
        {
            Position = Vector2.Zero;
            TargetPosition = Vector2.Zero;
            Rotation = 0;
            TargetRotation = 0;
            IsMoving = false;
        }
        
        /// <summary>
        /// Creates a new game object view model
        /// </summary>
        /// <param name="texture">The texture to display</param>
        /// <param name="row">Initial row position</param>
        /// <param name="column">Initial column position</param>
        /// <param name="rotation">Initial rotation in radians</param>
        public GameObjectViewModel(Texture2D texture, int row, int column, float rotation)
        {
            Texture = texture;
            Position = new Vector2(column, row);
            TargetPosition = Position;
            Rotation = rotation;
            TargetRotation = rotation;
            IsMoving = false;
            
            // Set the origin to the center of the texture
            _origin = new Vector2(texture.Width / 2f, texture.Height / 2f);
        }
        
        /// <summary>
        /// Draws the game object on the hex grid
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to draw with</param>
        /// <param name="hexGridRenderer">The hex grid renderer</param>
        public void Draw(SpriteBatch spriteBatch, HexGridRenderer hexGridRenderer)
        {
            if (Texture == null) return;
            
            // If _origin hasn't been set yet (e.g., when using the default constructor)
            if (_origin == Vector2.Zero && Texture != null)
            {
                _origin = new Vector2(Texture.Width / 2f, Texture.Height / 2f);
            }
            
            // Get the screen position from the hex grid renderer - this returns the center of the hex
            Vector2 position = hexGridRenderer.HexToScreenCoords((int)Position.Y, (int)Position.X);
            
            // For smooth movement between hexes, interpolate the position
            if (IsMoving)
            {
                // Get the screen position of the target hex
                Vector2 targetScreenPos = hexGridRenderer.HexToScreenCoords((int)TargetPosition.Y, (int)TargetPosition.X);
                
                // Calculate the fractional part of the position
                Vector2 fractionalPart = Position - new Vector2((int)Position.X, (int)Position.Y);
                
                // Interpolate between the current hex and the next hex
                Vector2 nextHexPos = hexGridRenderer.HexToScreenCoords((int)Position.Y + Math.Sign(TargetPosition.Y - Position.Y), 
                                                                      (int)Position.X + Math.Sign(TargetPosition.X - Position.X));
                
                // Adjust position based on the fractional part
                position = Vector2.Lerp(position, nextHexPos, fractionalPart.Length());
            }
            
            // Calculate a scale factor that makes the object fit within the hex
            float hexSize = 10 * hexGridRenderer.ScaleFactor; // Approximate hex radius in pixels
            float objectScale = hexSize / Math.Max(Texture.Width, Texture.Height);
            
            // Reduce the scale by 15% as requested
            objectScale *= 0.85f;
            
            // Draw the texture with rotation
            spriteBatch.Draw(
                Texture,
                position,
                null,
                Color.White, // Use original colors from the texture
                Rotation,
                _origin, // This ensures the texture is centered at the position
                objectScale,
                SpriteEffects.None,
                0f
            );
            
            // Draw a debug line showing the direction of movement if the object is moving
            if (IsMoving)
            {
                // Draw a line from the current position to the target position
                DrawLine(spriteBatch, position, 
                         position + new Vector2((float)Math.Cos(Rotation), (float)Math.Sin(Rotation)) * hexSize, 
                         Color.Yellow * 0.7f, 2);
            }
        }
        
        /// <summary>
        /// Draws a line between two points
        /// </summary>
        private void DrawLine(SpriteBatch spriteBatch, Vector2 start, Vector2 end, Color color, float thickness = 1f)
        {
            Vector2 edge = end - start;
            float angle = (float)Math.Atan2(edge.Y, edge.X);
            
            spriteBatch.Draw(
                Texture, // Using the same texture, assuming it's a white pixel texture
                start,
                null,
                color,
                angle,
                new Vector2(0, 0.5f), // Origin at the left middle
                new Vector2(edge.Length(), thickness),
                SpriteEffects.None,
                0f
            );
        }
    }
} 