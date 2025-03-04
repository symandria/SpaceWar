using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;
using System.Collections.Generic;

namespace SpaceWar.UI
{
    /// <summary>
    /// Represents a button in the menu system
    /// </summary>
    public class Button
    {
        private Rectangle _bounds;
        private string _text;
        private SpriteFont _font;
        private Color _textColor;
        private Color _backgroundColor;
        private Color _hoverColor;
        private bool _isHovered;
        private Action? _onClick;
        private Action<Button>? _onClickWithButton;
        private Texture2D _pixelTexture;

        public string Text 
        { 
            get { return _text; } 
            set { _text = value; } 
        }

        /// <summary>
        /// Creates a new button
        /// </summary>
        /// <param name="bounds">The bounds of the button</param>
        /// <param name="text">The text to display on the button</param>
        /// <param name="font">The font to use for the text</param>
        /// <param name="onClick">The action to perform when the button is clicked</param>
        /// <param name="pixelTexture">A 1x1 white texture for drawing</param>
        public Button(Rectangle bounds, string text, SpriteFont font, Action onClick, Texture2D pixelTexture)
        {
            _bounds = bounds;
            _text = text;
            _font = font;
            _onClick = onClick;
            _onClickWithButton = null;
            _pixelTexture = pixelTexture;
            _textColor = Color.Black;
            _backgroundColor = new Color(200, 200, 200);
            _hoverColor = new Color(220, 220, 220);
            _isHovered = false;
        }
        
        /// <summary>
        /// Creates a new button with a callback that receives the button instance
        /// </summary>
        /// <param name="bounds">The bounds of the button</param>
        /// <param name="text">The text to display on the button</param>
        /// <param name="font">The font to use for the text</param>
        /// <param name="onClickWithButton">The action to perform when the button is clicked, receiving the button instance</param>
        /// <param name="pixelTexture">A 1x1 white texture for drawing</param>
        public Button(Rectangle bounds, string text, SpriteFont font, Action<Button> onClickWithButton, Texture2D pixelTexture)
        {
            _bounds = bounds;
            _text = text;
            _font = font;
            _onClick = null;
            _onClickWithButton = onClickWithButton;
            _pixelTexture = pixelTexture;
            _textColor = Color.Black;
            _backgroundColor = new Color(200, 200, 200);
            _hoverColor = new Color(220, 220, 220);
            _isHovered = false;
        }

        /// <summary>
        /// Updates the button state
        /// </summary>
        /// <param name="mouseState">Current mouse state</param>
        /// <param name="prevMouseState">Previous mouse state</param>
        public void Update(MouseState mouseState, MouseState prevMouseState)
        {
            // Check if the mouse is over the button
            _isHovered = _bounds.Contains(mouseState.X, mouseState.Y);

            // Check if the button was clicked
            if (_isHovered && 
                mouseState.LeftButton == ButtonState.Released && 
                prevMouseState.LeftButton == ButtonState.Pressed)
            {
                if (_onClick != null)
                {
                    _onClick();
                }
                else if (_onClickWithButton != null)
                {
                    _onClickWithButton(this);
                }
            }
        }

        /// <summary>
        /// Draws the button
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to draw with</param>
        public void Draw(SpriteBatch spriteBatch)
        {
            // Draw button background with solid color
            spriteBatch.Draw(
                _pixelTexture, 
                _bounds, 
                _isHovered ? _hoverColor : _backgroundColor
            );
            
            // Draw button border
            DrawBorder(spriteBatch, _pixelTexture, _bounds, 2, Color.Black);
            
            // Draw button text
            Vector2 textSize = _font.MeasureString(_text);
            Vector2 textPosition = new Vector2(
                _bounds.X + (_bounds.Width - textSize.X) / 2,
                _bounds.Y + (_bounds.Height - textSize.Y) / 2
            );
            
            // Draw text with shadow for better visibility
            spriteBatch.DrawString(_font, _text, textPosition + new Vector2(1, 1), Color.Black * 0.5f);
            spriteBatch.DrawString(_font, _text, textPosition, _textColor);
        }
        
        /// <summary>
        /// Draws a border around a rectangle
        /// </summary>
        private void DrawBorder(SpriteBatch spriteBatch, Texture2D pixel, Rectangle rect, int thickness, Color color)
        {
            // Top
            spriteBatch.Draw(pixel, new Rectangle(rect.X, rect.Y, rect.Width, thickness), color);
            // Bottom
            spriteBatch.Draw(pixel, new Rectangle(rect.X, rect.Y + rect.Height - thickness, rect.Width, thickness), color);
            // Left
            spriteBatch.Draw(pixel, new Rectangle(rect.X, rect.Y, thickness, rect.Height), color);
            // Right
            spriteBatch.Draw(pixel, new Rectangle(rect.X + rect.Width - thickness, rect.Y, thickness, rect.Height), color);
        }
    }

    /// <summary>
    /// Represents a menu in the menu system
    /// </summary>
    public class Menu
    {
        private List<Button> _buttons;
        private string _title;
        private SpriteFont _font;
        private Color _backgroundColor;
        private GraphicsDevice _graphicsDevice;
        private Texture2D _pixelTexture;
        private bool _isTransparent;

        /// <summary>
        /// Creates a new menu
        /// </summary>
        /// <param name="title">The menu's title</param>
        /// <param name="font">The font to use for the title and buttons</param>
        /// <param name="graphicsDevice">The graphics device for getting viewport dimensions</param>
        /// <param name="pixelTexture">The pixel texture for drawing</param>
        /// <param name="isTransparent">Whether the menu background should be transparent</param>
        public Menu(string title, SpriteFont font, GraphicsDevice graphicsDevice, Texture2D pixelTexture, bool isTransparent = false)
        {
            _title = title;
            _font = font;
            _graphicsDevice = graphicsDevice;
            _pixelTexture = pixelTexture;
            _isTransparent = isTransparent;
            _buttons = new List<Button>();
            _backgroundColor = new Color(240, 240, 240);
        }

        /// <summary>
        /// Sets whether the menu background should be transparent
        /// </summary>
        /// <param name="isTransparent">True for transparent background, false for solid</param>
        public void SetTransparent(bool isTransparent)
        {
            _isTransparent = isTransparent;
        }

        /// <summary>
        /// Adds a button to the menu
        /// </summary>
        /// <param name="text">The text to display on the button</param>
        /// <param name="onClick">The action to perform when the button is clicked</param>
        public void AddButton(string text, Action onClick)
        {
            // Calculate the position of the button based on the number of buttons already in the menu
            int buttonY = 100 + _buttons.Count * 60;
            
            // Create the button
            Button button = new Button(
                new Rectangle(100, buttonY, 600, 50),
                text,
                _font,
                onClick,
                _pixelTexture
            );
            
            // Add the button to the list
            _buttons.Add(button);
        }
        
        /// <summary>
        /// Adds a button to the menu with a callback that receives the button instance
        /// </summary>
        /// <param name="text">The text to display on the button</param>
        /// <param name="onClickWithButton">The action to perform when the button is clicked, receiving the button instance</param>
        public void AddButton(string text, Action<Button> onClickWithButton)
        {
            // Calculate the position of the button based on the number of buttons already in the menu
            int buttonY = 100 + _buttons.Count * 60;
            
            // Create the button
            Button button = new Button(
                new Rectangle(100, buttonY, 600, 50),
                text,
                _font,
                onClickWithButton,
                _pixelTexture
            );
            
            // Add the button to the list
            _buttons.Add(button);
        }

        /// <summary>
        /// Updates the menu
        /// </summary>
        /// <param name="mouseState">Current mouse state</param>
        /// <param name="prevMouseState">Previous mouse state</param>
        public void Update(MouseState mouseState, MouseState prevMouseState)
        {
            foreach (var button in _buttons)
            {
                button.Update(mouseState, prevMouseState);
            }
        }

        /// <summary>
        /// Draws the menu
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to draw with</param>
        /// <param name="viewport">The viewport dimensions</param>
        public void Draw(SpriteBatch spriteBatch, Viewport viewport)
        {
            // Draw menu background with appropriate transparency
            Color bgColor = _backgroundColor;
            if (_isTransparent)
            {
                // Use a very transparent background in test mode
                bgColor = new Color(240, 240, 240, 150) * (1.0f/255.0f);
            }
            
            spriteBatch.Draw(
                _pixelTexture, 
                new Rectangle(0, 0, viewport.Width, viewport.Height), 
                bgColor
            );
            
            // Draw menu title
            Vector2 titleSize = _font.MeasureString(_title);
            Vector2 titlePosition = new Vector2(
                (viewport.Width - titleSize.X) / 2,
                30
            );
            
            // Draw title with shadow for better visibility
            spriteBatch.DrawString(_font, _title, titlePosition + new Vector2(1, 1), Color.Black * 0.7f);
            spriteBatch.DrawString(_font, _title, titlePosition, Color.Black);
            
            // Draw buttons
            foreach (var button in _buttons)
            {
                button.Draw(spriteBatch);
            }
        }
    }

    /// <summary>
    /// Manages the menu system
    /// </summary>
    public class MenuSystem
    {
        private Dictionary<string, Menu> _menus;
        private string _currentMenu;
        private SpriteFont _font;
        private MouseState _prevMouseState;
        private GraphicsDevice _graphicsDevice;
        private Texture2D _pixelTexture;
        
        // Test mode settings
        public bool ShowHexGrid { get; private set; } = true;
        public bool ShowTestShips { get; private set; } = true;
        public bool InTestMode { get; private set; } = false;
        
        // Events
        public event Action? OnStartGame;
        public event Action? OnRunTests;
        public event Action<string>? OnTestSettingChanged;
        
        // New events for menu navigation
        public event Action? OnNewCharacter;
        public event Action? OnLoadCharacter;
        public event Action? OnInstantAction;
        public event Action? OnPlayerSetup;
        public event Action? OnBattleSetup;
        public event Action? OnStartBattle;
        public event Action<string, int, int, int>? OnCreateObject;
        public event Action<int, int, int, int>? OnMoveObject;
        public event Action<int>? OnDeleteObject;

        /// <summary>
        /// Creates a new menu system
        /// </summary>
        /// <param name="font">The font to use for menus and buttons</param>
        /// <param name="graphicsDevice">The graphics device for getting viewport dimensions</param>
        public MenuSystem(SpriteFont font, GraphicsDevice graphicsDevice)
        {
            _font = font;
            _graphicsDevice = graphicsDevice;
            _menus = new Dictionary<string, Menu>();
            _prevMouseState = Mouse.GetState();
            
            // Create a pixel texture for drawing
            _pixelTexture = new Texture2D(graphicsDevice, 1, 1);
            _pixelTexture.SetData(new[] { Color.White });
            
            // Create all menus
            CreateMainMenu();
            CreateNewCharacterMenu();
            CreateLoadCharacterMenu();
            CreateCampaignMenu();
            CreateBattleSetupMenu();
            CreatePlayerSetupMenu();
            CreateTestMenu();
            
            // Set the current menu to the main menu
            _currentMenu = "Main";
        }

        /// <summary>
        /// Creates the main menu
        /// </summary>
        private void CreateMainMenu()
        {
            Menu mainMenu = new Menu("SpaceWar", _font, _graphicsDevice, _pixelTexture);
            
            mainMenu.AddButton("New Character", () => {
                _currentMenu = "NewCharacter";
            });
            
            mainMenu.AddButton("Load Character", () => {
                _currentMenu = "LoadCharacter";
            });
            
            mainMenu.AddButton("Instant Action", () => {
                // For now, do nothing
                Console.WriteLine("Instant Action selected - not implemented yet");
            });
            
            mainMenu.AddButton("Tests", () => {
                _currentMenu = "Tests";
                InTestMode = true;
                OnRunTests?.Invoke();
            });
            
            mainMenu.AddButton("Quit", () => {
                Environment.Exit(0);
            });
            
            _menus.Add("Main", mainMenu);
        }
        
        /// <summary>
        /// Creates the new character menu
        /// </summary>
        private void CreateNewCharacterMenu()
        {
            Menu newCharacterMenu = new Menu("New Character", _font, _graphicsDevice, _pixelTexture);
            
            // For now, just a placeholder for themes
            newCharacterMenu.AddButton("Federation Theme", () => {
                Console.WriteLine("Federation Theme selected - not implemented yet");
                _currentMenu = "Campaign";
            });
            
            newCharacterMenu.AddButton("Klingon Theme", () => {
                Console.WriteLine("Klingon Theme selected - not implemented yet");
                _currentMenu = "Campaign";
            });
            
            newCharacterMenu.AddButton("Romulan Theme", () => {
                Console.WriteLine("Romulan Theme selected - not implemented yet");
                _currentMenu = "Campaign";
            });
            
            newCharacterMenu.AddButton("Cancel", () => {
                _currentMenu = "Main";
            });
            
            _menus.Add("NewCharacter", newCharacterMenu);
        }
        
        /// <summary>
        /// Creates the load character menu
        /// </summary>
        private void CreateLoadCharacterMenu()
        {
            Menu loadCharacterMenu = new Menu("Load Character", _font, _graphicsDevice, _pixelTexture);
            
            // For now, just placeholder characters
            loadCharacterMenu.AddButton("Character 1", () => {
                Console.WriteLine("Character 1 selected - not implemented yet");
                _currentMenu = "Campaign";
            });
            
            loadCharacterMenu.AddButton("Character 2", () => {
                Console.WriteLine("Character 2 selected - not implemented yet");
                _currentMenu = "Campaign";
            });
            
            loadCharacterMenu.AddButton("Character 3", () => {
                Console.WriteLine("Character 3 selected - not implemented yet");
                _currentMenu = "Campaign";
            });
            
            loadCharacterMenu.AddButton("Cancel", () => {
                _currentMenu = "Main";
            });
            
            _menus.Add("LoadCharacter", loadCharacterMenu);
        }
        
        /// <summary>
        /// Creates the campaign menu
        /// </summary>
        private void CreateCampaignMenu()
        {
            Menu campaignMenu = new Menu("Campaign", _font, _graphicsDevice, _pixelTexture);
            
            campaignMenu.AddButton("New Battle", () => {
                _currentMenu = "BattleSetup";
            });
            
            campaignMenu.AddButton("Player Setup", () => {
                _currentMenu = "PlayerSetup";
            });
            
            campaignMenu.AddButton("View Statistics", () => {
                Console.WriteLine("View Statistics selected - not implemented yet");
            });
            
            campaignMenu.AddButton("Save Character", () => {
                Console.WriteLine("Save Character selected - not implemented yet");
            });
            
            campaignMenu.AddButton("Return to Main Menu", () => {
                _currentMenu = "Main";
            });
            
            _menus.Add("Campaign", campaignMenu);
        }
        
        /// <summary>
        /// Creates the battle setup menu
        /// </summary>
        private void CreateBattleSetupMenu()
        {
            Menu battleSetupMenu = new Menu("Battle Setup", _font, _graphicsDevice, _pixelTexture);
            
            battleSetupMenu.AddButton("Team Battle: OFF", (Button button) => {
                // Toggle button text
                if (button.Text.Contains("OFF"))
                {
                    button.Text = "Team Battle: ON";
                }
                else
                {
                    button.Text = "Team Battle: OFF";
                }
            });
            
            battleSetupMenu.AddButton("AI Opponent: Easy", (Button button) => {
                // Cycle through difficulty levels
                if (button.Text.Contains("Easy"))
                {
                    button.Text = "AI Opponent: Medium";
                }
                else if (button.Text.Contains("Medium"))
                {
                    button.Text = "AI Opponent: Hard";
                }
                else
                {
                    button.Text = "AI Opponent: Easy";
                }
            });
            
            battleSetupMenu.AddButton("Start Battle", () => {
                OnStartGame?.Invoke();
            });
            
            battleSetupMenu.AddButton("Cancel", () => {
                _currentMenu = "Campaign";
            });
            
            _menus.Add("BattleSetup", battleSetupMenu);
        }
        
        /// <summary>
        /// Creates the player setup menu
        /// </summary>
        private void CreatePlayerSetupMenu()
        {
            Menu playerSetupMenu = new Menu("Player Setup", _font, _graphicsDevice, _pixelTexture);
            
            playerSetupMenu.AddButton("Change Name", () => {
                Console.WriteLine("Change Name selected - not implemented yet");
            });
            
            playerSetupMenu.AddButton("Change Ship Name", () => {
                Console.WriteLine("Change Ship Name selected - not implemented yet");
            });
            
            playerSetupMenu.AddButton("Change Race", () => {
                Console.WriteLine("Change Race selected - not implemented yet");
            });
            
            playerSetupMenu.AddButton("Adjust Stats", () => {
                Console.WriteLine("Adjust Stats selected - not implemented yet");
            });
            
            playerSetupMenu.AddButton("Cancel", () => {
                _currentMenu = "Campaign";
            });
            
            _menus.Add("PlayerSetup", playerSetupMenu);
        }

        /// <summary>
        /// Creates the test menu
        /// </summary>
        private void CreateTestMenu()
        {
            Menu testMenu = new Menu("Tests", _font, _graphicsDevice, _pixelTexture, true);
            
            testMenu.AddButton("Draw Hex Grid", () => {
                ShowHexGrid = true;
                string message = "Hex grid enabled";
                Console.WriteLine(message);
                OnTestSettingChanged?.Invoke(message);
            });
            
            testMenu.AddButton("Hide Hex Grid", () => {
                ShowHexGrid = false;
                string message = "Hex grid disabled";
                Console.WriteLine(message);
                OnTestSettingChanged?.Invoke(message);
            });
            
            testMenu.AddButton("Draw Test Ships", () => {
                ShowTestShips = true;
                string message = "Test ships enabled";
                Console.WriteLine(message);
                OnTestSettingChanged?.Invoke(message);
            });
            
            testMenu.AddButton("Hide Test Ships", () => {
                ShowTestShips = false;
                string message = "Test ships disabled";
                Console.WriteLine(message);
                OnTestSettingChanged?.Invoke(message);
            });
            
            testMenu.AddButton("Create Federation Ship", () => {
                string message = "Creating federation ship at 1,1";
                Console.WriteLine(message);
                OnTestSettingChanged?.Invoke(message);
                OnCreateObject?.Invoke("federation", 1, 1, 180);
            });
            
            testMenu.AddButton("Move Ship to Bottom Right", () => {
                string message = "Moving ship to bottom right";
                Console.WriteLine(message);
                OnTestSettingChanged?.Invoke(message);
                OnMoveObject?.Invoke(0, 9, 9, 2);
            });
            
            testMenu.AddButton("Delete Ship", () => {
                string message = "Deleting ship";
                Console.WriteLine(message);
                OnTestSettingChanged?.Invoke(message);
                OnDeleteObject?.Invoke(0);
            });
            
            testMenu.AddButton("Return to Main Menu", () => {
                _currentMenu = "Main";
                InTestMode = false;
            });
            
            _menus.Add("Tests", testMenu);
        }

        /// <summary>
        /// Updates the menu system
        /// </summary>
        public void Update()
        {
            MouseState mouseState = Mouse.GetState();
            
            if (_menus.ContainsKey(_currentMenu))
            {
                _menus[_currentMenu].Update(mouseState, _prevMouseState);
            }
            
            _prevMouseState = mouseState;
        }

        /// <summary>
        /// Draws the current menu
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to draw with</param>
        /// <param name="viewport">The viewport dimensions</param>
        public void Draw(SpriteBatch spriteBatch, Viewport viewport)
        {
            if (_menus.ContainsKey(_currentMenu))
            {
                _menus[_currentMenu].Draw(spriteBatch, viewport);
            }
        }
    }
} 