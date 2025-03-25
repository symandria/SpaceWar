using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;

namespace SpaceWar.Core.Components.UI
{
    public class GlowingButton
    {
        private readonly Texture2D baseTexture;
        private readonly Texture2D glowTexture;
        private readonly SpriteFont font;
        private readonly string text;
        private readonly Rectangle bounds;
        private readonly Action onClick;
        private readonly Color baseColor = new Color((byte)0, (byte)119, (byte)255);      // #0077FF
        private readonly Color glowColor = new Color((byte)0, (byte)255, (byte)255);      // #00FFFF
        private readonly Color textColor = new Color((byte)224, (byte)224, (byte)224);    // #E0E0E0
        private readonly Color borderColor = new Color((byte)77, (byte)159, (byte)255, (byte)77); // #4D9FFF with 0.3 opacity

        private bool isHovered;
        private float glowIntensity;
        private const float MaxGlowIntensity = 1.0f;
        private const float GlowSpeed = 4.0f;
        private MouseState previousMouseState;

        public GlowingButton(GraphicsDevice graphicsDevice, SpriteFont font, string text, Rectangle bounds, Action onClick)
        {
            this.font = font;
            this.text = text;
            this.bounds = bounds;
            this.onClick = onClick;

            // Create base texture (gradient background)
            baseTexture = new Texture2D(graphicsDevice, bounds.Width, bounds.Height);
            Color[] baseData = new Color[bounds.Width * bounds.Height];
            for (int y = 0; y < bounds.Height; y++)
            {
                for (int x = 0; x < bounds.Width; x++)
                {
                    float progress = x / (float)bounds.Width;
                    baseData[y * bounds.Width + x] = Color.Lerp(baseColor, glowColor, progress);
                }
            }
            baseTexture.SetData(baseData);

            // Create glow texture (for hover effect)
            glowTexture = new Texture2D(graphicsDevice, bounds.Width + 20, bounds.Height + 20);
            Color[] glowData = new Color[(bounds.Width + 20) * (bounds.Height + 20)];
            for (int y = 0; y < bounds.Height + 20; y++)
            {
                for (int x = 0; x < bounds.Width + 20; x++)
                {
                    float distanceFromEdge = MathF.Min(
                        MathF.Min(x, (bounds.Width + 20) - x),
                        MathF.Min(y, (bounds.Height + 20) - y)
                    );
                    float alpha = MathF.Max(0, 1 - (distanceFromEdge / 10));
                    glowData[y * (bounds.Width + 20) + x] = new Color((byte)0, (byte)255, (byte)255, (byte)(alpha * 255));
                }
            }
            glowTexture.SetData(glowData);
        }

        public void Update(GameTime gameTime)
        {
            var mouseState = Mouse.GetState();
            var mousePoint = new Point(mouseState.X, mouseState.Y);
            bool wasHovered = isHovered;
            isHovered = bounds.Contains(mousePoint);

            // Handle hover animation
            float elapsed = (float)gameTime.ElapsedGameTime.TotalSeconds;
            if (isHovered && glowIntensity < MaxGlowIntensity)
            {
                glowIntensity = MathF.Min(MaxGlowIntensity, glowIntensity + elapsed * GlowSpeed);
            }
            else if (!isHovered && glowIntensity > 0)
            {
                glowIntensity = MathF.Max(0, glowIntensity - elapsed * GlowSpeed);
            }

            // Handle click
            if (isHovered && 
                mouseState.LeftButton == ButtonState.Released && 
                previousMouseState.LeftButton == ButtonState.Pressed)
            {
                onClick?.Invoke();
            }

            previousMouseState = mouseState;
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            // Draw glow effect if hovered
            if (glowIntensity > 0)
            {
                spriteBatch.Draw(
                    glowTexture, 
                    new Rectangle(bounds.X - 10, bounds.Y - 10, bounds.Width + 20, bounds.Height + 20),
                    Color.White * glowIntensity
                );
            }

            // Draw base button
            spriteBatch.Draw(baseTexture, bounds, Color.White);

            // Draw border
            int borderThickness = 1;
            spriteBatch.Draw(baseTexture, new Rectangle(bounds.X, bounds.Y, bounds.Width, borderThickness), borderColor);                              // Top
            spriteBatch.Draw(baseTexture, new Rectangle(bounds.X, bounds.Y + bounds.Height - borderThickness, bounds.Width, borderThickness), borderColor); // Bottom
            spriteBatch.Draw(baseTexture, new Rectangle(bounds.X, bounds.Y, borderThickness, bounds.Height), borderColor);                              // Left
            spriteBatch.Draw(baseTexture, new Rectangle(bounds.X + bounds.Width - borderThickness, bounds.Y, borderThickness, bounds.Height), borderColor); // Right

            // Draw text
            if (!string.IsNullOrEmpty(text))
            {
                Vector2 textSize = font.MeasureString(text);
                Vector2 textPosition = new Vector2(
                    bounds.X + (bounds.Width - textSize.X) / 2,
                    bounds.Y + (bounds.Height - textSize.Y) / 2
                );
                spriteBatch.DrawString(font, text, textPosition, textColor);
            }
        }

        public void Dispose()
        {
            baseTexture.Dispose();
            glowTexture.Dispose();
        }
    }
} 