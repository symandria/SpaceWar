using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;
using System.IO;

namespace SpaceWar.UI
{
    /// <summary>
    /// A test class to demonstrate how to use the BattleGrid.
    /// </summary>
    public class BattleGridTest : Game
    {
        private GraphicsDeviceManager _graphics;
        private SpriteBatch _spriteBatch;
        private SpriteFont _font;
        
        private TextureManager _textureManager;
        private IBattleGrid _battleGrid;
        
        private KeyboardState _prevKeyboardState;
        private MouseState _prevMouseState;
        
        // Test objects
        private int _federationShipId;
        private int _klingonShipId;
        
        // Selection
        private int? _selectedObjectId = null;
        private (int Row, int Column)? _selectedHex = null;
        
        public BattleGridTest()
        {
            _graphics = new GraphicsDeviceManager(this);
            Content.RootDirectory = "Content";
            IsMouseVisible = true;
            
            _graphics.PreferredBackBufferWidth = 1280;
            _graphics.PreferredBackBufferHeight = 720;
        }
        
        protected override void Initialize()
        {
            base.Initialize();
        }
        
        protected override void LoadContent()
        {
            _spriteBatch = new SpriteBatch(GraphicsDevice);
            _font = Content.Load<SpriteFont>("Font");
            
            // Create texture manager
            _textureManager = new TextureManager(Content, GraphicsDevice);
            
            // Load ship textures
            LoadShipTextures();
            
            // Create battle grid
            _battleGrid = new BattleGrid(GraphicsDevice, _textureManager, _font);
            
            // Create white background
            Texture2D whiteBackground = new Texture2D(GraphicsDevice, 1, 1);
            whiteBackground.SetData(new[] { Color.White });
            _battleGrid.SetBackground(whiteBackground);
            
            // Set up grid with 14 rows and 11 columns
            _battleGrid.DrawGameGrid(14, 11);
            
            // Register callbacks
            _battleGrid.RegisterObjectMovementCallback(OnObjectMoved);
            _battleGrid.RegisterObjectDestroyedCallback(OnObjectDestroyed);
            
            // Create test objects
            _federationShipId = _battleGrid.CreateObject("federation", 2, 3, 0, 5, 0.5f);
            _klingonShipId = _battleGrid.CreateObject("klingon", 5, 7, 0, 5, 0.5f);
            
            // Enable debug mode
            _battleGrid.SetDebugMode(true);
        }
        
        private void LoadShipTextures()
        {
            try
            {
                // Load federation ship texture
                using (FileStream fileStream = new FileStream("federation.png", FileMode.Open))
                {
                    Texture2D federationTexture = Texture2D.FromStream(GraphicsDevice, fileStream);
                    _textureManager.AddTexture("federation", federationTexture);
                }
                
                // Load klingon ship texture
                using (FileStream fileStream = new FileStream("klingon.png", FileMode.Open))
                {
                    Texture2D klingonTexture = Texture2D.FromStream(GraphicsDevice, fileStream);
                    _textureManager.AddTexture("klingon", klingonTexture);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading ship textures: {ex.Message}");
                
                // Generate fallback textures if loading fails
                _textureManager.GenerateCircleTexture("federation", 50, Color.Blue, 2, Color.White);
                _textureManager.GenerateCircleTexture("klingon", 50, Color.Red, 2, Color.White);
            }
            
            // Generate effect textures
            _textureManager.GenerateCircleTexture("explosion", 40, Color.OrangeRed, 0, Color.Transparent);
            _textureManager.GenerateCircleTexture("shield", 60, new Color(100, 100, 255, 128), 2, Color.Blue);
        }
        
        private void OnObjectMoved(int objectId, int finalRow, int finalColumn)
        {
            Console.WriteLine($"Object {objectId} moved to ({finalRow}, {finalColumn})");
            
            // Play animation when ship reaches destination
            if (objectId == _federationShipId)
            {
                _battleGrid.PlayAnimation("shield", finalRow, finalColumn, 1.0f, 1.0f, 15);
            }
        }
        
        private void OnObjectDestroyed(int objectId)
        {
            Console.WriteLine($"Object {objectId} was destroyed");
            
            // Get the position before it was destroyed
            try
            {
                var position = _battleGrid.GetObjectPosition(objectId);
                _battleGrid.PlayAnimation("explosion", position.Row, position.Column, 1.5f, 1.0f, 15);
            }
            catch
            {
                // Object already removed
            }
            
            // Clear selection if the selected object was destroyed
            if (_selectedObjectId == objectId)
            {
                _selectedObjectId = null;
                _selectedHex = null;
            }
        }
        
        protected override void Update(GameTime gameTime)
        {
            KeyboardState keyboardState = Keyboard.GetState();
            MouseState mouseState = Mouse.GetState();
            
            // Exit on Escape
            if (keyboardState.IsKeyDown(Keys.Escape))
            {
                Exit();
            }
            
            // Handle mouse clicks for selection
            if (mouseState.LeftButton == ButtonState.Pressed && _prevMouseState.LeftButton == ButtonState.Released)
            {
                HandleMouseClick(mouseState.Position);
            }
            
            // Move selected object with M key
            if (_selectedObjectId.HasValue && _selectedHex.HasValue && IsKeyPressed(keyboardState, Keys.M, _prevKeyboardState))
            {
                _battleGrid.MoveObject(_selectedObjectId.Value, _selectedHex.Value.Row, _selectedHex.Value.Column, 2.0f);
            }
            
            // Move federation ship with arrow keys
            if (IsKeyPressed(keyboardState, Keys.Up, _prevKeyboardState))
            {
                var position = _battleGrid.GetObjectPosition(_federationShipId);
                _battleGrid.MoveObject(_federationShipId, Math.Max(0, position.Row - 1), position.Column, 2.0f);
            }
            else if (IsKeyPressed(keyboardState, Keys.Down, _prevKeyboardState))
            {
                var position = _battleGrid.GetObjectPosition(_federationShipId);
                _battleGrid.MoveObject(_federationShipId, Math.Min(13, position.Row + 1), position.Column, 2.0f);
            }
            else if (IsKeyPressed(keyboardState, Keys.Left, _prevKeyboardState))
            {
                var position = _battleGrid.GetObjectPosition(_federationShipId);
                _battleGrid.MoveObject(_federationShipId, position.Row, Math.Max(0, position.Column - 1), 2.0f);
                _battleGrid.RotateObject(_federationShipId, 270, 180);
            }
            else if (IsKeyPressed(keyboardState, Keys.Right, _prevKeyboardState))
            {
                var position = _battleGrid.GetObjectPosition(_federationShipId);
                _battleGrid.MoveObject(_federationShipId, position.Row, Math.Min(10, position.Column + 1), 2.0f);
                _battleGrid.RotateObject(_federationShipId, 90, 180);
            }
            
            // Highlight range with number keys
            if (IsKeyPressed(keyboardState, Keys.D1, _prevKeyboardState))
            {
                var position = _battleGrid.GetObjectPosition(_federationShipId);
                _battleGrid.HighlightRange(position.Row, position.Column, 0, 1, Color.Yellow, 1.0f);
            }
            else if (IsKeyPressed(keyboardState, Keys.D2, _prevKeyboardState))
            {
                var position = _battleGrid.GetObjectPosition(_federationShipId);
                _battleGrid.HighlightRange(position.Row, position.Column, 0, 2, Color.Green, 1.0f);
            }
            else if (IsKeyPressed(keyboardState, Keys.D3, _prevKeyboardState))
            {
                var position = _battleGrid.GetObjectPosition(_federationShipId);
                _battleGrid.HighlightRange(position.Row, position.Column, 0, 3, Color.Blue, 1.0f);
            }
            
            // Draw path with P key
            if (IsKeyPressed(keyboardState, Keys.P, _prevKeyboardState))
            {
                var shipPos = _battleGrid.GetObjectPosition(_federationShipId);
                var klingonPos = _battleGrid.GetObjectPosition(_klingonShipId);
                
                _battleGrid.DrawLine(shipPos.Row, shipPos.Column, klingonPos.Row, klingonPos.Column, Color.Red, 2.0f);
            }
            
            // Toggle debug mode with Tab key
            if (IsKeyPressed(keyboardState, Keys.Tab, _prevKeyboardState))
            {
                _battleGrid.SetDebugMode(!keyboardState.IsKeyDown(Keys.LeftShift));
            }
            
            // Update battle grid
            _battleGrid.Update(gameTime);
            
            _prevKeyboardState = keyboardState;
            _prevMouseState = mouseState;
            
            base.Update(gameTime);
        }
        
        private void HandleMouseClick(Point mousePosition)
        {
            // Convert mouse position to hex coordinates
            var hexCoords = _battleGrid.GetHexFromScreenPosition(new Vector2(mousePosition.X, mousePosition.Y));
            
            if (hexCoords.HasValue)
            {
                // Store the selected hex
                _selectedHex = hexCoords.Value;
                
                // Get objects at this position
                int[] objectsAtPosition = _battleGrid.GetObjectsAtPosition(hexCoords.Value.Row, hexCoords.Value.Column);
                
                if (objectsAtPosition.Length > 0)
                {
                    // Select the first object at this position
                    _selectedObjectId = objectsAtPosition[0];
                    
                    // Determine ship type for display
                    string shipType = _selectedObjectId == _federationShipId ? "Federation" : "Klingon";
                    Console.WriteLine($"Selected {shipType} ship (ID: {_selectedObjectId}) at ({hexCoords.Value.Row}, {hexCoords.Value.Column})");
                    
                    // Highlight the selected object's hex
                    _battleGrid.HighlightHex(hexCoords.Value.Row, hexCoords.Value.Column, Color.Green, 0.5f);
                }
                else
                {
                    // No objects at this position
                    _selectedObjectId = null;
                    Console.WriteLine($"Selected empty hex at ({hexCoords.Value.Row}, {hexCoords.Value.Column})");
                    
                    // Highlight the selected hex
                    _battleGrid.HighlightHex(hexCoords.Value.Row, hexCoords.Value.Column, Color.Yellow, 0.5f);
                }
            }
            else
            {
                // Click was outside the grid, clear selection
                _selectedObjectId = null;
                _selectedHex = null;
            }
        }
        
        protected override void Draw(GameTime gameTime)
        {
            GraphicsDevice.Clear(Color.White);
            
            _spriteBatch.Begin();
            
            // Draw battle grid
            _battleGrid.Draw(_spriteBatch);
            
            // Draw selection indicator
            if (_selectedHex.HasValue)
            {
                // Get the screen position of the selected hex
                Vector2 hexPosition = _battleGrid.GetHexPosition(_selectedHex.Value.Row, _selectedHex.Value.Column);
                
                // Draw a selection ring around the selected hex
                Texture2D selectionTexture = _textureManager.GetTexture("hex_highlight");
                Color selectionColor = _selectedObjectId.HasValue ? Color.Green : Color.Yellow;
                
                _spriteBatch.Draw(
                    selectionTexture,
                    hexPosition,
                    null,
                    selectionColor * 0.5f, // Semi-transparent
                    0f,
                    new Vector2(selectionTexture.Width / 2, selectionTexture.Height / 2),
                    0.5f, // Scale to make it slightly larger than the hex
                    SpriteEffects.None,
                    0f
                );
            }
            
            // Draw selection info
            string selectionInfo = "";
            if (_selectedObjectId.HasValue)
            {
                string shipType = _selectedObjectId == _federationShipId ? "Federation" : "Klingon";
                selectionInfo = $"Selected: {shipType} ship (ID: {_selectedObjectId})";
                
                if (_selectedHex.HasValue)
                {
                    selectionInfo += $"\nAt position: ({_selectedHex.Value.Row}, {_selectedHex.Value.Column})";
                }
            }
            else if (_selectedHex.HasValue)
            {
                selectionInfo = $"Selected empty hex: ({_selectedHex.Value.Row}, {_selectedHex.Value.Column})";
            }
            
            if (!string.IsNullOrEmpty(selectionInfo))
            {
                _spriteBatch.DrawString(_font, selectionInfo, new Vector2(10, 150), Color.Black);
            }
            
            // Draw instructions
            string instructions = 
                "Left Click: Select hex/ship\n" +
                "M: Move selected ship to selected hex\n" +
                "Arrow Keys: Move Federation ship\n" +
                "1-3: Highlight Range\n" +
                "P: Draw Path\n" +
                "Tab: Toggle Debug Mode\n" +
                "Escape: Exit";
            
            _spriteBatch.DrawString(_font, instructions, new Vector2(10, 200), Color.Black);
            
            _spriteBatch.End();
            
            base.Draw(gameTime);
        }
        
        private bool IsKeyPressed(KeyboardState currentState, Keys key, KeyboardState previousState)
        {
            return currentState.IsKeyDown(key) && !previousState.IsKeyDown(key);
        }
    }
} 