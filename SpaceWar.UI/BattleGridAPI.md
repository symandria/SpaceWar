# BattleGrid API Documentation

This document outlines the API for the BattleGrid system in SpaceWar. The BattleGrid handles the rendering and management of the hex grid, game objects, animations, and visual effects.

## Grid Management

### `SetBackground(Texture2D background)`
Sets a background image (starscape, nebula, etc.) that appears behind all game elements.
- **Parameters:**
  - `background`: The texture to use as the background.

### `DrawGameGrid(int rows, int columns)`
Creates and displays a hex grid with specified dimensions.
- **Parameters:**
  - `rows`: Number of rows in the grid.
  - `columns`: Number of columns in the grid.

### `HideGameGrid()`
Hides the hex grid without destroying it.

### `ShowGameGrid()`
Makes a hidden grid visible again.

### `GetHexPosition(int row, int column)`
Returns the screen coordinates for a given hex cell.
- **Parameters:**
  - `row`: The row of the hex cell.
  - `column`: The column of the hex cell.
- **Returns:** Vector2 containing the screen coordinates.

### `GetHexFromScreenPosition(Vector2 screenPosition)`
Returns the hex coordinates for a given screen position.
- **Parameters:**
  - `screenPosition`: The screen position to convert.
- **Returns:** Tuple containing (row, column) or null if not on a valid hex.

## Object Management

### `CreateObject(string objectType, int row, int column, float rotation, int drawLayer = 0, float scale = 1.0f)`
Creates a game object at the specified hex position and returns its unique ID.
- **Parameters:**
  - `objectType`: The type of object to create (e.g., "ship", "asteroid").
  - `row`: The row position.
  - `column`: The column position.
  - `rotation`: The initial rotation in degrees.
  - `drawLayer`: The layer to draw the object on (higher numbers are drawn on top).
  - `scale`: The scale of the object.
- **Returns:** Integer ID of the created object.

### `DeleteObject(int objectId)`
Removes an object from the grid.
- **Parameters:**
  - `objectId`: The ID of the object to delete.
- **Returns:** Boolean indicating success.

### `GetObjectPosition(int objectId)`
Returns the current hex position of an object.
- **Parameters:**
  - `objectId`: The ID of the object.
- **Returns:** Tuple containing (row, column).

### `SetObjectVisibility(int objectId, bool isVisible)`
Shows or hides an object without deleting it.
- **Parameters:**
  - `objectId`: The ID of the object.
  - `isVisible`: Whether the object should be visible.

### `SetObjectTexture(int objectId, string textureKey)`
Changes the appearance of an existing object.
- **Parameters:**
  - `objectId`: The ID of the object.
  - `textureKey`: The key for the new texture.

### `SetObjectRotation(int objectId, float rotation)`
Immediately rotates an object to a specific angle.
- **Parameters:**
  - `objectId`: The ID of the object.
  - `rotation`: The rotation in degrees.

### `SetObjectScale(int objectId, float scale)`
Changes the size of an object.
- **Parameters:**
  - `objectId`: The ID of the object.
  - `scale`: The new scale factor.

### `SetObjectDrawLayer(int objectId, int drawLayer)`
Changes the drawing layer of an object.
- **Parameters:**
  - `objectId`: The ID of the object.
  - `drawLayer`: The new draw layer (higher numbers are drawn on top).

## Movement and Animation

### `MoveObject(int objectId, int targetRow, int targetColumn, float speed)`
Moves an object smoothly to a target hex at the specified speed.
- **Parameters:**
  - `objectId`: The ID of the object to move.
  - `targetRow`: The target row.
  - `targetColumn`: The target column.
  - `speed`: The speed in hex cells per second.
- **Returns:** Boolean indicating if the movement was started successfully.

### `RotateObject(int objectId, float targetRotation, float rotationSpeed)`
Smoothly rotates an object to a target angle.
- **Parameters:**
  - `objectId`: The ID of the object.
  - `targetRotation`: The target rotation in degrees.
  - `rotationSpeed`: The rotation speed in degrees per second.

### `StopObject(int objectId)`
Immediately stops any movement or rotation of an object.
- **Parameters:**
  - `objectId`: The ID of the object.

### `IsObjectMoving(int objectId)`
Returns whether an object is currently in motion.
- **Parameters:**
  - `objectId`: The ID of the object.
- **Returns:** Boolean indicating if the object is moving.

### `PlayAnimation(string animationType, int row, int column, float duration, float scale = 1.0f, int drawLayer = 10)`
Plays a predefined animation at a hex location.
- **Parameters:**
  - `animationType`: The type of animation (e.g., "explosion", "shield").
  - `row`: The row position.
  - `column`: The column position.
  - `duration`: The duration of the animation in seconds.
  - `scale`: The scale of the animation.
  - `drawLayer`: The layer to draw the animation on.

### `PlayCustomAnimation(Texture2D texture, int row, int column, float duration, float scale = 1.0f, float rotation = 0f, int drawLayer = 10)`
Plays a custom animation at a hex location.
- **Parameters:**
  - `texture`: The texture to use for the animation.
  - `row`: The row position.
  - `column`: The column position.
  - `duration`: The duration of the animation in seconds.
  - `scale`: The scale of the animation.
  - `rotation`: The rotation in degrees.
  - `drawLayer`: The layer to draw the animation on.

## Effects and Visual Enhancements

### `DrawPath(int[] rowPoints, int[] columnPoints, Color color, float duration = 0, int drawLayer = 5)`
Draws a path between hex points (temporary if duration > 0).
- **Parameters:**
  - `rowPoints`: Array of row coordinates.
  - `columnPoints`: Array of column coordinates.
  - `color`: The color of the path.
  - `duration`: How long the path should remain visible (0 = permanent).
  - `drawLayer`: The layer to draw the path on.

### `HighlightHex(int row, int column, Color color, float duration = 0, int drawLayer = 1)`
Highlights a specific hex (temporary if duration > 0).
- **Parameters:**
  - `row`: The row of the hex.
  - `column`: The column of the hex.
  - `color`: The highlight color.
  - `duration`: How long the highlight should remain visible (0 = permanent).
  - `drawLayer`: The layer to draw the highlight on.

### `HighlightRange(int centerRow, int centerColumn, int minRange, int maxRange, Color color, float duration = 0, int drawLayer = 1)`
Highlights all hexes within a range band (from minRange to maxRange).
- **Parameters:**
  - `centerRow`: The center row.
  - `centerColumn`: The center column.
  - `minRange`: The minimum range (inclusive).
  - `maxRange`: The maximum range (inclusive).
  - `color`: The highlight color.
  - `duration`: How long the highlight should remain visible (0 = permanent).
  - `drawLayer`: The layer to draw the highlight on.

### `DrawLine(int startRow, int startColumn, int endRow, int endColumn, Color color, float duration = 0, int drawLayer = 5)`
Draws a line between two hex cells.
- **Parameters:**
  - `startRow`: The starting row.
  - `startColumn`: The starting column.
  - `endRow`: The ending row.
  - `endColumn`: The ending column.
  - `color`: The line color.
  - `duration`: How long the line should remain visible (0 = permanent).
  - `drawLayer`: The layer to draw the line on.

### `AddParticleEffect(string effectType, int row, int column, float duration, int drawLayer = 10)`
Adds a particle effect (explosion, energy, etc.) at a hex location.
- **Parameters:**
  - `effectType`: The type of effect.
  - `row`: The row position.
  - `column`: The column position.
  - `duration`: The duration of the effect in seconds.
  - `drawLayer`: The layer to draw the effect on.

## Game State and UI Integration

### `SetDebugMode(bool enabled)`
Toggles display of debug information like object IDs, paths, etc.
- **Parameters:**
  - `enabled`: Whether debug mode should be enabled.

### `ClearAll()`
Removes all objects and effects from the grid.

### `GetObjectsInRange(int centerRow, int centerColumn, int range)`
Returns IDs of all objects within a certain range.
- **Parameters:**
  - `centerRow`: The center row.
  - `centerColumn`: The center column.
  - `range`: The range to check.
- **Returns:** Array of object IDs.

### `RegisterObjectMovementCallback(Action<int, int, int> callback)`
Registers a function to be called when an object completes movement.
- **Parameters:**
  - `callback`: The function to call with parameters (objectId, finalRow, finalColumn).

### `RegisterObjectDestroyedCallback(Action<int> callback)`
Registers a function to be called when an object is destroyed.
- **Parameters:**
  - `callback`: The function to call with parameter (objectId).

## Implementation Notes

- The BattleGrid uses a fixed timestep of 100 updates per second for smooth animations.
- Draw layers determine the order in which elements are drawn:
  - Lower numbers are drawn first (background)
  - Higher numbers are drawn last (foreground)
  - Suggested layer ranges:
    - 0-4: Background elements (grid, hex highlights)
    - 5-9: Mid-level elements (paths, lines)
    - 10-14: Foreground elements (ships, objects)
    - 15+: Effects and UI elements
- All rotations are specified in degrees for ease of use (converted internally to radians).
- Duration of 0 for visual effects means they will remain until explicitly cleared. 