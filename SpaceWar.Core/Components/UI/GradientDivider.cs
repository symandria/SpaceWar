using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;

namespace SpaceWar.Core.Components.UI
{
    public class GradientDivider
    {
        private readonly Texture2D dividerTexture;
        private readonly Rectangle bounds;
        private readonly Color startColor = new Color(77, 159, 255, 77);  // #4D9FFF with 0.3 opacity
        private readonly Color endColor = new Color(77, 159, 255, 0);     // #4D9FFF with 0 opacity (transparent)

        public GradientDivider(GraphicsDevice graphicsDevice, Rectangle bounds)
        {
            this.bounds = bounds;

            // Create gradient texture
            dividerTexture = new Texture2D(graphicsDevice, bounds.Width, 1);
            Color[] gradientData = new Color[bounds.Width];

            for (int x = 0; x < bounds.Width; x++)
            {
                float progress = x / (float)bounds.Width;
                if (progress < 0.5f)
                {
                    // First half: fade in to middle
                    float fadeIn = progress * 2;
                    gradientData[x] = Color.Lerp(startColor, startColor, fadeIn);
                }
                else
                {
                    // Second half: fade out to transparent
                    float fadeOut = (progress - 0.5f) * 2;
                    gradientData[x] = Color.Lerp(startColor, endColor, fadeOut);
                }
            }

            dividerTexture.SetData(gradientData);
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            spriteBatch.Draw(dividerTexture, bounds, Color.White);
        }

        public void Dispose()
        {
            dividerTexture.Dispose();
        }
    }
} 