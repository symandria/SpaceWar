using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using SpaceWar.Core.Components.UI;
using System.Collections.Generic;

namespace SpaceWar.Core.States
{
    public class MenuState : BaseGameState
    {
        private SpriteBatch spriteBatch;
        private Texture2D background;
        private SpriteFont font;
        private SpriteFont titleFont;
        private readonly Color backgroundColor = new Color(10, 15, 30);  // #0A0F1E
        private readonly Color titleColor = new Color(0, 119, 255);     // #0077FF
        private readonly Vector2 titlePosition = new Vector2(400, 75);   // Centered in title panel

        // UI Components
        private GlassPanel titlePanel;
        private List<GlowingButton> menuButtons;
        private GradientDivider divider;
        private LoadingSpinner loadingSpinner;
        private Modal settingsModal;
        private bool isLoading;

        public MenuState(Game game, GameStateMachine stateMachine) : base(game, stateMachine)
        {
            isLoading = false;
        }

        public override void Initialize()
        {
            base.Initialize();
            spriteBatch = new SpriteBatch(Game.GraphicsDevice);

            // Initialize UI components that don't need fonts
            titlePanel = new GlassPanel(
                Game.GraphicsDevice,
                new Rectangle(200, 30, 400, 100)  // Centered at top
            );

            divider = new GradientDivider(
                Game.GraphicsDevice,
                new Rectangle(200, 150, 400, 1)  // Aligned with title panel
            );

            loadingSpinner = new LoadingSpinner(
                Game.GraphicsDevice,
                new Vector2(400, 500),
                40
            );

            settingsModal = new Modal(
                Game.GraphicsDevice,
                new Rectangle(0, 0, 800, 600)
            );
        }

        public override void LoadContent()
        {
            base.LoadContent();
            try
            {
                background = Game.Content.Load<Texture2D>("backgrounds/menu");
            }
            catch
            {
                background = null; // We'll handle this in Draw
            }
            
            try
            {
                font = Game.Content.Load<SpriteFont>("fonts/menu");
                titleFont = Game.Content.Load<SpriteFont>("fonts/title");

                // Initialize buttons after fonts are loaded
                menuButtons = new List<GlowingButton>
                {
                    new GlowingButton(
                        Game.GraphicsDevice,
                        font,
                        "New Game",
                        new Rectangle(300, 200, 200, 50),
                        () => StartNewGame()
                    ),
                    new GlowingButton(
                        Game.GraphicsDevice,
                        font,
                        "Load Game",
                        new Rectangle(300, 270, 200, 50),
                        () => LoadGame()
                    ),
                    new GlowingButton(
                        Game.GraphicsDevice,
                        font,
                        "Settings",
                        new Rectangle(300, 340, 200, 50),
                        () => ShowSettings()
                    ),
                    new GlowingButton(
                        Game.GraphicsDevice,
                        font,
                        "Exit",
                        new Rectangle(300, 410, 200, 50),
                        () => Game.Exit()
                    )
                };
            }
            catch
            {
                // If we can't load the fonts, we can't proceed
                Game.Exit();
            }
        }

        public override void UnloadContent()
        {
            base.UnloadContent();
            background?.Dispose();
            spriteBatch?.Dispose();
            foreach (var button in menuButtons)
            {
                button.Dispose();
            }
            titlePanel.Dispose();
            divider.Dispose();
            loadingSpinner.Dispose();
            settingsModal.Dispose();
        }

        public override void Update(GameTime gameTime)
        {
            base.Update(gameTime);

            foreach (var button in menuButtons)
            {
                button.Update(gameTime);
            }

            if (isLoading)
            {
                loadingSpinner.Update(gameTime);
            }
            
            settingsModal.Update(gameTime);
        }

        public override void Draw(GameTime gameTime)
        {
            Game.GraphicsDevice.Clear(backgroundColor);

            spriteBatch.Begin();

            // Draw background if available
            if (background != null)
            {
                spriteBatch.Draw(background, Vector2.Zero, Color.White);
            }

            // Draw title panel and text
            titlePanel.Draw(spriteBatch);
            if (titleFont != null)
            {
                string title = "SPACE WAR";
                Vector2 titleSize = titleFont.MeasureString(title);
                spriteBatch.DrawString(
                    titleFont,
                    title,
                    titlePosition - titleSize / 2,  // Center the text
                    titleColor
                );
            }

            // Draw divider
            divider.Draw(spriteBatch);

            // Draw menu buttons
            foreach (var button in menuButtons)
            {
                button.Draw(spriteBatch);
            }

            // Draw loading spinner when needed
            if (isLoading)
            {
                loadingSpinner.Draw(spriteBatch);
            }

            spriteBatch.End();

            // Draw modal on top if visible
            if (settingsModal.IsVisible)
            {
                spriteBatch.Begin();
                settingsModal.Draw(spriteBatch);
                spriteBatch.End();
            }
        }

        private void StartNewGame()
        {
            isLoading = true;
            // TODO: Implement new game logic
        }

        private void LoadGame()
        {
            isLoading = true;
            // TODO: Implement load game logic
        }

        private void ShowSettings()
        {
            settingsModal.Show();
        }
    }
} 