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
using System.Linq;

namespace SpaceWar.UI
{
    /// <summary>
    /// Represents an animation to be displayed on the screen
    /// </summary>
    public class Animation
    {
        public Texture2D Texture { get; }
        public Vector2 Position { get; }
        public float Scale { get; }
        public float Duration { get; set; }
        public float ElapsedTime { get; set; }
        public float Rotation { get; set; }
        public Color Color { get; set; }
        public bool IsComplete => ElapsedTime >= Duration;

        public Animation(Texture2D texture, Vector2 position, float scale, float duration, float rotation = 0f, Color? color = null)
        {
            Texture = texture;
            Position = position;
            Scale = scale;
            Duration = duration;
            ElapsedTime = 0f;
            Rotation = rotation;
            Color = color ?? Color.White;
        }

        public void Update(GameTime gameTime)
        {
            ElapsedTime += (float)gameTime.ElapsedGameTime.TotalSeconds;
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            // Calculate alpha based on remaining time (fade out at the end)
            float alpha = 1.0f;
            if (Duration > 0)
            {
                float remainingTime = Duration - ElapsedTime;
                if (remainingTime < 0.5f)
                {
                    alpha = remainingTime / 0.5f;
                }
            }

            // Apply alpha to the color
            Color drawColor = Color * alpha;

            // Draw the texture
            spriteBatch.Draw(
                Texture,
                Position,
                null,
                drawColor,
                Rotation,
                new Vector2(Texture.Width / 2f, Texture.Height / 2f), // Center origin
                Scale,
                SpriteEffects.None,
                0f
            );
        }
    }

    /// <summary>
    /// Manages animations in the game
    /// </summary>
    public class AnimationManager
    {
        private List<Animation> _animations = new List<Animation>();

        public void AddAnimation(Animation animation)
        {
            _animations.Add(animation);
        }

        public void Update(GameTime gameTime)
        {
            // Update all animations
            foreach (var animation in _animations)
            {
                animation.Update(gameTime);
            }

            // Remove completed animations
            _animations.RemoveAll(a => a.IsComplete);
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            foreach (var animation in _animations)
            {
                animation.Draw(spriteBatch);
            }
        }

        public void Clear()
        {
            _animations.Clear();
        }
    }

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
        
        // Animation manager
        private AnimationManager _animationManager;
        
        // Fixed timestep for animations (100 updates per second)
        private const float FIXED_TIMESTEP = 0.01f; // 1/100 second
        private float _accumulatedTime = 0f;

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
            
            // Create the hex grid with 14 rows, 11 columns based on the original game
            _hexGrid = new HexGrid(14, 11);
            
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
            
            // Initialize animation manager
            _animationManager = new AnimationManager();
            
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
            
            // Wire up all event handlers
            _menuSystem.OnStartGame += StartGame;
            _menuSystem.OnRunTests += RunTests;
            _menuSystem.OnTestSettingChanged += (message) => {
                Console.WriteLine($"Test setting changed: {message}");
                _debugInfo += message + "\n";
            };
            
            // Wire up object manipulation events
            _menuSystem.OnCreateObject += (shipType, col, row, rotation) => {
                Console.WriteLine($"OnCreateObject event triggered: {shipType} at {col},{row} with rotation {rotation}");
                CreateObject(shipType, col, row, rotation);
            };
            _menuSystem.OnMoveObject += MoveObject;
            _menuSystem.OnDeleteObject += DeleteObject;
            
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
            // Clear existing textures if any
            _shipTextures.Clear();
            
            // Get the current directory
            string currentDir = Directory.GetCurrentDirectory();
            Console.WriteLine($"Current directory: {currentDir}");
            _debugInfo += $"Current directory: {currentDir}\n";
            
            // Check if we need to go up one level (if we're in the bin directory)
            if (currentDir.Contains("bin"))
            {
                var parent = Directory.GetParent(currentDir);
                if (parent?.Parent?.Parent != null)
                {
                    currentDir = parent.Parent.Parent.FullName;
                    Console.WriteLine($"Adjusted directory: {currentDir}");
                    _debugInfo += $"Adjusted directory: {currentDir}\n";
                }
                else
                {
                    Console.WriteLine("Could not navigate up from bin directory - parent directories not found");
                    _debugInfo += "Could not navigate up from bin directory\n";
                }
            }
            
            // Create a blank texture for testing
            Texture2D blankTexture = new Texture2D(GraphicsDevice, 16, 16);
            Color[] colorData = new Color[16 * 16];
            for (int i = 0; i < colorData.Length; i++)
            {
                colorData[i] = Color.White; // Use white instead of black for better visibility
            }
            blankTexture.SetData(colorData);
            
            // Create a dictionary of colors for each ship type
            Dictionary<string, Color> shipColors = new Dictionary<string, Color>
            {
                { "borg", Color.Green },
                { "federation", Color.Blue },
                { "klingon", Color.Red },
                { "dominion", Color.Purple },
                { "tholian", Color.Orange },
                { "sentry", Color.Yellow }
            };
            
            // Try multiple possible paths for the data directory
            string[] possibleDataPaths = new string[]
            {
                Path.Combine(currentDir, "data"),
                Path.Combine(currentDir, "..", "data"),
                Path.Combine(currentDir, "..", "..", "data"),
                Path.Combine(currentDir, "..", "..", "..", "data")
            };
            
            string? dataPath = null;
            foreach (string path in possibleDataPaths)
            {
                Console.WriteLine($"Checking path: {path}");
                _debugInfo += $"Checking path: {path}\n";
                
                if (Directory.Exists(path))
                {
                    dataPath = path;
                    Console.WriteLine($"Found data directory: {dataPath}");
                    _debugInfo += $"Found data directory: {dataPath}\n";
                    break;
                }
            }
            
            if (dataPath == null)
            {
                Console.WriteLine("Data directory not found in any of the checked paths");
                _debugInfo += "Data directory not found\n";
                
                // Use blank textures for testing
                foreach (string shipType in _shipTypes)
                {
                    // Create a unique colored texture for each ship type
                    Texture2D shipTexture = new Texture2D(GraphicsDevice, 16, 16);
                    Color[] shipColorData = new Color[16 * 16];
                    Color shipColor = shipColors.ContainsKey(shipType) ? shipColors[shipType] : Color.White;
                    
                    for (int i = 0; i < shipColorData.Length; i++)
                    {
                        // Create a simple ship shape
                        int x = i % 16;
                        int y = i / 16;
                        
                        // Make a triangle shape
                        if ((x >= 8 - y/2 && x <= 8 + y/2) || (y >= 8 && y <= 12))
                        {
                            shipColorData[i] = shipColor;
                        }
                        else
                        {
                            shipColorData[i] = Color.Transparent;
                        }
                    }
                    shipTexture.SetData(shipColorData);
                    
                    _shipTextures.Add(shipType, shipTexture);
                    Console.WriteLine($"Added colored texture for {shipType}");
                    _debugInfo += $"Added colored texture for {shipType}\n";
                }
                
                return;
            }
            
            // Try to find the themes directory
            string themePath = Path.Combine(dataPath, "themes", "classic");
            if (!Directory.Exists(themePath))
            {
                // Try without the "classic" subdirectory
                themePath = Path.Combine(dataPath, "themes");
                if (!Directory.Exists(themePath))
                {
                    Console.WriteLine($"Theme directory not found: {themePath}");
                    _debugInfo += $"Theme directory not found: {themePath}\n";
                    
                    // Use blank textures for testing
                    foreach (string shipType in _shipTypes)
                    {
                        // Create a unique colored texture for each ship type
                        Texture2D shipTexture = new Texture2D(GraphicsDevice, 16, 16);
                        Color[] shipColorData = new Color[16 * 16];
                        Color shipColor = shipColors.ContainsKey(shipType) ? shipColors[shipType] : Color.White;
                        
                        for (int i = 0; i < shipColorData.Length; i++)
                        {
                            // Create a simple ship shape
                            int x = i % 16;
                            int y = i / 16;
                            
                            // Make a triangle shape
                            if ((x >= 8 - y/2 && x <= 8 + y/2) || (y >= 8 && y <= 12))
                            {
                                shipColorData[i] = shipColor;
                            }
                            else
                            {
                                shipColorData[i] = Color.Transparent;
                            }
                        }
                        shipTexture.SetData(shipColorData);
                        
                        _shipTextures.Add(shipType, shipTexture);
                        Console.WriteLine($"Added colored texture for {shipType}");
                        _debugInfo += $"Added colored texture for {shipType}\n";
                    }
                    
                    return;
                }
            }
            
            Console.WriteLine($"Theme directory found: {themePath}");
            _debugInfo += $"Theme directory: {themePath}\n";
            
            // List all files in the theme directory for debugging
            string[] files = Directory.GetFiles(themePath);
            Console.WriteLine($"Files in theme directory: {string.Join(", ", files)}");
            _debugInfo += $"Files in theme directory: {string.Join(", ", files)}\n";
            
            foreach (string shipType in _shipTypes)
            {
                string shipImagePath = Path.Combine(themePath, $"{shipType}.png");
                
                if (!File.Exists(shipImagePath))
                {
                    Console.WriteLine($"Ship image not found: {shipImagePath}");
                    
                    // Create a colored texture for this ship type
                    Texture2D shipTexture = new Texture2D(GraphicsDevice, 16, 16);
                    Color[] shipColorData = new Color[16 * 16];
                    Color shipColor = shipColors.ContainsKey(shipType) ? shipColors[shipType] : Color.White;
                    
                    for (int i = 0; i < shipColorData.Length; i++)
                    {
                        // Create a simple ship shape
                        int x = i % 16;
                        int y = i / 16;
                        
                        // Make a triangle shape
                        if ((x >= 8 - y/2 && x <= 8 + y/2) || (y >= 8 && y <= 12))
                        {
                            shipColorData[i] = shipColor;
                        }
                        else
                        {
                            shipColorData[i] = Color.Transparent;
                        }
                    }
                    shipTexture.SetData(shipColorData);
                    
                    _shipTextures.Add(shipType, shipTexture);
                    _debugInfo += $"Created fallback texture for {shipType}\n";
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
        /// Updates the game
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
            
            // Accumulate time for fixed timestep updates
            _accumulatedTime += (float)gameTime.ElapsedGameTime.TotalSeconds;
            
            // Perform fixed timestep updates (100 updates per second)
            while (_accumulatedTime >= FIXED_TIMESTEP)
            {
                // Update animations
                _animationManager.Update(new GameTime(gameTime.TotalGameTime, TimeSpan.FromSeconds(FIXED_TIMESTEP)));
                
                // Update based on current state
                switch (_currentState)
                {
                    case GameStateType.Menu:
                        _menuSystem.Update();
                        break;
                        
                    case GameStateType.Playing:
                        UpdateGame(new GameTime(gameTime.TotalGameTime, TimeSpan.FromSeconds(FIXED_TIMESTEP)));
                        break;
                        
                    case GameStateType.GameOver:
                        // TODO: Handle game over state
                        break;
                }
                
                _accumulatedTime -= FIXED_TIMESTEP;
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
            if (_gameObjects == null || _gameObjects.Count == 0)
            {
                return; // No objects to update
            }
            
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
                        Console.WriteLine($"Object {i} reached target position {gameObject.Position.X},{gameObject.Position.Y}");
                        _debugInfo += $"Object {i} reached target position {gameObject.Position.X},{gameObject.Position.Y}\n";
                    }
                    else
                    {
                        // Normalize the direction and move towards the target
                        direction.Normalize();
                        
                        // Calculate speed in hexes per second
                        // Speed 1.0 means 1 hex per second
                        float moveAmount = gameObject.Speed * (float)gameTime.ElapsedGameTime.TotalSeconds;
                        
                        // Limit the move amount to prevent overshooting
                        moveAmount = Math.Min(moveAmount, distance);
                        
                        // Update position
                        gameObject.Position += direction * moveAmount;
                        
                        // Log movement for debugging
                        if (i == 0 && gameTime.TotalGameTime.TotalSeconds % 1 < 0.1f) // Log once per second for object 0
                        {
                            Console.WriteLine($"Moving object {i}: Position={gameObject.Position.X},{gameObject.Position.Y}, Target={gameObject.TargetPosition.X},{gameObject.TargetPosition.Y}, Distance={distance}, Speed={gameObject.Speed} hexes/sec");
                        }
                        
                        // Smoothly rotate towards the target rotation
                        float rotationDifference = gameObject.TargetRotation - gameObject.Rotation;
                        
                        // Normalize the rotation difference to be between -PI and PI
                        while (rotationDifference > MathHelper.Pi)
                            rotationDifference -= MathHelper.TwoPi;
                        while (rotationDifference < -MathHelper.Pi)
                            rotationDifference += MathHelper.TwoPi;
                        
                        // Apply a portion of the rotation difference
                        // Rotate at a rate that completes in about 1 second
                        float rotationSpeed = 5.0f * (float)gameTime.ElapsedGameTime.TotalSeconds;
                        gameObject.Rotation += rotationDifference * rotationSpeed;
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
                    // If in test mode, draw the game elements underneath the menu
                    if (_menuSystem.InTestMode)
                    {
                        // Draw hex grid if enabled
                        if (_menuSystem.ShowHexGrid)
                        {
                            _hexGridRenderer.Draw(_spriteBatch);
                        }
                        
                        // Draw game objects if enabled
                        if (_menuSystem.ShowTestShips && _gameObjects != null)
                        {
                            foreach (var gameObject in _gameObjects)
                            {
                                gameObject.Draw(_spriteBatch, _hexGridRenderer);
                                
                                // Draw debug visualization if debug mode is enabled
                                if (_showDebugInfo)
                                {
                                    gameObject.DrawDebugVisualization(_spriteBatch, _hexGridRenderer, _pixelTexture);
                                }
                            }
                        }
                    }
                    
                    _menuSystem.Draw(_spriteBatch);
                    break;
                    
                case GameStateType.Playing:
                    DrawGame();
                    break;
                    
                case GameStateType.GameOver:
                    // TODO: Draw game over screen
                    break;
            }
            
            // Draw animations on top of everything else
            _animationManager.Draw(_spriteBatch);
            
            // Draw debug info if enabled
            if (_showDebugInfo)
            {
                DrawDebugInfo();
            }
            
            _spriteBatch.End();
            
            base.Draw(gameTime);
        }
        
        /// <summary>
        /// Draws the game when in Playing state
        /// </summary>
        private void DrawGame()
        {
            // Draw the hex grid
            _hexGridRenderer.Draw(_spriteBatch);
            
            // Draw game objects
            if (_gameObjects != null)
            {
                foreach (var gameObject in _gameObjects)
                {
                    gameObject.Draw(_spriteBatch, _hexGridRenderer);
                    
                    // Draw debug visualization if debug mode is enabled
                    if (_showDebugInfo)
                    {
                        gameObject.DrawDebugVisualization(_spriteBatch, _hexGridRenderer, _pixelTexture);
                    }
                }
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
                    GraphicsDevice.Viewport.Height - 30
                );
                
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
            
            // Enable test mode
            _menuSystem.InTestMode = true;
            
            // Load ship textures if not already loaded
            if (_shipTextures == null || _shipTextures.Count == 0)
            {
                Console.WriteLine("Loading ship textures for tests");
                _shipTextures = new Dictionary<string, Texture2D>();
                LoadShipTextures();
            }
            
            // Create ship objects if not already created
            if (_gameObjects == null || _gameObjects.Count == 0)
            {
                Console.WriteLine("Creating ship objects for tests");
                _gameObjects = new List<GameObjectViewModel>();
                CreateShipObjects();
            }
            
            // Make sure ships are visible
            _menuSystem.ShowTestShips = true;
            
            Console.WriteLine($"Test mode active with {_gameObjects.Count} ships");
            _debugInfo += $"Test mode active with {_gameObjects.Count} ships\n";
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
            Console.WriteLine($"CreateObject called: {shipType} at {col},{row} with rotation {rotation}");
            _debugInfo += $"CreateObject called: {shipType} at {col},{row} with rotation {rotation}\n";
            
            // Initialize the game objects list if it's null
            if (_gameObjects == null)
            {
                _gameObjects = new List<GameObjectViewModel>();
                Console.WriteLine("Initialized game objects list");
            }
            
            // Load textures if not already loaded
            if (_shipTextures == null || _shipTextures.Count == 0)
            {
                Console.WriteLine("No textures loaded, loading now...");
                _debugInfo += "No textures loaded, loading now...\n";
                _shipTextures = new Dictionary<string, Texture2D>();
                LoadShipTextures();
            }
            
            Console.WriteLine($"Available textures: {string.Join(", ", _shipTextures.Keys)}");
            _debugInfo += $"Available textures: {string.Join(", ", _shipTextures.Keys)}\n";
            
            // Create a simple white texture as fallback
            Texture2D shipTexture;
            
            // Try to get the requested ship texture
            if (_shipTextures.ContainsKey(shipType))
            {
                shipTexture = _shipTextures[shipType];
                Console.WriteLine($"Using texture for {shipType}");
            }
            else
            {
                Console.WriteLine($"Texture for {shipType} not found, creating fallback texture");
                
                // Create a fallback texture
                shipTexture = new Texture2D(GraphicsDevice, 16, 16);
                Color[] colorData = new Color[16 * 16];
                for (int i = 0; i < colorData.Length; i++)
                {
                    // Create a simple ship shape
                    int x = i % 16;
                    int y = i / 16;
                    
                    // Make a triangle shape
                    if ((x >= 8 - y/2 && x <= 8 + y/2) || (y >= 8 && y <= 12))
                    {
                        colorData[i] = Color.Red;
                    }
                    else
                    {
                        colorData[i] = Color.Transparent;
                    }
                }
                shipTexture.SetData(colorData);
                
                // Add it to the dictionary for future use
                _shipTextures[shipType] = shipTexture;
            }
            
            // Create the game object
            GameObjectViewModel gameObject = new GameObjectViewModel(
                shipTexture,
                row,
                col,
                MathHelper.ToRadians(rotation)
            );
            
            // Add the game object to the list
            _gameObjects.Add(gameObject);
            
            // Enable showing test ships and test mode
            _menuSystem.ShowTestShips = true;
            _menuSystem.InTestMode = true;
            
            Console.WriteLine($"Created object with ID {_gameObjects.Count - 1}, total objects: {_gameObjects.Count}");
            _debugInfo += $"Created object with ID {_gameObjects.Count - 1}, total objects: {_gameObjects.Count}\n";
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
            Console.WriteLine($"MoveObject called for ID {objectId} to position {targetCol},{targetRow} at speed {speed}");
            _debugInfo += $"MoveObject called for ID {objectId} to position {targetCol},{targetRow} at speed {speed}\n";
            
            // Validate object ID
            if (_gameObjects == null || _gameObjects.Count == 0)
            {
                Console.WriteLine("No game objects available to move");
                _debugInfo += "No game objects available to move\n";
                return;
            }
            
            if (objectId < 0 || objectId >= _gameObjects.Count)
            {
                Console.WriteLine($"Invalid object ID: {objectId}. Available objects: {_gameObjects.Count}");
                _debugInfo += $"Invalid object ID: {objectId}. Available objects: {_gameObjects.Count}\n";
                return;
            }
            
            // Get the game object
            GameObjectViewModel gameObject = _gameObjects[objectId];
            
            // Log current position
            Console.WriteLine($"Current position: {gameObject.Position.X},{gameObject.Position.Y}");
            _debugInfo += $"Current position: {gameObject.Position.X},{gameObject.Position.Y}\n";
            
            // Set the target position
            gameObject.TargetPosition = new Vector2(targetCol, targetRow);
            gameObject.Speed = Math.Max(0.5f, speed); // Ensure minimum speed
            gameObject.IsMoving = true;
            
            // Calculate the direction to face (in radians)
            Vector2 direction = gameObject.TargetPosition - gameObject.Position;
            if (direction != Vector2.Zero)
            {
                direction.Normalize();
                
                // Calculate the angle in radians
                float angle = (float)Math.Atan2(direction.Y, direction.X);
                
                // Set the target rotation
                gameObject.TargetRotation = angle;
                
                Console.WriteLine($"Direction: {direction.X},{direction.Y}, Target rotation: {angle} radians");
                _debugInfo += $"Direction: {direction.X},{direction.Y}, Target rotation: {angle} radians\n";
            }
            
            // Enable test mode and show ships
            _menuSystem.InTestMode = true;
            _menuSystem.ShowTestShips = true;
            
            Console.WriteLine($"Object {objectId} is now moving to {targetCol},{targetRow}");
            _debugInfo += $"Object {objectId} is now moving to {targetCol},{targetRow}\n";
        }
        
        /// <summary>
        /// Deletes a game object
        /// </summary>
        /// <param name="objectId">The ID of the object to delete</param>
        private void DeleteObject(int objectId)
        {
            if (_gameObjects == null || objectId < 0 || objectId >= _gameObjects.Count)
            {
                Console.WriteLine($"Invalid object ID: {objectId}");
                _debugInfo += $"Invalid object ID: {objectId}\n";
                return;
            }
            
            Console.WriteLine($"Deleting object {objectId}");
            _debugInfo += $"Deleting object {objectId}\n";
            
            // Remove the game object from the list immediately with no animation
            _gameObjects.RemoveAt(objectId);
        }

        /// <summary>
        /// Draws debug information
        /// </summary>
        private void DrawDebugInfo()
        {
            Vector2 debugPosition = new Vector2(10, 10);
            _spriteBatch.DrawString(_font, $"Game Objects: {(_gameObjects?.Count ?? 0)}", debugPosition, Color.Red, 0f, Vector2.Zero, 0.5f, SpriteEffects.None, 0f);
            
            Vector2 modePosition = new Vector2(10, 30);
            string modeText = $"Mode: {_currentState} | Test Mode: {_menuSystem.InTestMode} | Show Ships: {_menuSystem.ShowTestShips}";
            _spriteBatch.DrawString(_font, modeText, modePosition, Color.Red, 0f, Vector2.Zero, 0.5f, SpriteEffects.None, 0f);
            
            Vector2 fullDebugPosition = new Vector2(10, 50);
            _spriteBatch.DrawString(_font, _debugInfo, fullDebugPosition, Color.Red, 0f, Vector2.Zero, 0.5f, SpriteEffects.None, 0f);
        }

        /// <summary>
        /// Draws an animation at the specified coordinates
        /// </summary>
        /// <param name="coordinate">The hex coordinate (row, column)</param>
        /// <param name="animationTexture">The texture to use for the animation</param>
        /// <param name="scale">The scale of the animation</param>
        /// <param name="duration">The duration of the animation in seconds</param>
        /// <param name="rotation">Optional rotation in degrees</param>
        /// <param name="color">Optional color tint</param>
        public void DrawAnimation(Vector2 coordinate, Texture2D animationTexture, float scale, float duration, float rotation = 0f, Color? color = null)
        {
            // Convert hex coordinate to screen position
            Vector2 screenPosition = _hexGridRenderer.HexToScreenCoords((int)coordinate.Y, (int)coordinate.X);
            
            // Create and add the animation
            Animation animation = new Animation(
                animationTexture,
                screenPosition,
                scale * _hexGridRenderer.ScaleFactor, // Scale relative to hex grid
                duration,
                MathHelper.ToRadians(rotation), // Convert degrees to radians
                color
            );
            
            _animationManager.AddAnimation(animation);
            
            Console.WriteLine($"Added animation at {coordinate.X},{coordinate.Y} with duration {duration}s");
            _debugInfo += $"Added animation at {coordinate.X},{coordinate.Y} with duration {duration}s\n";
        }
        
        /// <summary>
        /// Draws an animation at the specified screen coordinates
        /// </summary>
        /// <param name="screenPosition">The screen position</param>
        /// <param name="animationTexture">The texture to use for the animation</param>
        /// <param name="scale">The scale of the animation</param>
        /// <param name="duration">The duration of the animation in seconds</param>
        /// <param name="rotation">Optional rotation in degrees</param>
        /// <param name="color">Optional color tint</param>
        public void DrawAnimationAtScreenPosition(Vector2 screenPosition, Texture2D animationTexture, float scale, float duration, float rotation = 0f, Color? color = null)
        {
            // Create and add the animation
            Animation animation = new Animation(
                animationTexture,
                screenPosition,
                scale,
                duration,
                MathHelper.ToRadians(rotation), // Convert degrees to radians
                color
            );
            
            _animationManager.AddAnimation(animation);
            
            Console.WriteLine($"Added animation at screen position {screenPosition.X},{screenPosition.Y} with duration {duration}s");
            _debugInfo += $"Added animation at screen position {screenPosition.X},{screenPosition.Y} with duration {duration}s\n";
        }
    }
} 