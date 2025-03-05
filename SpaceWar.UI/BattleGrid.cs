using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using System;
using System.Collections.Generic;
using System.Linq;

namespace SpaceWar.UI
{
    /// <summary>
    /// Implementation of the BattleGrid interface that manages the hex grid, game objects, and visual effects.
    /// </summary>
    public class BattleGrid : IBattleGrid
    {
        // Constants
        private const float DEFAULT_HEX_SIZE = 40f;
        private const float GRID_OFFSET_X = 100f;
        private const float GRID_OFFSET_Y = 100f;
        private const float GRID_MARGIN = 50f; // Margin around the grid

        // Core components
        private readonly GraphicsDevice _graphicsDevice;
        private readonly TextureManager _textureManager;
        private readonly SpriteFont _debugFont;

        // Grid properties
        private int _rows;
        private int _columns;
        private float _hexSize = DEFAULT_HEX_SIZE;
        private bool _gridVisible = true;
        private Texture2D _backgroundTexture;

        // Collections for game elements
        private readonly Dictionary<int, GridObject> _objects = new Dictionary<int, GridObject>();
        private readonly List<GridAnimation> _animations = new List<GridAnimation>();
        private readonly List<GridEffect> _effects = new List<GridEffect>();
        private readonly List<GridPath> _paths = new List<GridPath>();
        private readonly List<HexHighlight> _highlights = new List<HexHighlight>();

        // ID counters
        private int _nextObjectId = 1;
        private int _nextAnimationId = 1;
        private int _nextEffectId = 1;
        private int _nextPathId = 1;
        private int _nextHighlightId = 1;

        // Callbacks
        private Action<int, int, int> _objectMovementCallback;
        private Action<int> _objectDestroyedCallback;

        // Debug mode
        private bool _debugMode = false;

        /// <summary>
        /// Creates a new BattleGrid.
        /// </summary>
        /// <param name="graphicsDevice">The graphics device.</param>
        /// <param name="textureManager">The texture manager.</param>
        /// <param name="debugFont">The font to use for debug information.</param>
        public BattleGrid(GraphicsDevice graphicsDevice, TextureManager textureManager, SpriteFont debugFont)
        {
            _graphicsDevice = graphicsDevice;
            _textureManager = textureManager;
            _debugFont = debugFont;
        }

        /// <summary>
        /// Calculates the optimal hex size based on the window dimensions and grid size.
        /// </summary>
        /// <param name="rows">Number of rows in the grid.</param>
        /// <param name="columns">Number of columns in the grid.</param>
        /// <returns>The optimal hex size.</returns>
        private float CalculateHexSize(int rows, int columns)
        {
            // Get viewport dimensions
            int viewportWidth = _graphicsDevice.Viewport.Width;
            int viewportHeight = _graphicsDevice.Viewport.Height;
            
            // Calculate available space
            float availableWidth = viewportWidth - (2 * GRID_OFFSET_X) - (2 * GRID_MARGIN);
            float availableHeight = viewportHeight - (2 * GRID_OFFSET_Y) - (2 * GRID_MARGIN);
            
            // Calculate hex size based on width
            // For odd-q layout, width is 2 * hexSize * HEX_WIDTH_MULTIPLIER * columns
            float hexWidthMultiplier = 0.866f; // sqrt(3)/2
            float hexSizeFromWidth = availableWidth / (2 * hexWidthMultiplier * columns);
            
            // Calculate hex size based on height
            // Height is 1.5 * hexSize * rows
            float hexSizeFromHeight = availableHeight / (1.5f * rows);
            
            // Use the smaller of the two to ensure the grid fits
            return Math.Min(hexSizeFromWidth, hexSizeFromHeight);
        }

        /// <summary>
        /// Creates and displays a hex grid with specified dimensions.
        /// </summary>
        /// <param name="rows">Number of rows in the grid.</param>
        /// <param name="columns">Number of columns in the grid.</param>
        public void DrawGameGrid(int rows, int columns)
        {
            _rows = rows;
            _columns = columns;
            _gridVisible = true;
            
            // Calculate optimal hex size
            _hexSize = CalculateHexSize(rows, columns);
        }

        /// <summary>
        /// Sets a background image that appears behind all game elements.
        /// </summary>
        /// <param name="background">The texture to use as the background.</param>
        public void SetBackground(Texture2D background)
        {
            _backgroundTexture = background;
        }

        /// <summary>
        /// Hides the hex grid without destroying it.
        /// </summary>
        public void HideGameGrid()
        {
            _gridVisible = false;
        }

        /// <summary>
        /// Makes a hidden grid visible again.
        /// </summary>
        public void ShowGameGrid()
        {
            _gridVisible = true;
        }

        /// <summary>
        /// Returns the screen coordinates for a given hex cell.
        /// </summary>
        /// <param name="row">The row of the hex cell.</param>
        /// <param name="column">The column of the hex cell.</param>
        /// <returns>Vector2 containing the screen coordinates.</returns>
        public Vector2 GetHexPosition(int row, int column)
        {
            return HexGridUtils.HexToScreen(row, column, _hexSize, GRID_OFFSET_X, GRID_OFFSET_Y);
        }

        /// <summary>
        /// Returns the hex coordinates for a given screen position.
        /// </summary>
        /// <param name="screenPosition">The screen position to convert.</param>
        /// <returns>Tuple containing (row, column) or null if not on a valid hex.</returns>
        public (int Row, int Column)? GetHexFromScreenPosition(Vector2 screenPosition)
        {
            return HexGridUtils.ScreenToHex(screenPosition, _hexSize, GRID_OFFSET_X, GRID_OFFSET_Y, _rows, _columns);
        }

        #region Object Management

        /// <summary>
        /// Creates a game object at the specified hex position and returns its unique ID.
        /// </summary>
        /// <param name="objectType">The type of object to create (e.g., "ship", "asteroid").</param>
        /// <param name="row">The row position.</param>
        /// <param name="column">The column position.</param>
        /// <param name="rotation">The initial rotation in degrees.</param>
        /// <param name="drawLayer">The layer to draw the object on (higher numbers are drawn on top).</param>
        /// <param name="scale">The scale of the object.</param>
        /// <returns>Integer ID of the created object.</returns>
        public int CreateObject(string objectType, int row, int column, float rotation, int drawLayer = 0, float scale = 1.0f)
        {
            // Validate position
            if (row < 0 || row >= _rows || column < 0 || column >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Position ({row}, {column}) is outside the grid bounds.");
            }
            
            // Create object
            int id = _nextObjectId++;
            string textureKey = objectType.ToLower(); // Assuming texture key matches object type
            
            GridObject obj = new GridObject(id, objectType, row, column, rotation, drawLayer, scale, textureKey);
            obj.InterpolatedPosition = GetHexPosition(row, column);
            
            _objects[id] = obj;
            
            return id;
        }

        /// <summary>
        /// Removes an object from the grid.
        /// </summary>
        /// <param name="objectId">The ID of the object to delete.</param>
        /// <returns>Boolean indicating success.</returns>
        public bool DeleteObject(int objectId)
        {
            if (_objects.TryGetValue(objectId, out GridObject obj))
            {
                _objects.Remove(objectId);
                _objectDestroyedCallback?.Invoke(objectId);
                return true;
            }
            
            return false;
        }

        /// <summary>
        /// Returns the current hex position of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <returns>Tuple containing (row, column).</returns>
        public (int Row, int Column) GetObjectPosition(int objectId)
        {
            if (_objects.TryGetValue(objectId, out GridObject obj))
            {
                return (obj.CurrentRow, obj.CurrentColumn);
            }
            
            throw new KeyNotFoundException($"Object with ID {objectId} not found.");
        }

        /// <summary>
        /// Shows or hides an object without deleting it.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="isVisible">Whether the object should be visible.</param>
        public void SetObjectVisibility(int objectId, bool isVisible)
        {
            if (_objects.TryGetValue(objectId, out GridObject obj))
            {
                obj.IsVisible = isVisible;
            }
            else
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
        }

        /// <summary>
        /// Changes the appearance of an existing object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="textureKey">The key for the new texture.</param>
        public void SetObjectTexture(int objectId, string textureKey)
        {
            if (_objects.TryGetValue(objectId, out GridObject obj))
            {
                obj.TextureKey = textureKey;
            }
            else
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
        }

        /// <summary>
        /// Immediately rotates an object to a specific angle.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="rotation">The rotation in degrees.</param>
        public void SetObjectRotation(int objectId, float rotation)
        {
            if (_objects.TryGetValue(objectId, out GridObject obj))
            {
                obj.Rotation = rotation;
                obj.TargetRotation = null; // Cancel any ongoing rotation
            }
            else
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
        }

        /// <summary>
        /// Changes the size of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="scale">The new scale factor.</param>
        public void SetObjectScale(int objectId, float scale)
        {
            if (_objects.TryGetValue(objectId, out GridObject obj))
            {
                obj.Scale = scale;
            }
            else
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
        }

        /// <summary>
        /// Changes the drawing layer of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="drawLayer">The new draw layer (higher numbers are drawn on top).</param>
        public void SetObjectDrawLayer(int objectId, int drawLayer)
        {
            if (_objects.TryGetValue(objectId, out GridObject obj))
            {
                obj.DrawLayer = drawLayer;
            }
            else
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
        }

        #endregion

        #region Movement and Animation

        /// <summary>
        /// Moves an object smoothly to a target hex at the specified speed.
        /// </summary>
        /// <param name="objectId">The ID of the object to move.</param>
        /// <param name="targetRow">The target row.</param>
        /// <param name="targetColumn">The target column.</param>
        /// <param name="speed">The speed in hex cells per second.</param>
        /// <returns>Boolean indicating if the movement was started successfully.</returns>
        public bool MoveObject(int objectId, int targetRow, int targetColumn, float speed)
        {
            // Validate target position
            if (targetRow < 0 || targetRow >= _rows || targetColumn < 0 || targetColumn >= _columns)
            {
                return false;
            }
            
            if (!_objects.TryGetValue(objectId, out GridObject obj))
            {
                return false;
            }
            
            // Check if already at target
            if (obj.CurrentRow == targetRow && obj.CurrentColumn == targetColumn)
            {
                return true;
            }
            
            // Set target and speed
            obj.TargetRow = targetRow;
            obj.TargetColumn = targetColumn;
            obj.MovementSpeed = speed;
            
            return true;
        }

        /// <summary>
        /// Smoothly rotates an object to a target angle.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="targetRotation">The target rotation in degrees.</param>
        /// <param name="rotationSpeed">The rotation speed in degrees per second.</param>
        public void RotateObject(int objectId, float targetRotation, float rotationSpeed)
        {
            if (!_objects.TryGetValue(objectId, out GridObject obj))
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
            
            // Normalize target rotation to 0-360 range
            targetRotation = targetRotation % 360;
            if (targetRotation < 0) targetRotation += 360;
            
            // Set target and speed
            obj.TargetRotation = targetRotation;
            obj.RotationSpeed = rotationSpeed;
        }

        /// <summary>
        /// Immediately stops any movement or rotation of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        public void StopObject(int objectId)
        {
            if (!_objects.TryGetValue(objectId, out GridObject obj))
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
            
            obj.TargetRow = null;
            obj.TargetColumn = null;
            obj.TargetRotation = null;
        }

        /// <summary>
        /// Returns whether an object is currently in motion.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <returns>Boolean indicating if the object is moving.</returns>
        public bool IsObjectMoving(int objectId)
        {
            if (!_objects.TryGetValue(objectId, out GridObject obj))
            {
                throw new KeyNotFoundException($"Object with ID {objectId} not found.");
            }
            
            return obj.IsMoving || obj.IsRotating;
        }

        /// <summary>
        /// Plays a predefined animation at a hex location.
        /// </summary>
        /// <param name="animationType">The type of animation (e.g., "explosion", "shield").</param>
        /// <param name="row">The row position.</param>
        /// <param name="column">The column position.</param>
        /// <param name="duration">The duration of the animation in seconds.</param>
        /// <param name="scale">The scale of the animation.</param>
        /// <param name="drawLayer">The layer to draw the animation on.</param>
        public void PlayAnimation(string animationType, int row, int column, float duration, float scale = 1.0f, int drawLayer = 10)
        {
            // Validate position
            if (row < 0 || row >= _rows || column < 0 || column >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Position ({row}, {column}) is outside the grid bounds.");
            }
            
            // Get animation texture
            Texture2D texture = _textureManager.GetTexture(animationType);
            
            // Create animation
            int id = _nextAnimationId++;
            GridAnimation animation = new GridAnimation(id, animationType, texture, row, column, duration, scale, 0f, drawLayer);
            
            _animations.Add(animation);
        }

        /// <summary>
        /// Plays a custom animation at a hex location.
        /// </summary>
        /// <param name="texture">The texture to use for the animation.</param>
        /// <param name="row">The row position.</param>
        /// <param name="column">The column position.</param>
        /// <param name="duration">The duration of the animation in seconds.</param>
        /// <param name="scale">The scale of the animation.</param>
        /// <param name="rotation">The rotation in degrees.</param>
        /// <param name="drawLayer">The layer to draw the animation on.</param>
        public void PlayCustomAnimation(Texture2D texture, int row, int column, float duration, float scale = 1.0f, float rotation = 0f, int drawLayer = 10)
        {
            // Validate position
            if (row < 0 || row >= _rows || column < 0 || column >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Position ({row}, {column}) is outside the grid bounds.");
            }
            
            // Create animation
            int id = _nextAnimationId++;
            GridAnimation animation = new GridAnimation(id, "custom", texture, row, column, duration, scale, rotation, drawLayer);
            
            _animations.Add(animation);
        }

        #endregion

        #region Effects and Visual Enhancements

        /// <summary>
        /// Draws a path between hex points (temporary if duration > 0).
        /// </summary>
        /// <param name="rowPoints">Array of row coordinates.</param>
        /// <param name="columnPoints">Array of column coordinates.</param>
        /// <param name="color">The color of the path.</param>
        /// <param name="duration">How long the path should remain visible (0 = permanent).</param>
        /// <param name="drawLayer">The layer to draw the path on.</param>
        public void DrawPath(int[] rowPoints, int[] columnPoints, Color color, float duration = 0, int drawLayer = 5)
        {
            // Validate input
            if (rowPoints == null || columnPoints == null)
            {
                throw new ArgumentNullException("Row and column points cannot be null.");
            }
            
            if (rowPoints.Length != columnPoints.Length)
            {
                throw new ArgumentException("Row and column points arrays must have the same length.");
            }
            
            if (rowPoints.Length < 2)
            {
                throw new ArgumentException("Path must have at least two points.");
            }
            
            // Validate all points are within grid bounds
            for (int i = 0; i < rowPoints.Length; i++)
            {
                if (rowPoints[i] < 0 || rowPoints[i] >= _rows || columnPoints[i] < 0 || columnPoints[i] >= _columns)
                {
                    throw new ArgumentOutOfRangeException($"Point ({rowPoints[i]}, {columnPoints[i]}) is outside the grid bounds.");
                }
            }
            
            // Create path
            int id = _nextPathId++;
            GridPath path = new GridPath(id, rowPoints, columnPoints, color, duration, drawLayer);
            
            _paths.Add(path);
        }

        /// <summary>
        /// Highlights a specific hex (temporary if duration > 0).
        /// </summary>
        /// <param name="row">The row of the hex.</param>
        /// <param name="column">The column of the hex.</param>
        /// <param name="color">The highlight color.</param>
        /// <param name="duration">How long the highlight should remain visible (0 = permanent).</param>
        /// <param name="drawLayer">The layer to draw the highlight on.</param>
        public void HighlightHex(int row, int column, Color color, float duration = 0, int drawLayer = 1)
        {
            // Validate position
            if (row < 0 || row >= _rows || column < 0 || column >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Position ({row}, {column}) is outside the grid bounds.");
            }
            
            // Create highlight
            int id = _nextHighlightId++;
            HexHighlight highlight = new HexHighlight(id, row, column, color, duration, drawLayer);
            
            _highlights.Add(highlight);
        }

        /// <summary>
        /// Highlights all hexes within a range band (from minRange to maxRange).
        /// </summary>
        /// <param name="centerRow">The center row.</param>
        /// <param name="centerColumn">The center column.</param>
        /// <param name="minRange">The minimum range (inclusive).</param>
        /// <param name="maxRange">The maximum range (inclusive).</param>
        /// <param name="color">The highlight color.</param>
        /// <param name="duration">How long the highlight should remain visible (0 = permanent).</param>
        /// <param name="drawLayer">The layer to draw the highlight on.</param>
        public void HighlightRange(int centerRow, int centerColumn, int minRange, int maxRange, Color color, float duration = 0, int drawLayer = 1)
        {
            // Validate center position
            if (centerRow < 0 || centerRow >= _rows || centerColumn < 0 || centerColumn >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Center position ({centerRow}, {centerColumn}) is outside the grid bounds.");
            }
            
            // Validate ranges
            if (minRange < 0 || maxRange < minRange)
            {
                throw new ArgumentOutOfRangeException("Invalid range values.");
            }
            
            // Get hexes in range band
            List<(int Row, int Column)> hexes = HexGridUtils.GetHexesInRangeBand(centerRow, centerColumn, minRange, maxRange, _rows, _columns);
            
            // Highlight each hex
            foreach (var hex in hexes)
            {
                HighlightHex(hex.Row, hex.Column, color, duration, drawLayer);
            }
        }

        /// <summary>
        /// Draws a line between two hex cells.
        /// </summary>
        /// <param name="startRow">The starting row.</param>
        /// <param name="startColumn">The starting column.</param>
        /// <param name="endRow">The ending row.</param>
        /// <param name="endColumn">The ending column.</param>
        /// <param name="color">The line color.</param>
        /// <param name="duration">How long the line should remain visible (0 = permanent).</param>
        /// <param name="drawLayer">The layer to draw the line on.</param>
        public void DrawLine(int startRow, int startColumn, int endRow, int endColumn, Color color, float duration = 0, int drawLayer = 5)
        {
            // Validate positions
            if (startRow < 0 || startRow >= _rows || startColumn < 0 || startColumn >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Start position ({startRow}, {startColumn}) is outside the grid bounds.");
            }
            
            if (endRow < 0 || endRow >= _rows || endColumn < 0 || endColumn >= _columns)
            {
                throw new ArgumentOutOfRangeException($"End position ({endRow}, {endColumn}) is outside the grid bounds.");
            }
            
            // Create path with just two points
            int[] rowPoints = new int[] { startRow, endRow };
            int[] columnPoints = new int[] { startColumn, endColumn };
            
            DrawPath(rowPoints, columnPoints, color, duration, drawLayer);
        }

        /// <summary>
        /// Adds a particle effect (explosion, energy, etc.) at a hex location.
        /// </summary>
        /// <param name="effectType">The type of effect.</param>
        /// <param name="row">The row position.</param>
        /// <param name="column">The column position.</param>
        /// <param name="duration">The duration of the effect in seconds.</param>
        /// <param name="drawLayer">The layer to draw the effect on.</param>
        public void AddParticleEffect(string effectType, int row, int column, float duration, int drawLayer = 10)
        {
            // Validate position
            if (row < 0 || row >= _rows || column < 0 || column >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Position ({row}, {column}) is outside the grid bounds.");
            }
            
            // Create effect
            int id = _nextEffectId++;
            Color effectColor = Color.White; // Default color
            
            // Set color based on effect type
            switch (effectType.ToLower())
            {
                case "explosion":
                    effectColor = Color.OrangeRed;
                    break;
                case "shield":
                    effectColor = Color.CornflowerBlue;
                    break;
                case "energy":
                    effectColor = Color.Yellow;
                    break;
                case "heal":
                    effectColor = Color.LightGreen;
                    break;
                default:
                    effectColor = Color.White;
                    break;
            }
            
            GridEffect effect = new GridEffect(id, effectType, row, column, duration, drawLayer, effectColor);
            
            _effects.Add(effect);
        }

        #endregion

        #region Game State and UI Integration

        /// <summary>
        /// Toggles display of debug information like object IDs, paths, etc.
        /// </summary>
        /// <param name="enabled">Whether debug mode should be enabled.</param>
        public void SetDebugMode(bool enabled)
        {
            _debugMode = enabled;
        }

        /// <summary>
        /// Removes all objects and effects from the grid.
        /// </summary>
        public void ClearAll()
        {
            _objects.Clear();
            _animations.Clear();
            _effects.Clear();
            _paths.Clear();
            _highlights.Clear();
        }

        /// <summary>
        /// Returns IDs of all objects within a certain range.
        /// </summary>
        /// <param name="centerRow">The center row.</param>
        /// <param name="centerColumn">The center column.</param>
        /// <param name="range">The range to check.</param>
        /// <returns>Array of object IDs.</returns>
        public int[] GetObjectsInRange(int centerRow, int centerColumn, int range)
        {
            // Validate center position
            if (centerRow < 0 || centerRow >= _rows || centerColumn < 0 || centerColumn >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Center position ({centerRow}, {centerColumn}) is outside the grid bounds.");
            }
            
            // Validate range
            if (range < 0)
            {
                throw new ArgumentOutOfRangeException("Range cannot be negative.");
            }
            
            // Get hexes in range
            List<(int Row, int Column)> hexes = HexGridUtils.GetHexesInRange(centerRow, centerColumn, range, _rows, _columns);
            
            // Find objects in those hexes
            List<int> objectIds = new List<int>();
            
            foreach (var obj in _objects.Values)
            {
                if (hexes.Any(h => h.Row == obj.CurrentRow && h.Column == obj.CurrentColumn))
                {
                    objectIds.Add(obj.Id);
                }
            }
            
            return objectIds.ToArray();
        }

        /// <summary>
        /// Registers a function to be called when an object completes movement.
        /// </summary>
        /// <param name="callback">The function to call with parameters (objectId, finalRow, finalColumn).</param>
        public void RegisterObjectMovementCallback(Action<int, int, int> callback)
        {
            _objectMovementCallback = callback;
        }

        /// <summary>
        /// Registers a function to be called when an object is destroyed.
        /// </summary>
        /// <param name="callback">The function to call with parameter (objectId).</param>
        public void RegisterObjectDestroyedCallback(Action<int> callback)
        {
            _objectDestroyedCallback = callback;
        }

        /// <summary>
        /// Returns IDs of all objects at a specific hex position.
        /// </summary>
        /// <param name="row">The row of the hex.</param>
        /// <param name="column">The column of the hex.</param>
        /// <returns>Array of object IDs at the specified position.</returns>
        public int[] GetObjectsAtPosition(int row, int column)
        {
            // Validate position
            if (row < 0 || row >= _rows || column < 0 || column >= _columns)
            {
                throw new ArgumentOutOfRangeException($"Position ({row}, {column}) is outside the grid bounds.");
            }
            
            // Find objects at the position
            List<int> objectIds = new List<int>();
            
            foreach (var obj in _objects.Values)
            {
                if (obj.CurrentRow == row && obj.CurrentColumn == column)
                {
                    objectIds.Add(obj.Id);
                }
            }
            
            return objectIds.ToArray();
        }

        #endregion

        /// <summary>
        /// Updates the battle grid state.
        /// </summary>
        /// <param name="gameTime">The game time.</param>
        public void Update(GameTime gameTime)
        {
            float deltaTime = (float)gameTime.ElapsedGameTime.TotalSeconds;
            
            // Update animations
            UpdateAnimations(deltaTime);
            
            // Update objects
            UpdateObjects(deltaTime);
            
            // Update effects
            UpdateEffects(deltaTime);
            
            // Update paths
            UpdatePaths(deltaTime);
            
            // Update highlights
            UpdateHighlights(deltaTime);
        }

        /// <summary>
        /// Draws the battle grid and all its elements.
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to use for drawing.</param>
        public void Draw(SpriteBatch spriteBatch)
        {
            // Draw background
            if (_backgroundTexture != null)
            {
                spriteBatch.Draw(_backgroundTexture, new Rectangle(0, 0, _graphicsDevice.Viewport.Width, _graphicsDevice.Viewport.Height), Color.White);
            }
            
            // Draw grid
            if (_gridVisible)
            {
                DrawGrid(spriteBatch);
            }
            
            // Get all drawable elements sorted by draw layer
            var drawables = new List<(int DrawLayer, Action<SpriteBatch> DrawAction)>();
            
            // Add highlights
            foreach (var highlight in _highlights)
            {
                drawables.Add((highlight.DrawLayer, (sb) => DrawHighlight(sb, highlight)));
            }
            
            // Add paths
            foreach (var path in _paths)
            {
                drawables.Add((path.DrawLayer, (sb) => DrawPath(sb, path)));
            }
            
            // Add objects
            foreach (var obj in _objects.Values.Where(o => o.IsVisible))
            {
                drawables.Add((obj.DrawLayer, (sb) => DrawObject(sb, obj)));
            }
            
            // Add animations
            foreach (var animation in _animations)
            {
                drawables.Add((animation.DrawLayer, (sb) => DrawAnimation(sb, animation)));
            }
            
            // Add effects
            foreach (var effect in _effects)
            {
                drawables.Add((effect.DrawLayer, (sb) => DrawEffect(sb, effect)));
            }
            
            // Sort by draw layer and draw
            foreach (var drawable in drawables.OrderBy(d => d.DrawLayer))
            {
                drawable.DrawAction(spriteBatch);
            }
            
            // Draw debug information
            if (_debugMode)
            {
                DrawDebugInfo(spriteBatch);
            }
        }

        private void DrawGrid(SpriteBatch spriteBatch)
        {
            Texture2D hexTexture = _textureManager.GetTexture("hex");
            
            for (int row = 0; row < _rows; row++)
            {
                for (int column = 0; column < _columns; column++)
                {
                    Vector2 position = GetHexPosition(row, column);
                    spriteBatch.Draw(
                        hexTexture,
                        position,
                        null,
                        Color.Black, // Use black color for the hex outlines
                        0f,
                        new Vector2(hexTexture.Width / 2, hexTexture.Height / 2),
                        _hexSize / 100f, // Assuming the hex texture is 200x200
                        SpriteEffects.None,
                        0f
                    );
                }
            }
        }

        private void UpdateAnimations(float deltaTime)
        {
            for (int i = _animations.Count - 1; i >= 0; i--)
            {
                _animations[i].ElapsedTime += deltaTime;
                
                if (_animations[i].IsComplete)
                {
                    _animations.RemoveAt(i);
                }
            }
        }

        private void UpdateObjects(float deltaTime)
        {
            foreach (var obj in _objects.Values)
            {
                bool positionChanged = false;
                
                // Update rotation
                if (obj.IsRotating)
                {
                    float targetRotation = obj.TargetRotation.Value;
                    float currentRotation = obj.Rotation;
                    
                    // Calculate shortest rotation direction
                    float diff = (targetRotation - currentRotation) % 360;
                    if (diff > 180) diff -= 360;
                    if (diff < -180) diff += 360;
                    
                    float rotationAmount = obj.RotationSpeed * deltaTime;
                    
                    if (Math.Abs(diff) <= rotationAmount)
                    {
                        // Reached target rotation
                        obj.Rotation = targetRotation;
                        obj.TargetRotation = null;
                    }
                    else
                    {
                        // Continue rotating
                        obj.Rotation += Math.Sign(diff) * rotationAmount;
                    }
                }
                
                // Update movement
                if (obj.IsMoving)
                {
                    Vector2 currentPosition = GetHexPosition(obj.CurrentRow, obj.CurrentColumn);
                    Vector2 targetPosition = GetHexPosition(obj.TargetRow.Value, obj.TargetColumn.Value);
                    
                    // Calculate distance to target
                    float distance = Vector2.Distance(currentPosition, targetPosition);
                    
                    // Calculate movement step
                    float hexDistance = HexGridUtils.HexDistance(obj.CurrentRow, obj.CurrentColumn, obj.TargetRow.Value, obj.TargetColumn.Value);
                    float moveSpeed = obj.MovementSpeed * _hexSize * deltaTime;
                    
                    if (distance <= moveSpeed)
                    {
                        // Reached target position
                        obj.CurrentRow = obj.TargetRow.Value;
                        obj.CurrentColumn = obj.TargetColumn.Value;
                        obj.InterpolatedPosition = targetPosition;
                        obj.TargetRow = null;
                        obj.TargetColumn = null;
                        positionChanged = true;
                        
                        // Call movement callback
                        _objectMovementCallback?.Invoke(obj.Id, obj.CurrentRow, obj.CurrentColumn);
                    }
                    else
                    {
                        // Continue moving
                        Vector2 direction = Vector2.Normalize(targetPosition - currentPosition);
                        obj.InterpolatedPosition = currentPosition + direction * moveSpeed;
                    }
                }
                else
                {
                    // Not moving, set interpolated position to current position
                    obj.InterpolatedPosition = GetHexPosition(obj.CurrentRow, obj.CurrentColumn);
                }
            }
        }

        private void UpdateEffects(float deltaTime)
        {
            for (int i = _effects.Count - 1; i >= 0; i--)
            {
                _effects[i].ElapsedTime += deltaTime;
                
                if (_effects[i].IsComplete)
                {
                    _effects.RemoveAt(i);
                }
            }
        }

        private void UpdatePaths(float deltaTime)
        {
            for (int i = _paths.Count - 1; i >= 0; i--)
            {
                _paths[i].ElapsedTime += deltaTime;
                
                if (_paths[i].IsComplete)
                {
                    _paths.RemoveAt(i);
                }
            }
        }

        private void UpdateHighlights(float deltaTime)
        {
            for (int i = _highlights.Count - 1; i >= 0; i--)
            {
                _highlights[i].ElapsedTime += deltaTime;
                
                if (_highlights[i].IsComplete)
                {
                    _highlights.RemoveAt(i);
                }
            }
        }

        private void DrawObject(SpriteBatch spriteBatch, GridObject obj)
        {
            Texture2D texture = _textureManager.GetTexture(obj.TextureKey);
            
            spriteBatch.Draw(
                texture,
                obj.InterpolatedPosition,
                null,
                Color.White,
                MathHelper.ToRadians(obj.Rotation),
                new Vector2(texture.Width / 2, texture.Height / 2),
                obj.Scale,
                SpriteEffects.None,
                0f
            );
            
            if (_debugMode)
            {
                spriteBatch.DrawString(
                    _debugFont,
                    $"ID: {obj.Id}",
                    obj.InterpolatedPosition + new Vector2(0, -30),
                    Color.Yellow,
                    0f,
                    new Vector2(_debugFont.MeasureString($"ID: {obj.Id}").X / 2, 0),
                    0.8f,
                    SpriteEffects.None,
                    0f
                );
            }
        }

        private void DrawAnimation(SpriteBatch spriteBatch, GridAnimation animation)
        {
            Vector2 position = GetHexPosition(animation.Row, animation.Column);
            float alpha = 1.0f;
            
            // Fade out in the last quarter of the animation
            if (animation.ElapsedTime > animation.Duration * 0.75f)
            {
                alpha = 1.0f - ((animation.ElapsedTime - (animation.Duration * 0.75f)) / (animation.Duration * 0.25f));
            }
            
            spriteBatch.Draw(
                animation.Texture,
                position,
                null,
                new Color(1f, 1f, 1f, alpha),
                MathHelper.ToRadians(animation.Rotation),
                new Vector2(animation.Texture.Width / 2, animation.Texture.Height / 2),
                animation.Scale,
                SpriteEffects.None,
                0f
            );
        }

        private void DrawEffect(SpriteBatch spriteBatch, GridEffect effect)
        {
            // This would be implemented based on the effect type
            // For now, just draw a simple circle
            Vector2 position = GetHexPosition(effect.Row, effect.Column);
            Texture2D texture = _textureManager.GetTexture("circle");
            
            float alpha = 1.0f;
            if (effect.ElapsedTime > effect.Duration * 0.75f)
            {
                alpha = 1.0f - ((effect.ElapsedTime - (effect.Duration * 0.75f)) / (effect.Duration * 0.25f));
            }
            
            spriteBatch.Draw(
                texture,
                position,
                null,
                new Color(effect.Color.R, effect.Color.G, effect.Color.B, (byte)(effect.Color.A * alpha)),
                0f,
                new Vector2(texture.Width / 2, texture.Height / 2),
                0.5f,
                SpriteEffects.None,
                0f
            );
        }

        private void DrawPath(SpriteBatch spriteBatch, GridPath path)
        {
            Texture2D pixel = _textureManager.GetTexture("pixel");
            
            for (int i = 0; i < path.RowPoints.Length - 1; i++)
            {
                Vector2 start = GetHexPosition(path.RowPoints[i], path.ColumnPoints[i]);
                Vector2 end = GetHexPosition(path.RowPoints[i + 1], path.ColumnPoints[i + 1]);
                
                DrawLine(spriteBatch, pixel, start, end, path.Color, 2f);
            }
        }

        private void DrawHighlight(SpriteBatch spriteBatch, HexHighlight highlight)
        {
            Vector2 position = GetHexPosition(highlight.Row, highlight.Column);
            Texture2D hexHighlight = _textureManager.GetTexture("hex_highlight");
            
            float alpha = 1.0f;
            if (highlight.ElapsedTime > highlight.Duration * 0.75f && highlight.Duration > 0)
            {
                alpha = 1.0f - ((highlight.ElapsedTime - (highlight.Duration * 0.75f)) / (highlight.Duration * 0.25f));
            }
            
            spriteBatch.Draw(
                hexHighlight,
                position,
                null,
                new Color(highlight.Color.R, highlight.Color.G, highlight.Color.B, (byte)(highlight.Color.A * alpha)),
                0f,
                new Vector2(hexHighlight.Width / 2, hexHighlight.Height / 2),
                _hexSize / 100f,
                SpriteEffects.None,
                0f
            );
        }

        private void DrawLine(SpriteBatch spriteBatch, Texture2D pixel, Vector2 start, Vector2 end, Color color, float thickness = 1f)
        {
            Vector2 direction = end - start;
            float length = direction.Length();
            
            if (length < 1)
                return;
            
            float angle = (float)Math.Atan2(direction.Y, direction.X);
            
            spriteBatch.Draw(
                pixel,
                start,
                null,
                color,
                angle,
                Vector2.Zero,
                new Vector2(length, thickness),
                SpriteEffects.None,
                0f
            );
        }

        private void DrawDebugInfo(SpriteBatch spriteBatch)
        {
            // Draw grid coordinates
            for (int row = 0; row < _rows; row++)
            {
                for (int column = 0; column < _columns; column++)
                {
                    Vector2 position = GetHexPosition(row, column);
                    spriteBatch.DrawString(
                        _debugFont,
                        $"{row},{column}",
                        position,
                        Color.Black, // Use black for coordinate text
                        0f,
                        new Vector2(_debugFont.MeasureString($"{row},{column}").X / 2, 0),
                        0.6f,
                        SpriteEffects.None,
                        0f
                    );
                }
            }
            
            // Draw object counts
            string debugText = $"Objects: {_objects.Count}\n" +
                              $"Animations: {_animations.Count}\n" +
                              $"Effects: {_effects.Count}\n" +
                              $"Paths: {_paths.Count}\n" +
                              $"Highlights: {_highlights.Count}";
            
            spriteBatch.DrawString(
                _debugFont,
                debugText,
                new Vector2(10, 10),
                Color.Black, // Use black for debug text
                0f,
                Vector2.Zero,
                1f,
                SpriteEffects.None,
                0f
            );
        }
    }
} 