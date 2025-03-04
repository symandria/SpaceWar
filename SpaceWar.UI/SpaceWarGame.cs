using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using SpaceWar.Core;
using System;
using System.Collections.Generic;
using System.IO;
using XnaColor = Microsoft.Xna.Framework.Color;
using XnaKeys = Microsoft.Xna.Framework.Input.Keys;
using XnaButtonState = Microsoft.Xna.Framework.Input.ButtonState;

namespace SpaceWar.UI
{
    /// <summary>
    /// Game state enum
    /// </summary>
    public enum GameStateType
    {
        Menu,
        Playing,
        GameOver
    }

    /// <summary>
    /// Main game class for SpaceWar
    /// </summary>
    public class SpaceWarGame : Game
    {
        private GraphicsDeviceManager _graphics;
        private SpriteBatch _spriteBatch;
        private GameState _gameState;
        private SpriteFont _font;
        private string _welcomeMessage = "Welcome to SpaceWar!";
        
        // Game state
        private GameStateType _currentState = GameStateType.Menu;
        
        // Menu system
        private MenuSystem _menuSystem;
        
        // Hex grid
        private HexGrid _hexGrid;
        private HexGridRenderer _hexGridRenderer;
        
        // Ship assets
        private Dictionary<string, Texture2D> _shipTextures;
        private List<GameObjectViewModel> _gameObjects;
        
        // Ship types to display
        private readonly string[] _shipTypes = { "borg", "federation", "klingon", "dominion", "tholian", "sentry" };
        
        // Debug info
        private bool _showDebugInfo = true;
        private string _debugInfo = "";

        // Pixel texture for drawing primitives
        private Texture2D _pixelTexture;

        /// <summary>
        /// Creates a new instance of the game
        /// </summary>
        public SpaceWarGame()
        {
            Console.WriteLine("SpaceWarGame constructor starting...");
            
            _graphics = new GraphicsDeviceManager(this);
            Content.RootDirectory = "Content";
            
            // Set window properties based on the monitor's dimensions
            // Get the current display mode
            DisplayMode currentDisplay = GraphicsAdapter.DefaultAdapter.CurrentDisplayMode;
            
            // Use 80% of the monitor's height for the window height
            int windowHeight = (int)(currentDisplay.Height * 0.8f);
            // Make the window square to match the original game's aspect ratio
            int windowWidth = windowHeight;
            
            // If the window is too wide for the monitor, adjust it
            if (windowWidth > currentDisplay.Width * 0.9f)
            {
                windowWidth = (int)(currentDisplay.Width * 0.9f);
                windowHeight = windowWidth; // Keep it square
            }
            
            _graphics.PreferredBackBufferWidth = windowWidth;
            _graphics.PreferredBackBufferHeight = windowHeight;
            
            IsMouseVisible = true;
            
            _gameState = new GameState();
            
            // Create hex grid (14 rows, 11 columns based on the original game)
            _hexGrid = new HexGrid(14, 11);
            
            // Initialize collections
            _shipTextures = new Dictionary<string, Texture2D>();
            _gameObjects = new List<GameObjectViewModel>();
            
            Console.WriteLine($"Window size set to {windowWidth}x{windowHeight}");
            Console.WriteLine("SpaceWarGame constructor completed.");
        }

        /// <summary>
        /// Initializes the game
        /// </summary>
        protected override void Initialize()
        {
            Console.WriteLine("Initialize starting...");
            
            // Set window title
            Window.Title = "SpaceWar";
            
            // Center the window on the screen
            Window.Position = new Point(
                (GraphicsAdapter.DefaultAdapter.CurrentDisplayMode.Width - Window.ClientBounds.Width) / 2,
                (GraphicsAdapter.DefaultAdapter.CurrentDisplayMode.Height - Window.ClientBounds.Height) / 2
            );
            
            // Create the hex grid
            _hexGrid = new HexGrid(10, 10);
            
            // Create the menu system
            _menuSystem = new MenuSystem(_font, GraphicsDevice);
            
            // Subscribe to menu events
            _menuSystem.OnStartGame += StartGame;
            _menuSystem.OnRunTests += RunTests;
            _menuSystem.OnTestSettingChanged += (message) => {
                _debugInfo += message + "\n";
            };
            
            // Subscribe to object manipulation events
            _menuSystem.OnCreateObject += CreateObject;
            _menuSystem.OnMoveObject += MoveObject;
            _menuSystem.OnDeleteObject += DeleteObject;
            
            // Create empty lists for game objects
            _gameObjects = new List<GameObjectViewModel>();
            _shipTextures = new Dictionary<string, Texture2D>();
            
            base.Initialize();
            
            Console.WriteLine("Initialize completed.");
        }

        /// <summary>
        /// Loads game content
        /// </summary>
        protected override void LoadContent()
        {
            Console.WriteLine("LoadContent starting...");
            
            _spriteBatch = new SpriteBatch(GraphicsDevice);
            
            // Create a pixel texture for drawing primitives
            _pixelTexture = new Texture2D(GraphicsDevice, 1, 1);
            _pixelTexture.SetData(new[] { Color.White });
            
            // Create hex grid renderer
            // The scale parameter is no longer used as the renderer calculates its own scale
            _hexGridRenderer = new HexGridRenderer(_hexGrid, GraphicsDevice, 1.0f);
            
            // Load font
            try
            {
                _font = Content.Load<SpriteFont>("Font");
                Console.WriteLine("Font loaded successfully");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading font: {ex.Message}");
                // Continue without the font
            }
            
            // Initialize menu system
            _menuSystem = new MenuSystem(_font, GraphicsDevice);
            _menuSystem.OnStartGame += StartGame;
            _menuSystem.OnRunTests += () => {
                Console.WriteLine("Test mode activated");
                _debugInfo += "Test mode activated\n";
            };
            _menuSystem.OnTestSettingChanged += (message) => {
                _debugInfo += message + "\n";
            };
            
            // Load ship textures
            LoadShipTextures();
            
            // Create game objects for each ship type
            CreateShipObjects();
            
            Console.WriteLine("LoadContent completed.");
        }
        
        /// <summary>
        /// Loads the ship textures from the data/themes/classic folder
        /// </summary>
        private void LoadShipTextures()
        {
            // Get the current directory
            string currentDir = Directory.GetCurrentDirectory();
            Console.WriteLine($"Current directory: {currentDir}");
            
            // Check if we need to go up one level (if we're in the bin directory)
            if (currentDir.Contains("bin"))
            {
                var parent = Directory.GetParent(currentDir);
                if (parent?.Parent?.Parent != null)
                {
                    currentDir = parent.Parent.Parent.FullName;
                    Console.WriteLine($"Adjusted directory: {currentDir}");
                }
                else
                {
                    Console.WriteLine("Could not navigate up from bin directory - parent directories not found");
                }
            }
            
            // Create a blank texture for testing
            Texture2D blankTexture = new Texture2D(GraphicsDevice, 8, 8);
            Color[] colorData = new Color[8 * 8];
            for (int i = 0; i < colorData.Length; i++)
            {
                colorData[i] = Color.Black;
            }
            blankTexture.SetData(colorData);
            
            // Check if the data directory exists
            string dataPath = Path.Combine(currentDir, "..", "data");
            if (!Directory.Exists(dataPath))
            {
                dataPath = Path.Combine(currentDir, "data");
            }
            
            if (!Directory.Exists(dataPath))
            {
                Console.WriteLine($"Data directory not found: {dataPath}");
                
                // Use blank textures for testing
                foreach (string shipType in _shipTypes)
                {
                    _shipTextures.Add(shipType, blankTexture);
                    Console.WriteLine($"Added blank texture for {shipType}");
                }
                
                _debugInfo += $"Data directory not found: {dataPath}\n";
                return;
            }
            
            string themePath = Path.Combine(dataPath, "themes", "classic");
            if (!Directory.Exists(themePath))
            {
                Console.WriteLine($"Theme directory not found: {themePath}");
                
                // Use blank textures for testing
                foreach (string shipType in _shipTypes)
                {
                    _shipTextures.Add(shipType, blankTexture);
                    Console.WriteLine($"Added blank texture for {shipType}");
                }
                
                _debugInfo += $"Theme directory not found: {themePath}\n";
                return;
            }
            
            Console.WriteLine($"Theme directory found: {themePath}");
            _debugInfo += $"Theme directory: {themePath}\n";
            
            foreach (string shipType in _shipTypes)
            {
                string shipImagePath = Path.Combine(themePath, $"{shipType}.png");
                
                if (!File.Exists(shipImagePath))
                {
                    Console.WriteLine($"Ship image not found: {shipImagePath}");
                    _shipTextures.Add(shipType, blankTexture);
                    _debugInfo += $"Ship image not found: {shipImagePath}\n";
                    continue;
                }
                
                try
                {
                    using (FileStream fileStream = new FileStream(shipImagePath, FileMode.Open))
                    {
                        // Load the texture with proper transparency
                        Texture2D texture = Texture2D.FromStream(GraphicsDevice, fileStream);
                        
                        // Set the texture to use point sampling for sharp pixel art
                        GraphicsDevice.SamplerStates[0] = SamplerState.PointClamp;
                        
                        // The PNG files might have a colorkey for transparency
                        // We need to convert any magenta pixels (255, 0, 255) to transparent
                        Color[] textureData = new Color[texture.Width * texture.Height];
                        texture.GetData(textureData);
                        
                        for (int i = 0; i < textureData.Length; i++)
                        {
                            if (textureData[i].R == 255 && textureData[i].G == 0 && textureData[i].B == 255)
                            {
                                textureData[i] = Color.Transparent;
                            }
                        }
                        
                        texture.SetData(textureData);
                        _shipTextures.Add(shipType, texture);
                        
                        Console.WriteLine($"Loaded texture for {shipType} - Size: {texture.Width}x{texture.Height}");
                        _debugInfo += $"Loaded texture for {shipType} - Size: {texture.Width}x{texture.Height}\n";
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading texture for {shipType}: {ex.Message}");
                    _shipTextures.Add(shipType, blankTexture);
                    _debugInfo += $"Error loading texture for {shipType}: {ex.Message}\n";
                }
            }
        }
        
        /// <summary>
        /// Creates game objects for each ship type
        /// </summary>
        private void CreateShipObjects()
        {
            // Clear any existing objects
            _gameObjects.Clear();
            
            // Create 6 ships of each type in different rows, with different rotations
            for (int i = 0; i < _shipTypes.Length; i++)
            {
                string shipType = _shipTypes[i];
                
                // Skip if the texture wasn't loaded
                if (!_shipTextures.ContainsKey(shipType))
                {
                    Console.WriteLine($"Skipping {shipType} - texture not loaded");
                    _debugInfo += $"Skipping {shipType} - texture not loaded\n";
                    continue;
                }
                
                Console.WriteLine($"Creating objects for {shipType}");
                _debugInfo += $"Creating objects for {shipType}\n";
                
                // Place 6 ships in a row, each with a different rotation
                for (int j = 0; j < 6; j++)
                {
                    int row = i + 2; // Start from row 2
                    int column = j * 2 + 1; // Space them out
                    int rotation = j * 60; // 0, 60, 120, 180, 240, 300 degrees
                    
                    // Adjust column if needed for odd rows
                    if (column > _hexGrid.GetMaxColumnsForRow(row))
                    {
                        Console.WriteLine($"Skipping {shipType} at ({row}, {column}) - column out of range");
                        _debugInfo += $"Skipping {shipType} at ({row}, {column}) - column out of range\n";
                        continue;
                    }
                    
                    GameObjectViewModel shipObject = new GameObjectViewModel(
                        _shipTextures[shipType],
                        row,
                        column,
                        rotation
                    );
                    
                    _gameObjects.Add(shipObject);
                    Console.WriteLine($"Added {shipType} at ({row}, {column}) with rotation {rotation}");
                    _debugInfo += $"Added {shipType} at ({row}, {column}) with rotation {rotation}\n";
                }
            }
            
            Console.WriteLine($"Created {_gameObjects.Count} game objects");
            _debugInfo += $"Created {_gameObjects.Count} game objects\n";
        }

        /// <summary>
        /// Updates the game state
        /// </summary>
        protected override void Update(GameTime gameTime)
        {
            // Exit on Escape key
            if (Keyboard.GetState().IsKeyDown(Keys.Escape))
            {
                Console.WriteLine("Escape key pressed. Exiting...");
                Exit();
            }
            
            // Toggle debug info on F1
            if (Keyboard.GetState().IsKeyDown(Keys.F1) && !_prevKeyboardState.IsKeyDown(Keys.F1))
            {
                _showDebugInfo = !_showDebugInfo;
            }
            
            // Update based on current state
            switch (_currentState)
            {
                case GameStateType.Menu:
                    _menuSystem.Update();
                    break;
                    
                case GameStateType.Playing:
                    UpdateGame(gameTime);
                    break;
                    
                case GameStateType.GameOver:
                    // TODO: Handle game over state
                    break;
            }
            
            _prevKeyboardState = Keyboard.GetState();

            base.Update(gameTime);
        }
        
        /// <summary>
        /// Updates the game when in Playing state
        /// </summary>
        private void UpdateGame(GameTime gameTime)
        {
            // Update game objects
            for (int i = 0; i < _gameObjects.Count; i++)
            {
                GameObjectViewModel gameObject = _gameObjects[i];
                
                // Update movement
                if (gameObject.IsMoving)
                {
                    // Calculate the distance to the target
                    Vector2 direction = gameObject.TargetPosition - gameObject.Position;
                    float distance = direction.Length();
                    
                    // If we're close enough, snap to the target position
                    if (distance < 0.1f)
                    {
                        gameObject.Position = gameObject.TargetPosition;
                        gameObject.IsMoving = false;
                        Console.WriteLine($"Object {i} reached target position");
                        _debugInfo += $"Object {i} reached target position\n";
                    }
                    else
                    {
                        // Normalize the direction and move towards the target
                        direction.Normalize();
                        
                        // Move at the specified speed
                        float moveAmount = gameObject.Speed * (float)gameTime.ElapsedGameTime.TotalSeconds;
                        gameObject.Position += direction * moveAmount;
                        
                        // Smoothly rotate towards the target rotation
                        float rotationDifference = gameObject.TargetRotation - gameObject.Rotation;
                        
                        // Normalize the rotation difference to be between -PI and PI
                        while (rotationDifference > MathHelper.Pi)
                            rotationDifference -= MathHelper.TwoPi;
                        while (rotationDifference < -MathHelper.Pi)
                            rotationDifference += MathHelper.TwoPi;
                        
                        // Apply a portion of the rotation difference
                        gameObject.Rotation += rotationDifference * 0.1f;
                    }
                }
            }
            
            // Return to menu on M key
            if (Keyboard.GetState().IsKeyDown(Keys.M) && !_prevKeyboardState.IsKeyDown(Keys.M))
            {
                ReturnToMenu();
            }
        }
        
        /// <summary>
        /// Returns to the main menu
        /// </summary>
        private void ReturnToMenu()
        {
            _currentState = GameStateType.Menu;
            Console.WriteLine("Returned to menu");
            _debugInfo += "Returned to menu\n";
        }
        
        private KeyboardState _prevKeyboardState;

        /// <summary>
        /// Draws the game
        /// </summary>
        protected override void Draw(GameTime gameTime)
        {
            GraphicsDevice.Clear(Color.White);
            
            // Use point sampling for sharper pixel art
            _spriteBatch.Begin(samplerState: SamplerState.PointClamp);
            
            // Draw based on current state
            switch (_currentState)
            {
                case GameStateType.Menu:
                    // Always draw game elements in test mode
                    if (_menuSystem.InTestMode)
                    {
                        // Draw game elements first
                        if (_menuSystem.ShowHexGrid)
                        {
                            _hexGridRenderer.Draw(_spriteBatch);
                        }
                        
                        if (_menuSystem.ShowTestShips)
                        {
                            foreach (var gameObject in _gameObjects)
                            {
                                gameObject.Draw(_spriteBatch, _hexGridRenderer);
                            }
                        }
                        
                        // Draw test status
                        if (_font != null)
                        {
                            string testInfo = $"Hex Grid: {(_menuSystem.ShowHexGrid ? "Visible" : "Hidden")} | Ships: {(_menuSystem.ShowTestShips ? "Visible" : "Hidden")}";
                            Vector2 textSize = _font.MeasureString(testInfo);
                            Vector2 position = new Vector2(
                                (GraphicsDevice.Viewport.Width - textSize.X) / 2,
                                GraphicsDevice.Viewport.Height - 50);
                            
                            // Draw with a shadow for better visibility
                            _spriteBatch.DrawString(_font, testInfo, position + new Vector2(1, 1), Color.Black * 0.5f);
                            _spriteBatch.DrawString(_font, testInfo, position, Color.Blue);
                        }
                    }
                    
                    // Then draw the menu on top with semi-transparency in test mode
                    _menuSystem.Draw(_spriteBatch, GraphicsDevice.Viewport);
                    break;
                    
                case GameStateType.Playing:
                    DrawGame();
                    break;
                    
                case GameStateType.GameOver:
                    // TODO: Draw game over screen
                    break;
            }
            
            // Draw debug info if enabled
            if (_showDebugInfo && !string.IsNullOrEmpty(_debugInfo) && _font != null)
            {
                Vector2 debugPosition = new Vector2(10, 50);
                _spriteBatch.DrawString(_font, _debugInfo, debugPosition, Color.Red, 0f, Vector2.Zero, 0.5f, SpriteEffects.None, 0f);
            }
            
            _spriteBatch.End();
            
            base.Draw(gameTime);
        }
        
        /// <summary>
        /// Draws the game when in Playing state
        /// </summary>
        private void DrawGame()
        {
            // Draw hex grid
            _hexGridRenderer.Draw(_spriteBatch);
            
            // Draw game objects
            foreach (var gameObject in _gameObjects)
            {
                gameObject.Draw(_spriteBatch, _hexGridRenderer);
            }
            
            // Draw welcome message
            if (_font != null)
            {
                Vector2 textSize = _font.MeasureString(_welcomeMessage);
                Vector2 position = new Vector2(
                    (GraphicsDevice.Viewport.Width - textSize.X) / 2,
                    10 * (GraphicsDevice.Viewport.Height / 160f)); // Scale the top margin
                
                _spriteBatch.DrawString(_font, _welcomeMessage, position, Color.Black);
                
                // Draw instructions
                string instructions = "Press M to return to menu";
                Vector2 instructionsSize = _font.MeasureString(instructions);
                Vector2 instructionsPosition = new Vector2(
                    (GraphicsDevice.Viewport.Width - instructionsSize.X) / 2,
                    GraphicsDevice.Viewport.Height - 30);
                
                _spriteBatch.DrawString(_font, instructions, instructionsPosition, Color.Black);
            }
        }
        
        /// <summary>
        /// Starts the game
        /// </summary>
        private void StartGame()
        {
            _currentState = GameStateType.Playing;
            Console.WriteLine("Game started");
            _debugInfo += "Game started\n";
        }
        
        /// <summary>
        /// Runs the test mode
        /// </summary>
        private void RunTests()
        {
            Console.WriteLine("Running tests");
            _debugInfo += "Running tests\n";
            
            // Load ship textures if not already loaded
            if (_shipTextures.Count == 0)
            {
                LoadShipTextures();
            }
            
            // Create ship objects if not already created
            if (_gameObjects.Count == 0)
            {
                CreateShipObjects();
            }
        }

        /// <summary>
        /// Creates a new game object
        /// </summary>
        /// <param name="shipType">The type of ship to create</param>
        /// <param name="col">The column position</param>
        /// <param name="row">The row position</param>
        /// <param name="rotation">The rotation in degrees</param>
        private void CreateObject(string shipType, int col, int row, int rotation)
        {
            Console.WriteLine($"Creating {shipType} at {col},{row} with rotation {rotation}");
            _debugInfo += $"Creating {shipType} at {col},{row} with rotation {rotation}\n";
            
            // Load textures if not already loaded
            if (_shipTextures.Count == 0)
            {
                LoadShipTextures();
            }
            
            // Create the game object
            GameObjectViewModel gameObject = new GameObjectViewModel
            {
                Position = new Vector2(col, row),
                Rotation = MathHelper.ToRadians(rotation),
                Texture = _shipTextures.ContainsKey(shipType) ? _shipTextures[shipType] : _pixelTexture
            };
            
            // Add the game object to the list
            _gameObjects.Add(gameObject);
            
            Console.WriteLine($"Created object with ID {_gameObjects.Count - 1}");
            _debugInfo += $"Created object with ID {_gameObjects.Count - 1}\n";
        }
        
        /// <summary>
        /// Moves a game object
        /// </summary>
        /// <param name="objectId">The ID of the object to move</param>
        /// <param name="targetCol">The target column</param>
        /// <param name="targetRow">The target row</param>
        /// <param name="speed">The speed of movement</param>
        private void MoveObject(int objectId, int targetCol, int targetRow, int speed)
        {
            if (objectId < 0 || objectId >= _gameObjects.Count)
            {
                Console.WriteLine($"Invalid object ID: {objectId}");
                _debugInfo += $"Invalid object ID: {objectId}\n";
                return;
            }
            
            GameObjectViewModel gameObject = _gameObjects[objectId];
            
            Console.WriteLine($"Moving object {objectId} to {targetCol},{targetRow} at speed {speed}");
            _debugInfo += $"Moving object {objectId} to {targetCol},{targetRow} at speed {speed}\n";
            
            // Set the target position
            gameObject.TargetPosition = new Vector2(targetCol, targetRow);
            gameObject.Speed = speed;
            gameObject.IsMoving = true;
            
            // Calculate the direction to face
            Vector2 direction = gameObject.TargetPosition - gameObject.Position;
            if (direction != Vector2.Zero)
            {
                direction.Normalize();
                gameObject.TargetRotation = (float)Math.Atan2(direction.Y, direction.X);
            }
        }
        
        /// <summary>
        /// Deletes a game object
        /// </summary>
        /// <param name="objectId">The ID of the object to delete</param>
        private void DeleteObject(int objectId)
        {
            if (objectId < 0 || objectId >= _gameObjects.Count)
            {
                Console.WriteLine($"Invalid object ID: {objectId}");
                _debugInfo += $"Invalid object ID: {objectId}\n";
                return;
            }
            
            Console.WriteLine($"Deleting object {objectId}");
            _debugInfo += $"Deleting object {objectId}\n";
            
            // Remove the game object from the list
            _gameObjects.RemoveAt(objectId);
        }
    }
} 