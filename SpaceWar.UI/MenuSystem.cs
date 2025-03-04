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
        private Action _onClick;
        private Texture2D _pixelTexture;

        /// <summary>
        /// Creates a new button
        /// </summary>
        /// <param name="bounds">The button's position and size</param>
        /// <param name="text">The button's text</param>
        /// <param name="font">The font to use for the text</param>
        /// <param name="onClick">The action to perform when clicked</param>
        /// <param name="pixelTexture">The pixel texture for drawing</param>
        public Button(Rectangle bounds, string text, SpriteFont font, Action onClick, Texture2D pixelTexture)
        {
            _bounds = bounds;
            _text = text;
            _font = font;
            _onClick = onClick;
            _pixelTexture = pixelTexture;
            _textColor = Color.Black;
            _backgroundColor = new Color(200, 200, 200, 255); // Fully opaque background
            _hoverColor = new Color(220, 220, 220, 255); // Fully opaque hover color
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
            _isHovered = _bounds.Contains(mouseState.Position);

            // Check if the button was clicked
            if (_isHovered && 
                mouseState.LeftButton == ButtonState.Released && 
                prevMouseState.LeftButton == ButtonState.Pressed)
            {
                _onClick?.Invoke();
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
        /// <param name="text">The button's text</param>
        /// <param name="onClick">The action to perform when clicked</param>
        public void AddButton(string text, Action onClick)
        {
            // Calculate button position based on the number of existing buttons
            int buttonWidth = 200;
            int buttonHeight = 40;
            int buttonSpacing = 10;
            int startY = 100; // Start position for the first button
            
            Rectangle bounds = new Rectangle(
                (_graphicsDevice.Viewport.Width - buttonWidth) / 2, // Center horizontally using actual viewport width
                startY + (_buttons.Count * (buttonHeight + buttonSpacing)),
                buttonWidth,
                buttonHeight
            );
            
            _buttons.Add(new Button(bounds, text, _font, onClick, _pixelTexture));
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
        
        // Test flags
        public bool ShowHexGrid { get; private set; } = true;
        public bool ShowTestShips { get; private set; } = true;
        public bool InTestMode { get; private set; } = false;
        
        // Events
        public event Action OnStartGame;
        public event Action OnRunTests;
        public event Action<string> OnTestSettingChanged;

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
            
            // Create menus
            CreateMainMenu();
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
            
            mainMenu.AddButton("Play Game", () => {
                OnStartGame?.Invoke();
            });
            
            mainMenu.AddButton("Tests", () => {
                _currentMenu = "Tests";
                InTestMode = true;
                
                // Make the test menu transparent
                if (_menus.ContainsKey("Tests"))
                {
                    _menus["Tests"].SetTransparent(true);
                }
                
                // Start the test mode
                OnRunTests?.Invoke();
            });
            
            mainMenu.AddButton("Exit", () => {
                Environment.Exit(0);
            });
            
            _menus.Add("Main", mainMenu);
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
            
            testMenu.AddButton("Back", () => {
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