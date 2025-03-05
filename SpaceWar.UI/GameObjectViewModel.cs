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
        public Texture2D? Texture { get; set; }
        
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
            if (texture != null)
            {
                _origin = new Vector2(texture.Width / 2f, texture.Height / 2f);
            }
            else
            {
                _origin = new Vector2(8, 8); // Default size for fallback textures
            }
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
            if (_origin == Vector2.Zero)
            {
                _origin = new Vector2(Texture.Width / 2f, Texture.Height / 2f);
            }
            
            // Get the screen position from the hex grid renderer - this returns the center of the hex
            Vector2 currentHexScreenPos = hexGridRenderer.HexToScreenCoords((int)Position.Y, (int)Position.X);
            Vector2 targetHexScreenPos = hexGridRenderer.HexToScreenCoords((int)TargetPosition.Y, (int)TargetPosition.X);
            
            // For smooth movement between hexes, interpolate the position directly in screen space
            Vector2 position = currentHexScreenPos;
            
            if (IsMoving)
            {
                // Calculate the fractional part of the position for interpolation
                Vector2 fractionalPart = Position - new Vector2((int)Position.X, (int)Position.Y);
                
                // Calculate a direct interpolation between current hex and target hex in screen space
                // This provides smoother movement than trying to interpolate in hex space
                float progress = fractionalPart.Length();
                position = Vector2.Lerp(currentHexScreenPos, targetHexScreenPos, progress);
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
        }
        
        /// <summary>
        /// Draws debug visualization for the game object
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to draw with</param>
        /// <param name="hexGridRenderer">The hex grid renderer</param>
        /// <param name="pixelTexture">A 1x1 white pixel texture for drawing lines</param>
        public void DrawDebugVisualization(SpriteBatch spriteBatch, HexGridRenderer hexGridRenderer, Texture2D pixelTexture)
        {
            if (!IsMoving) return;
            
            // Get the screen positions
            Vector2 currentHexScreenPos = hexGridRenderer.HexToScreenCoords((int)Position.Y, (int)Position.X);
            Vector2 targetHexScreenPos = hexGridRenderer.HexToScreenCoords((int)TargetPosition.Y, (int)TargetPosition.X);
            
            // For smooth movement between hexes, interpolate the position directly in screen space
            Vector2 position = currentHexScreenPos;
            
            if (IsMoving)
            {
                // Calculate the fractional part of the position for interpolation
                Vector2 fractionalPart = Position - new Vector2((int)Position.X, (int)Position.Y);
                
                // Calculate a direct interpolation between current hex and target hex in screen space
                float progress = fractionalPart.Length();
                position = Vector2.Lerp(currentHexScreenPos, targetHexScreenPos, progress);
            }
            
            // Calculate hex size for visualization
            float hexSize = 10 * hexGridRenderer.ScaleFactor; // Approximate hex radius in pixels
            
            // Draw a line showing the movement direction
            DrawLine(spriteBatch, pixelTexture, position, 
                     position + new Vector2((float)Math.Cos(Rotation), (float)Math.Sin(Rotation)) * hexSize, 
                     Color.Yellow * 0.7f, 2);
            
            // Draw a circle at the target position
            DrawCircle(spriteBatch, pixelTexture, targetHexScreenPos, hexSize * 0.3f, Color.Red * 0.5f);
            
            // Draw a line from current position to target position
            DrawLine(spriteBatch, pixelTexture, position, targetHexScreenPos, Color.Green * 0.3f, 1);
        }
        
        /// <summary>
        /// Draws a line between two points
        /// </summary>
        private void DrawLine(SpriteBatch spriteBatch, Texture2D pixelTexture, Vector2 start, Vector2 end, Color color, float thickness = 1f)
        {
            Vector2 edge = end - start;
            float angle = (float)Math.Atan2(edge.Y, edge.X);
            
            spriteBatch.Draw(
                pixelTexture,
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
        
        /// <summary>
        /// Draws a circle at the specified position
        /// </summary>
        private void DrawCircle(SpriteBatch spriteBatch, Texture2D pixelTexture, Vector2 center, float radius, Color color)
        {
            const int segments = 16;
            Vector2[] points = new Vector2[segments + 1];
            
            // Calculate points around the circle
            for (int i = 0; i <= segments; i++)
            {
                float angle = i * MathHelper.TwoPi / segments;
                points[i] = center + new Vector2((float)Math.Cos(angle), (float)Math.Sin(angle)) * radius;
            }
            
            // Draw lines between the points
            for (int i = 0; i < segments; i++)
            {
                DrawLine(spriteBatch, pixelTexture, points[i], points[i + 1], color, 2);
            }
        }
    }
} 