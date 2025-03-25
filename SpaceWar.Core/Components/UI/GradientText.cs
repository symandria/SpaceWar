using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;

namespace SpaceWar.Core.Components.UI
{
    public class GradientText
    {
        private readonly string text;
        private readonly SpriteFont font;
        private readonly Vector2 position;
        private readonly Color startColor = new Color(0, 119, 255);    // #0077FF
        private readonly Color endColor = new Color(77, 159, 255);     // #4D9FFF
        private readonly Texture2D gradientTexture;
        private readonly Vector2 textSize;

        public GradientText(GraphicsDevice graphicsDevice, SpriteFont font, string text, Vector2 position)
        {
            this.font = font;
            this.text = text;
            this.position = position;
            this.textSize = font.MeasureString(text);

            // Create gradient texture
            gradientTexture = new Texture2D(graphicsDevice, (int)textSize.X, 1);
            Color[] gradientData = new Color[(int)textSize.X];
            
            for (int x = 0; x < textSize.X; x++)
            {
                float progress = x / textSize.X;
                gradientData[x] = Color.Lerp(startColor, endColor, progress);
            }
            
            gradientTexture.SetData(gradientData);
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            // First draw the text in black for a subtle shadow effect
            spriteBatch.DrawString(font, text, position + new Vector2(1, 1), new Color(0, 0, 0, 128));

            // Draw the text multiple times with slight offsets for a glow effect
            float glowOpacity = 0.3f;
            spriteBatch.DrawString(font, text, position + new Vector2(-1, 0), startColor * glowOpacity);
            spriteBatch.DrawString(font, text, position + new Vector2(1, 0), startColor * glowOpacity);
            spriteBatch.DrawString(font, text, position + new Vector2(0, -1), startColor * glowOpacity);
            spriteBatch.DrawString(font, text, position + new Vector2(0, 1), startColor * glowOpacity);

            // Draw the main text
            for (int y = 0; y < textSize.Y; y++)
            {
                Rectangle sourceRect = new Rectangle(0, 0, (int)textSize.X, 1);
                Rectangle destRect = new Rectangle((int)position.X, (int)position.Y + y, (int)textSize.X, 1);
                
                // Use the gradient texture as a mask for the text
                spriteBatch.Draw(gradientTexture, destRect, sourceRect, Color.White);
            }
        }

        public void Dispose()
        {
            gradientTexture.Dispose();
        }
    }
} 