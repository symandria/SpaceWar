using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;

namespace SpaceWar.Core.Components.UI
{
    public class Modal
    {
        private readonly GraphicsDevice graphicsDevice;
        private readonly Texture2D overlayTexture;
        private readonly GlassPanel panel;
        private readonly Rectangle screenBounds;
        private readonly Rectangle modalBounds;
        private bool isVisible;
        private float opacity;
        private const float FadeSpeed = 4f;

        public bool IsVisible => isVisible;

        public Modal(GraphicsDevice graphicsDevice, Rectangle screenBounds, int modalWidth = 400, int modalHeight = 300)
        {
            this.graphicsDevice = graphicsDevice;
            this.screenBounds = screenBounds;

            // Create semi-transparent overlay texture
            overlayTexture = new Texture2D(graphicsDevice, 1, 1);
            overlayTexture.SetData(new[] { Color.Black });

            // Calculate modal position (centered)
            modalBounds = new Rectangle(
                (screenBounds.Width - modalWidth) / 2,
                (screenBounds.Height - modalHeight) / 2,
                modalWidth,
                modalHeight
            );

            // Create glass panel for modal content
            panel = new GlassPanel(graphicsDevice, modalBounds);
        }

        public void Show()
        {
            isVisible = true;
        }

        public void Hide()
        {
            isVisible = false;
        }

        public void Update(GameTime gameTime)
        {
            float elapsed = (float)gameTime.ElapsedGameTime.TotalSeconds;

            // Update opacity for fade effect
            if (isVisible && opacity < 1f)
            {
                opacity = MathF.Min(1f, opacity + elapsed * FadeSpeed);
            }
            else if (!isVisible && opacity > 0f)
            {
                opacity = MathF.Max(0f, opacity - elapsed * FadeSpeed);
            }
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            if (opacity <= 0f) return;

            // Draw semi-transparent overlay
            spriteBatch.Draw(
                overlayTexture,
                screenBounds,
                Color.Black * 0.5f * opacity
            );

            // Draw modal panel
            if (opacity > 0.5f)
            {
                panel.Draw(spriteBatch);
            }
        }

        public void Dispose()
        {
            overlayTexture.Dispose();
            panel.Dispose();
        }
    }
} 