using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using System;

namespace SpaceWar.UI
{
    /// <summary>
    /// Interface for the BattleGrid system that handles rendering and management of the hex grid,
    /// game objects, animations, and visual effects.
    /// </summary>
    public interface IBattleGrid
    {
        #region Grid Management

        /// <summary>
        /// Sets a background image that appears behind all game elements.
        /// </summary>
        /// <param name="background">The texture to use as the background.</param>
        void SetBackground(Texture2D background);

        /// <summary>
        /// Creates and displays a hex grid with specified dimensions.
        /// </summary>
        /// <param name="rows">Number of rows in the grid.</param>
        /// <param name="columns">Number of columns in the grid.</param>
        void DrawGameGrid(int rows, int columns);

        /// <summary>
        /// Hides the hex grid without destroying it.
        /// </summary>
        void HideGameGrid();

        /// <summary>
        /// Makes a hidden grid visible again.
        /// </summary>
        void ShowGameGrid();

        /// <summary>
        /// Returns the screen coordinates for a given hex cell.
        /// </summary>
        /// <param name="row">The row of the hex cell.</param>
        /// <param name="column">The column of the hex cell.</param>
        /// <returns>Vector2 containing the screen coordinates.</returns>
        Vector2 GetHexPosition(int row, int column);

        /// <summary>
        /// Returns the hex coordinates for a given screen position.
        /// </summary>
        /// <param name="screenPosition">The screen position to convert.</param>
        /// <returns>Tuple containing (row, column) or null if not on a valid hex.</returns>
        (int Row, int Column)? GetHexFromScreenPosition(Vector2 screenPosition);

        #endregion

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
        int CreateObject(string objectType, int row, int column, float rotation, int drawLayer = 0, float scale = 1.0f);

        /// <summary>
        /// Removes an object from the grid.
        /// </summary>
        /// <param name="objectId">The ID of the object to delete.</param>
        /// <returns>Boolean indicating success.</returns>
        bool DeleteObject(int objectId);

        /// <summary>
        /// Returns the current hex position of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <returns>Tuple containing (row, column).</returns>
        (int Row, int Column) GetObjectPosition(int objectId);

        /// <summary>
        /// Shows or hides an object without deleting it.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="isVisible">Whether the object should be visible.</param>
        void SetObjectVisibility(int objectId, bool isVisible);

        /// <summary>
        /// Changes the appearance of an existing object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="textureKey">The key for the new texture.</param>
        void SetObjectTexture(int objectId, string textureKey);

        /// <summary>
        /// Immediately rotates an object to a specific angle.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="rotation">The rotation in degrees.</param>
        void SetObjectRotation(int objectId, float rotation);

        /// <summary>
        /// Changes the size of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="scale">The new scale factor.</param>
        void SetObjectScale(int objectId, float scale);

        /// <summary>
        /// Changes the drawing layer of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="drawLayer">The new draw layer (higher numbers are drawn on top).</param>
        void SetObjectDrawLayer(int objectId, int drawLayer);

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
        bool MoveObject(int objectId, int targetRow, int targetColumn, float speed);

        /// <summary>
        /// Smoothly rotates an object to a target angle.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <param name="targetRotation">The target rotation in degrees.</param>
        /// <param name="rotationSpeed">The rotation speed in degrees per second.</param>
        void RotateObject(int objectId, float targetRotation, float rotationSpeed);

        /// <summary>
        /// Immediately stops any movement or rotation of an object.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        void StopObject(int objectId);

        /// <summary>
        /// Returns whether an object is currently in motion.
        /// </summary>
        /// <param name="objectId">The ID of the object.</param>
        /// <returns>Boolean indicating if the object is moving.</returns>
        bool IsObjectMoving(int objectId);

        /// <summary>
        /// Plays a predefined animation at a hex location.
        /// </summary>
        /// <param name="animationType">The type of animation (e.g., "explosion", "shield").</param>
        /// <param name="row">The row position.</param>
        /// <param name="column">The column position.</param>
        /// <param name="duration">The duration of the animation in seconds.</param>
        /// <param name="scale">The scale of the animation.</param>
        /// <param name="drawLayer">The layer to draw the animation on.</param>
        void PlayAnimation(string animationType, int row, int column, float duration, float scale = 1.0f, int drawLayer = 10);

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
        void PlayCustomAnimation(Texture2D texture, int row, int column, float duration, float scale = 1.0f, float rotation = 0f, int drawLayer = 10);

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
        void DrawPath(int[] rowPoints, int[] columnPoints, Color color, float duration = 0, int drawLayer = 5);

        /// <summary>
        /// Highlights a specific hex (temporary if duration > 0).
        /// </summary>
        /// <param name="row">The row of the hex.</param>
        /// <param name="column">The column of the hex.</param>
        /// <param name="color">The highlight color.</param>
        /// <param name="duration">How long the highlight should remain visible (0 = permanent).</param>
        /// <param name="drawLayer">The layer to draw the highlight on.</param>
        void HighlightHex(int row, int column, Color color, float duration = 0, int drawLayer = 1);

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
        void HighlightRange(int centerRow, int centerColumn, int minRange, int maxRange, Color color, float duration = 0, int drawLayer = 1);

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
        void DrawLine(int startRow, int startColumn, int endRow, int endColumn, Color color, float duration = 0, int drawLayer = 5);

        /// <summary>
        /// Adds a particle effect (explosion, energy, etc.) at a hex location.
        /// </summary>
        /// <param name="effectType">The type of effect.</param>
        /// <param name="row">The row position.</param>
        /// <param name="column">The column position.</param>
        /// <param name="duration">The duration of the effect in seconds.</param>
        /// <param name="drawLayer">The layer to draw the effect on.</param>
        void AddParticleEffect(string effectType, int row, int column, float duration, int drawLayer = 10);

        #endregion

        #region Game State and UI Integration

        /// <summary>
        /// Toggles display of debug information like object IDs, paths, etc.
        /// </summary>
        /// <param name="enabled">Whether debug mode should be enabled.</param>
        void SetDebugMode(bool enabled);

        /// <summary>
        /// Removes all objects and effects from the grid.
        /// </summary>
        void ClearAll();

        /// <summary>
        /// Returns IDs of all objects within a certain range.
        /// </summary>
        /// <param name="centerRow">The center row.</param>
        /// <param name="centerColumn">The center column.</param>
        /// <param name="range">The range to check.</param>
        /// <returns>Array of object IDs.</returns>
        int[] GetObjectsInRange(int centerRow, int centerColumn, int range);

        /// <summary>
        /// Returns IDs of all objects at a specific hex position.
        /// </summary>
        /// <param name="row">The row of the hex.</param>
        /// <param name="column">The column of the hex.</param>
        /// <returns>Array of object IDs at the specified position.</returns>
        int[] GetObjectsAtPosition(int row, int column);

        /// <summary>
        /// Registers a function to be called when an object completes movement.
        /// </summary>
        /// <param name="callback">The function to call with parameters (objectId, finalRow, finalColumn).</param>
        void RegisterObjectMovementCallback(Action<int, int, int> callback);

        /// <summary>
        /// Registers a function to be called when an object is destroyed.
        /// </summary>
        /// <param name="callback">The function to call with parameter (objectId).</param>
        void RegisterObjectDestroyedCallback(Action<int> callback);

        #endregion

        /// <summary>
        /// Updates the battle grid state.
        /// </summary>
        /// <param name="gameTime">The game time.</param>
        void Update(GameTime gameTime);

        /// <summary>
        /// Draws the battle grid and all its elements.
        /// </summary>
        /// <param name="spriteBatch">The sprite batch to use for drawing.</param>
        void Draw(SpriteBatch spriteBatch);
    }
} 