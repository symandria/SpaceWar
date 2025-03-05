using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using System;

namespace SpaceWar.UI
{
    /// <summary>
    /// Represents a game object on the battle grid.
    /// </summary>
    public class GridObject
    {
        /// <summary>
        /// Unique identifier for the object.
        /// </summary>
        public int Id { get; }

        /// <summary>
        /// Type of the object (e.g., "ship", "asteroid").
        /// </summary>
        public string ObjectType { get; }

        /// <summary>
        /// Current row position on the grid.
        /// </summary>
        public int CurrentRow { get; set; }

        /// <summary>
        /// Current column position on the grid.
        /// </summary>
        public int CurrentColumn { get; set; }

        /// <summary>
        /// Target row position for movement.
        /// </summary>
        public int? TargetRow { get; set; }

        /// <summary>
        /// Target column position for movement.
        /// </summary>
        public int? TargetColumn { get; set; }

        /// <summary>
        /// Current rotation in degrees.
        /// </summary>
        public float Rotation { get; set; }

        /// <summary>
        /// Target rotation in degrees.
        /// </summary>
        public float? TargetRotation { get; set; }

        /// <summary>
        /// Rotation speed in degrees per second.
        /// </summary>
        public float RotationSpeed { get; set; }

        /// <summary>
        /// Movement speed in hex cells per second.
        /// </summary>
        public float MovementSpeed { get; set; }

        /// <summary>
        /// Scale of the object.
        /// </summary>
        public float Scale { get; set; }

        /// <summary>
        /// Layer to draw the object on (higher numbers are drawn on top).
        /// </summary>
        public int DrawLayer { get; set; }

        /// <summary>
        /// Whether the object is visible.
        /// </summary>
        public bool IsVisible { get; set; } = true;

        /// <summary>
        /// Current texture key for the object.
        /// </summary>
        public string TextureKey { get; set; }

        /// <summary>
        /// Current interpolated position for smooth movement.
        /// </summary>
        public Vector2 InterpolatedPosition { get; set; }

        /// <summary>
        /// Creates a new grid object.
        /// </summary>
        public GridObject(int id, string objectType, int row, int column, float rotation, int drawLayer, float scale, string textureKey)
        {
            Id = id;
            ObjectType = objectType;
            CurrentRow = row;
            CurrentColumn = column;
            Rotation = rotation;
            DrawLayer = drawLayer;
            Scale = scale;
            TextureKey = textureKey;
        }

        /// <summary>
        /// Whether the object is currently moving.
        /// </summary>
        public bool IsMoving => TargetRow.HasValue && TargetColumn.HasValue;

        /// <summary>
        /// Whether the object is currently rotating.
        /// </summary>
        public bool IsRotating => TargetRotation.HasValue;
    }

    /// <summary>
    /// Represents a visual effect on the battle grid.
    /// </summary>
    public class GridEffect
    {
        /// <summary>
        /// Unique identifier for the effect.
        /// </summary>
        public int Id { get; }

        /// <summary>
        /// Type of the effect.
        /// </summary>
        public string EffectType { get; }

        /// <summary>
        /// Row position on the grid.
        /// </summary>
        public int Row { get; }

        /// <summary>
        /// Column position on the grid.
        /// </summary>
        public int Column { get; }

        /// <summary>
        /// Duration of the effect in seconds (0 = permanent).
        /// </summary>
        public float Duration { get; }

        /// <summary>
        /// Elapsed time since the effect started.
        /// </summary>
        public float ElapsedTime { get; set; }

        /// <summary>
        /// Layer to draw the effect on (higher numbers are drawn on top).
        /// </summary>
        public int DrawLayer { get; }

        /// <summary>
        /// Color of the effect.
        /// </summary>
        public Color Color { get; }

        /// <summary>
        /// Whether the effect is complete.
        /// </summary>
        public bool IsComplete => Duration > 0 && ElapsedTime >= Duration;

        /// <summary>
        /// Creates a new grid effect.
        /// </summary>
        public GridEffect(int id, string effectType, int row, int column, float duration, int drawLayer, Color color)
        {
            Id = id;
            EffectType = effectType;
            Row = row;
            Column = column;
            Duration = duration;
            DrawLayer = drawLayer;
            Color = color;
            ElapsedTime = 0;
        }
    }

    /// <summary>
    /// Represents a path between hex points.
    /// </summary>
    public class GridPath
    {
        /// <summary>
        /// Unique identifier for the path.
        /// </summary>
        public int Id { get; }

        /// <summary>
        /// Array of row coordinates.
        /// </summary>
        public int[] RowPoints { get; }

        /// <summary>
        /// Array of column coordinates.
        /// </summary>
        public int[] ColumnPoints { get; }

        /// <summary>
        /// Color of the path.
        /// </summary>
        public Color Color { get; }

        /// <summary>
        /// Duration of the path in seconds (0 = permanent).
        /// </summary>
        public float Duration { get; }

        /// <summary>
        /// Elapsed time since the path was created.
        /// </summary>
        public float ElapsedTime { get; set; }

        /// <summary>
        /// Layer to draw the path on (higher numbers are drawn on top).
        /// </summary>
        public int DrawLayer { get; }

        /// <summary>
        /// Whether the path is complete.
        /// </summary>
        public bool IsComplete => Duration > 0 && ElapsedTime >= Duration;

        /// <summary>
        /// Creates a new grid path.
        /// </summary>
        public GridPath(int id, int[] rowPoints, int[] columnPoints, Color color, float duration, int drawLayer)
        {
            Id = id;
            RowPoints = rowPoints;
            ColumnPoints = columnPoints;
            Color = color;
            Duration = duration;
            DrawLayer = drawLayer;
            ElapsedTime = 0;
        }
    }

    /// <summary>
    /// Represents a hex highlight on the battle grid.
    /// </summary>
    public class HexHighlight
    {
        /// <summary>
        /// Unique identifier for the highlight.
        /// </summary>
        public int Id { get; }

        /// <summary>
        /// Row position on the grid.
        /// </summary>
        public int Row { get; }

        /// <summary>
        /// Column position on the grid.
        /// </summary>
        public int Column { get; }

        /// <summary>
        /// Color of the highlight.
        /// </summary>
        public Color Color { get; }

        /// <summary>
        /// Duration of the highlight in seconds (0 = permanent).
        /// </summary>
        public float Duration { get; }

        /// <summary>
        /// Elapsed time since the highlight was created.
        /// </summary>
        public float ElapsedTime { get; set; }

        /// <summary>
        /// Layer to draw the highlight on (higher numbers are drawn on top).
        /// </summary>
        public int DrawLayer { get; }

        /// <summary>
        /// Whether the highlight is complete.
        /// </summary>
        public bool IsComplete => Duration > 0 && ElapsedTime >= Duration;

        /// <summary>
        /// Creates a new hex highlight.
        /// </summary>
        public HexHighlight(int id, int row, int column, Color color, float duration, int drawLayer)
        {
            Id = id;
            Row = row;
            Column = column;
            Color = color;
            Duration = duration;
            DrawLayer = drawLayer;
            ElapsedTime = 0;
        }
    }

    /// <summary>
    /// Represents an animation on the battle grid.
    /// </summary>
    public class GridAnimation
    {
        /// <summary>
        /// Unique identifier for the animation.
        /// </summary>
        public int Id { get; }

        /// <summary>
        /// Type of the animation.
        /// </summary>
        public string AnimationType { get; }

        /// <summary>
        /// Texture to use for the animation.
        /// </summary>
        public Texture2D Texture { get; }

        /// <summary>
        /// Row position on the grid.
        /// </summary>
        public int Row { get; }

        /// <summary>
        /// Column position on the grid.
        /// </summary>
        public int Column { get; }

        /// <summary>
        /// Duration of the animation in seconds.
        /// </summary>
        public float Duration { get; }

        /// <summary>
        /// Elapsed time since the animation started.
        /// </summary>
        public float ElapsedTime { get; set; }

        /// <summary>
        /// Scale of the animation.
        /// </summary>
        public float Scale { get; }

        /// <summary>
        /// Rotation of the animation in degrees.
        /// </summary>
        public float Rotation { get; }

        /// <summary>
        /// Layer to draw the animation on (higher numbers are drawn on top).
        /// </summary>
        public int DrawLayer { get; }

        /// <summary>
        /// Whether the animation is complete.
        /// </summary>
        public bool IsComplete => ElapsedTime >= Duration;

        /// <summary>
        /// Creates a new grid animation.
        /// </summary>
        public GridAnimation(int id, string animationType, Texture2D texture, int row, int column, float duration, float scale, float rotation, int drawLayer)
        {
            Id = id;
            AnimationType = animationType;
            Texture = texture;
            Row = row;
            Column = column;
            Duration = duration;
            Scale = scale;
            Rotation = rotation;
            DrawLayer = drawLayer;
            ElapsedTime = 0;
        }
    }
} 