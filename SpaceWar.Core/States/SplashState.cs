using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using SpaceWar.Core.Components.UI;

namespace SpaceWar.Core.States
{
    public class SplashState : BaseGameState
    {
        private SpriteBatch spriteBatch;
        private Texture2D splashBackground;
        private Texture2D gameLogo;
        private SpriteFont titleFont;
        private GlowingButton playButton;
        private float logoAlpha = 0f;
        private float buttonAlpha = 0f;
        private const float FadeInSpeed = 1.0f;
        private const float LogoDelay = 0.5f;
        private const float ButtonDelay = 1.5f;
        private float elapsedTime = 0f;

        public SplashState(Game game, GameStateMachine stateMachine) : base(game, stateMachine)
        {
        }

        public override void Initialize()
        {
            base.Initialize();
            spriteBatch = new SpriteBatch(Game.GraphicsDevice);
        }

        public override void LoadContent()
        {
            base.LoadContent();
            
            // Load assets
            splashBackground = Game.Content.Load<Texture2D>("backgrounds/splash");
            gameLogo = Game.Content.Load<Texture2D>("backgrounds/SpaceWarsLogo");
            titleFont = Game.Content.Load<SpriteFont>("fonts/title");

            // Calculate centered position for the play button based on screen size
            int screenWidth = Game.GraphicsDevice.Viewport.Width;
            int screenHeight = Game.GraphicsDevice.Viewport.Height;
            int buttonWidth = 200;
            int buttonHeight = 50;
            int buttonX = (screenWidth - buttonWidth) / 2;
            int buttonY = (int)(screenHeight * 0.7f); // Position at 70% of screen height

            // Create play button
            playButton = new GlowingButton(
                Game.GraphicsDevice,
                titleFont,
                "Play Game",
                new Rectangle(buttonX, buttonY, buttonWidth, buttonHeight),
                () => StateMachine.TransitionTo<MenuState>()
            );
        }

        public override void UnloadContent()
        {
            base.UnloadContent();
            splashBackground?.Dispose();
            gameLogo?.Dispose();
            spriteBatch?.Dispose();
            playButton?.Dispose();
        }

        public override void Update(GameTime gameTime)
        {
            base.Update(gameTime);

            float deltaTime = (float)gameTime.ElapsedGameTime.TotalSeconds;
            elapsedTime += deltaTime;
            
            // Update logo fade-in
            if (elapsedTime > LogoDelay)
            {
                logoAlpha = MathHelper.Min((elapsedTime - LogoDelay) * FadeInSpeed, 1f);
            }

            // Update button fade-in and interaction
            if (elapsedTime > ButtonDelay)
            {
                buttonAlpha = MathHelper.Min((elapsedTime - ButtonDelay) * FadeInSpeed, 1f);
                playButton.Update(gameTime);
            }

            // Allow keyboard/mouse to skip splash screen
            var keyboardState = Keyboard.GetState();
            var mouseState = Mouse.GetState();
            if (keyboardState.GetPressedKeys().Length > 0 || 
                mouseState.LeftButton == ButtonState.Pressed || 
                mouseState.RightButton == ButtonState.Pressed)
            {
                if (elapsedTime > 0.5f) // Prevent accidental skips
                {
                    StateMachine.TransitionTo<MenuState>();
                }
            }
        }

        public override void Draw(GameTime gameTime)
        {
            Game.GraphicsDevice.Clear(Color.Black);

            spriteBatch.Begin();

            // Draw background (no fade)
            if (splashBackground != null)
            {
                spriteBatch.Draw(
                    splashBackground,
                    new Rectangle(0, 0, Game.GraphicsDevice.Viewport.Width, Game.GraphicsDevice.Viewport.Height),
                    Color.White
                );
            }

            // Draw logo with fade-in
            if (gameLogo != null)
            {
                // Calculate centered position for logo
                int screenWidth = Game.GraphicsDevice.Viewport.Width;
                int screenHeight = Game.GraphicsDevice.Viewport.Height;
                int logoWidth = (int)(screenWidth * 0.5f); // Logo takes up 50% of screen width
                int logoHeight = (int)(logoWidth * ((float)gameLogo.Height / gameLogo.Width)); // Maintain aspect ratio
                int logoX = (screenWidth - logoWidth) / 2;
                int logoY = (int)(screenHeight * 0.2f); // Position at 20% of screen height

                spriteBatch.Draw(
                    gameLogo,
                    new Rectangle(logoX, logoY, logoWidth, logoHeight),
                    Color.White * logoAlpha
                );
            }

            spriteBatch.End();

            // Draw button with fade-in (if visible)
            if (buttonAlpha > 0)
            {
                spriteBatch.Begin();
                playButton.Draw(spriteBatch);
                spriteBatch.End();
            }
        }
    }
} 