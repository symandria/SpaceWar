using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;

namespace SpaceWar.Core.Components.UI
{
    public class LoadingSpinner
    {
        private readonly Texture2D ringTexture;
        private readonly Vector2 position;
        private readonly float size;
        private readonly Color color = new Color(77, 159, 255);  // #4D9FFF
        private float rotation1, rotation2, rotation3;
        private const float RotationSpeed1 = 3f;  // Full rotation in 2 seconds
        private const float RotationSpeed2 = -3.75f;  // Full rotation in 1.6 seconds
        private const float RotationSpeed3 = 2.5f;  // Full rotation in 2.4 seconds

        public LoadingSpinner(GraphicsDevice graphicsDevice, Vector2 position, float size)
        {
            this.position = position;
            this.size = size;

            // Create ring texture
            int textureSize = (int)size;
            ringTexture = new Texture2D(graphicsDevice, textureSize, textureSize);
            Color[] ringData = new Color[textureSize * textureSize];
            float thickness = size / 20;  // Ring thickness
            float radius = size / 2;

            for (int y = 0; y < textureSize; y++)
            {
                for (int x = 0; x < textureSize; x++)
                {
                    float distanceFromCenter = Vector2.Distance(
                        new Vector2(x, y),
                        new Vector2(radius, radius)
                    );

                    // Create ring effect
                    if (distanceFromCenter > radius - thickness && distanceFromCenter < radius)
                    {
                        ringData[y * textureSize + x] = color;
                    }
                    else
                    {
                        ringData[y * textureSize + x] = Color.Transparent;
                    }
                }
            }

            ringTexture.SetData(ringData);
        }

        public void Update(GameTime gameTime)
        {
            float elapsed = (float)gameTime.ElapsedGameTime.TotalSeconds;

            // Update rotations
            rotation1 = (rotation1 + RotationSpeed1 * elapsed) % MathHelper.TwoPi;
            rotation2 = (rotation2 + RotationSpeed2 * elapsed) % MathHelper.TwoPi;
            rotation3 = (rotation3 + RotationSpeed3 * elapsed) % MathHelper.TwoPi;
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            Vector2 origin = new Vector2(size / 2);

            // Draw outer ring
            spriteBatch.Draw(
                ringTexture,
                position,
                null,
                color,
                rotation1,
                origin,
                1f,
                SpriteEffects.None,
                0f
            );

            // Draw middle ring
            spriteBatch.Draw(
                ringTexture,
                position,
                null,
                color,
                rotation2,
                origin,
                0.8f,
                SpriteEffects.None,
                0f
            );

            // Draw inner ring
            spriteBatch.Draw(
                ringTexture,
                position,
                null,
                color,
                rotation3,
                origin,
                0.6f,
                SpriteEffects.None,
                0f
            );
        }

        public void Dispose()
        {
            ringTexture.Dispose();
        }
    }
} 