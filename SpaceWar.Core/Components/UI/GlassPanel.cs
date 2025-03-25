using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using System;

namespace SpaceWar.Core.Components.UI
{
    public class GlassPanel
    {
        private readonly Texture2D backgroundTexture;
        private readonly Texture2D borderTexture;
        private readonly Rectangle bounds;
        private readonly Color backgroundColor = new Color((byte)22, (byte)33, (byte)55, (byte)153);  // #162137 with 0.6 opacity
        private readonly Color borderColor = new Color((byte)77, (byte)159, (byte)255, (byte)77);     // #4D9FFF with 0.3 opacity
        private readonly Color glowColor = new Color((byte)0, (byte)119, (byte)255, (byte)26);        // #0077FF with 0.1 opacity

        public GlassPanel(GraphicsDevice graphicsDevice, Rectangle bounds)
        {
            this.bounds = bounds;

            // Create background texture
            backgroundTexture = new Texture2D(graphicsDevice, 1, 1);
            backgroundTexture.SetData(new[] { Color.White });

            // Create border texture with glow
            int borderSize = 20; // Size of the border glow effect
            borderTexture = new Texture2D(graphicsDevice, bounds.Width + borderSize * 2, bounds.Height + borderSize * 2);
            Color[] borderData = new Color[(bounds.Width + borderSize * 2) * (bounds.Height + borderSize * 2)];

            for (int y = 0; y < bounds.Height + borderSize * 2; y++)
            {
                for (int x = 0; x < bounds.Width + borderSize * 2; x++)
                {
                    // Calculate distance from edge of panel
                    float distanceFromEdge = float.MaxValue;
                    if (x < borderSize || x >= bounds.Width + borderSize)
                        distanceFromEdge = MathF.Min(distanceFromEdge, MathF.Min(x, bounds.Width + borderSize * 2 - x));
                    if (y < borderSize || y >= bounds.Height + borderSize)
                        distanceFromEdge = MathF.Min(distanceFromEdge, MathF.Min(y, bounds.Height + borderSize * 2 - y));

                    // Create glow effect
                    float glowStrength = MathF.Max(0, 1 - distanceFromEdge / borderSize);
                    borderData[y * (bounds.Width + borderSize * 2) + x] = glowColor * glowStrength;
                }
            }
            borderTexture.SetData(borderData);
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            // Draw border glow
            spriteBatch.Draw(
                borderTexture,
                new Vector2(bounds.X - 20, bounds.Y - 20),
                Color.White
            );

            // Draw background
            spriteBatch.Draw(backgroundTexture, bounds, backgroundColor);

            // Draw border
            int borderThickness = 1;
            spriteBatch.Draw(backgroundTexture, new Rectangle(bounds.X, bounds.Y, bounds.Width, borderThickness), borderColor);                              // Top
            spriteBatch.Draw(backgroundTexture, new Rectangle(bounds.X, bounds.Y + bounds.Height - borderThickness, bounds.Width, borderThickness), borderColor); // Bottom
            spriteBatch.Draw(backgroundTexture, new Rectangle(bounds.X, bounds.Y, borderThickness, bounds.Height), borderColor);                              // Left
            spriteBatch.Draw(backgroundTexture, new Rectangle(bounds.X + bounds.Width - borderThickness, bounds.Y, borderThickness, bounds.Height), borderColor); // Right
        }

        public void Dispose()
        {
            backgroundTexture.Dispose();
            borderTexture.Dispose();
        }
    }
} 