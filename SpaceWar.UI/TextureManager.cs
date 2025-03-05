using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using System;
using System.Collections.Generic;

namespace SpaceWar.UI
{
    /// <summary>
    /// Manages loading and caching of textures.
    /// </summary>
    public class TextureManager
    {
        private readonly ContentManager _content;
        private readonly GraphicsDevice _graphicsDevice;
        private readonly Dictionary<string, Texture2D> _textures = new Dictionary<string, Texture2D>();
        private readonly Dictionary<string, Texture2D> _generatedTextures = new Dictionary<string, Texture2D>();

        /// <summary>
        /// Creates a new texture manager.
        /// </summary>
        /// <param name="content">The content manager.</param>
        /// <param name="graphicsDevice">The graphics device.</param>
        public TextureManager(ContentManager content, GraphicsDevice graphicsDevice)
        {
            _content = content;
            _graphicsDevice = graphicsDevice;
            
            // Generate common textures
            GenerateHexTexture("hex", 100, Color.Transparent, 2, Color.Black);
            GenerateHexTexture("hex_highlight", 100, new Color(255, 255, 255, 128), 2, Color.Yellow);
            GenerateCircleTexture("circle", 100, Color.White, 2, Color.Black);
            GenerateRectangleTexture("pixel", 1, 1, Color.White);
        }

        /// <summary>
        /// Gets a texture by key.
        /// </summary>
        /// <param name="key">The texture key.</param>
        /// <returns>The texture.</returns>
        public Texture2D GetTexture(string key)
        {
            // Check if the texture is already loaded
            if (_textures.TryGetValue(key, out Texture2D texture))
            {
                return texture;
            }
            
            // Check if it's a generated texture
            if (_generatedTextures.TryGetValue(key, out texture))
            {
                return texture;
            }
            
            // Try to load the texture from content
            try
            {
                texture = _content.Load<Texture2D>(key);
                _textures[key] = texture;
                return texture;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to load texture '{key}': {ex.Message}");
                
                // Return a default texture
                return GetTexture("pixel");
            }
        }

        /// <summary>
        /// Adds a texture to the manager.
        /// </summary>
        /// <param name="key">The texture key.</param>
        /// <param name="texture">The texture.</param>
        public void AddTexture(string key, Texture2D texture)
        {
            _textures[key] = texture;
        }

        /// <summary>
        /// Generates a hex texture.
        /// </summary>
        /// <param name="key">The texture key.</param>
        /// <param name="size">The size of the hex (distance from center to corner).</param>
        /// <param name="fillColor">The fill color.</param>
        /// <param name="outlineThickness">The outline thickness.</param>
        /// <param name="outlineColor">The outline color.</param>
        public void GenerateHexTexture(string key, int size, Color fillColor, int outlineThickness, Color outlineColor)
        {
            int width = (int)(size * 2);
            int height = (int)(size * 2);
            
            Texture2D texture = new Texture2D(_graphicsDevice, width, height);
            Color[] data = new Color[width * height];
            
            // Fill with transparent
            for (int i = 0; i < data.Length; i++)
            {
                data[i] = Color.Transparent;
            }
            
            // Calculate hex points
            Vector2 center = new Vector2(width / 2, height / 2);
            Vector2[] points = new Vector2[6];
            
            for (int i = 0; i < 6; i++)
            {
                float angle = MathHelper.TwoPi * i / 6 + MathHelper.PiOver2;
                points[i] = center + new Vector2((float)Math.Cos(angle), (float)Math.Sin(angle)) * size;
            }
            
            // For the "hex" key, only draw the outline
            if (key == "hex")
            {
                // Draw outline only
                if (outlineThickness > 0)
                {
                    for (int i = 0; i < 6; i++)
                    {
                        DrawLine(data, width, height, points[i], points[(i + 1) % 6], outlineThickness, outlineColor);
                    }
                }
            }
            else
            {
                // For other hex textures, draw filled hex
                FillPolygon(data, width, height, points, fillColor);
                
                // Draw outline
                if (outlineThickness > 0)
                {
                    for (int i = 0; i < 6; i++)
                    {
                        DrawLine(data, width, height, points[i], points[(i + 1) % 6], outlineThickness, outlineColor);
                    }
                }
            }
            
            texture.SetData(data);
            _generatedTextures[key] = texture;
        }

        /// <summary>
        /// Generates a circle texture.
        /// </summary>
        /// <param name="key">The texture key.</param>
        /// <param name="radius">The radius of the circle.</param>
        /// <param name="fillColor">The fill color.</param>
        /// <param name="outlineThickness">The outline thickness.</param>
        /// <param name="outlineColor">The outline color.</param>
        public void GenerateCircleTexture(string key, int radius, Color fillColor, int outlineThickness, Color outlineColor)
        {
            int diameter = radius * 2;
            Texture2D texture = new Texture2D(_graphicsDevice, diameter, diameter);
            Color[] data = new Color[diameter * diameter];
            
            // Fill with transparent
            for (int i = 0; i < data.Length; i++)
            {
                data[i] = Color.Transparent;
            }
            
            // Draw filled circle
            Vector2 center = new Vector2(radius, radius);
            
            for (int y = 0; y < diameter; y++)
            {
                for (int x = 0; x < diameter; x++)
                {
                    float distance = Vector2.Distance(new Vector2(x, y), center);
                    
                    if (distance <= radius - outlineThickness)
                    {
                        data[y * diameter + x] = fillColor;
                    }
                    else if (distance <= radius)
                    {
                        data[y * diameter + x] = outlineColor;
                    }
                }
            }
            
            texture.SetData(data);
            _generatedTextures[key] = texture;
        }

        /// <summary>
        /// Generates a rectangle texture.
        /// </summary>
        /// <param name="key">The texture key.</param>
        /// <param name="width">The width of the rectangle.</param>
        /// <param name="height">The height of the rectangle.</param>
        /// <param name="color">The color of the rectangle.</param>
        public void GenerateRectangleTexture(string key, int width, int height, Color color)
        {
            Texture2D texture = new Texture2D(_graphicsDevice, width, height);
            Color[] data = new Color[width * height];
            
            for (int i = 0; i < data.Length; i++)
            {
                data[i] = color;
            }
            
            texture.SetData(data);
            _generatedTextures[key] = texture;
        }

        /// <summary>
        /// Fills a polygon with a color.
        /// </summary>
        /// <param name="data">The texture data.</param>
        /// <param name="width">The texture width.</param>
        /// <param name="height">The texture height.</param>
        /// <param name="points">The polygon points.</param>
        /// <param name="color">The fill color.</param>
        private void FillPolygon(Color[] data, int width, int height, Vector2[] points, Color color)
        {
            // Find bounding box
            float minX = float.MaxValue;
            float minY = float.MaxValue;
            float maxX = float.MinValue;
            float maxY = float.MinValue;
            
            foreach (Vector2 point in points)
            {
                minX = Math.Min(minX, point.X);
                minY = Math.Min(minY, point.Y);
                maxX = Math.Max(maxX, point.X);
                maxY = Math.Max(maxY, point.Y);
            }
            
            // Clip to texture bounds
            minX = Math.Max(0, minX);
            minY = Math.Max(0, minY);
            maxX = Math.Min(width - 1, maxX);
            maxY = Math.Min(height - 1, maxY);
            
            // Fill polygon
            for (int y = (int)minY; y <= maxY; y++)
            {
                for (int x = (int)minX; x <= maxX; x++)
                {
                    if (PointInPolygon(new Vector2(x, y), points))
                    {
                        data[y * width + x] = color;
                    }
                }
            }
        }

        /// <summary>
        /// Checks if a point is inside a polygon.
        /// </summary>
        /// <param name="point">The point.</param>
        /// <param name="polygon">The polygon points.</param>
        /// <returns>True if the point is inside the polygon, false otherwise.</returns>
        private bool PointInPolygon(Vector2 point, Vector2[] polygon)
        {
            bool inside = false;
            
            for (int i = 0, j = polygon.Length - 1; i < polygon.Length; j = i++)
            {
                if (((polygon[i].Y > point.Y) != (polygon[j].Y > point.Y)) &&
                    (point.X < (polygon[j].X - polygon[i].X) * (point.Y - polygon[i].Y) / (polygon[j].Y - polygon[i].Y) + polygon[i].X))
                {
                    inside = !inside;
                }
            }
            
            return inside;
        }

        /// <summary>
        /// Draws a line between two points.
        /// </summary>
        /// <param name="data">The texture data.</param>
        /// <param name="width">The texture width.</param>
        /// <param name="height">The texture height.</param>
        /// <param name="start">The start point.</param>
        /// <param name="end">The end point.</param>
        /// <param name="thickness">The line thickness.</param>
        /// <param name="color">The line color.</param>
        private void DrawLine(Color[] data, int width, int height, Vector2 start, Vector2 end, int thickness, Color color)
        {
            // Calculate line direction
            Vector2 direction = end - start;
            float length = direction.Length();
            
            if (length < 1)
            {
                return;
            }
            
            direction /= length;
            
            // Calculate perpendicular direction
            Vector2 perpendicular = new Vector2(-direction.Y, direction.X);
            
            // Draw line
            for (int i = 0; i < length; i++)
            {
                Vector2 position = start + direction * i;
                
                for (int t = -thickness / 2; t <= thickness / 2; t++)
                {
                    Vector2 point = position + perpendicular * t;
                    
                    int x = (int)point.X;
                    int y = (int)point.Y;
                    
                    if (x >= 0 && x < width && y >= 0 && y < height)
                    {
                        data[y * width + x] = color;
                    }
                }
            }
        }
    }
} 