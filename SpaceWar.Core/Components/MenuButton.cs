using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;

namespace SpaceWar.Core.Components
{
    public class MenuButton
    {
        private readonly Texture2D normalTexture;
        private readonly Texture2D hoverTexture;
        private readonly Rectangle bounds;
        private readonly string text;
        private readonly SpriteFont font;
        private readonly Action onClick;
        private bool isHovered;
        private MouseState previousMouseState;

        public MenuButton(Texture2D normalTexture, Texture2D hoverTexture, Rectangle bounds, string text, SpriteFont font, Action onClick)
        {
            this.normalTexture = normalTexture;
            this.hoverTexture = hoverTexture;
            this.bounds = bounds;
            this.text = text;
            this.font = font;
            this.onClick = onClick;
        }

        public void Update(GameTime gameTime)
        {
            var mouseState = Mouse.GetState();
            var mousePoint = new Point(mouseState.X, mouseState.Y);

            isHovered = bounds.Contains(mousePoint);

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
            var texture = isHovered ? hoverTexture : normalTexture;
            spriteBatch.Draw(texture, bounds, Color.White);

            if (!string.IsNullOrEmpty(text))
            {
                var textSize = font.MeasureString(text);
                var textPosition = new Vector2(
                    bounds.X + (bounds.Width - textSize.X) / 2,
                    bounds.Y + (bounds.Height - textSize.Y) / 2
                );
                spriteBatch.DrawString(font, text, textPosition, Color.White);
            }
        }
    }
} 