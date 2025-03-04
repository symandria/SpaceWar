using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using SpaceWar.Core;
using System;

namespace SpaceWar.UI
{
    /// <summary>
    /// Renders a hex grid using SpriteBatch, matching the original Python implementation
    /// </summary>
    public class HexGridRenderer
    {
        private readonly HexGrid _hexGrid;
        private readonly Texture2D _hexTexture;
        private readonly GraphicsDevice _graphicsDevice;
        
        // Original game dimensions
        private const int ORIGINAL_GAME_WIDTH = 160;
        private const int ORIGINAL_GAME_HEIGHT = 160;

        // Constants from the original Python implementation
        private const int HEX_WIDTH = 15;
        private const int HEX_HEIGHT = 15;
        private const int HEX_HORIZONTAL_SPACING = 14;
        private const int HEX_VERTICAL_SPACING = 10;
        private const int HEX_ODD_ROW_OFFSET = 7;
        private const int GRID_LEFT_OFFSET = 2;
        private const int GRID_TOP_OFFSET = 15;
        
        // Scaling factor calculated based on window size
        private readonly float _scaleFactor;
        
        /// <summary>
        /// Gets the scale factor used for rendering
        /// </summary>
        public float ScaleFactor => _scaleFactor;
        
        /// <summary>
        /// Gets the offset used to center the grid in the window
        /// </summary>
        public Vector2 GridOffset { get; private set; }

        public HexGridRenderer(HexGrid hexGrid, GraphicsDevice graphicsDevice, float scale)
        {
            _hexGrid = hexGrid;
            _graphicsDevice = graphicsDevice;
            
            // Calculate the scaling factor based on the window size
            // We want to scale the entire grid to fit the window
            float scaleX = (float)graphicsDevice.Viewport.Width / ORIGINAL_GAME_WIDTH;
            float scaleY = (float)graphicsDevice.Viewport.Height / ORIGINAL_GAME_HEIGHT;
            _scaleFactor = Math.Min(scaleX, scaleY);
            
            // Calculate the grid offset
            float gridWidth = ORIGINAL_GAME_WIDTH * _scaleFactor;
            float gridHeight = ORIGINAL_GAME_HEIGHT * _scaleFactor;
            GridOffset = new Vector2(
                (_graphicsDevice.Viewport.Width - gridWidth) / 2,
                (_graphicsDevice.Viewport.Height - gridHeight) / 2
            );
            
            // Create the hex texture exactly as in the Python implementation
            _hexTexture = CreateHexTexture();
        }

        /// <summary>
        /// Creates a texture for a hexagon, matching the original Python implementation
        /// </summary>
        private Texture2D CreateHexTexture()
        {
            // Create a texture for the hex
            Texture2D texture = new Texture2D(_graphicsDevice, HEX_WIDTH, HEX_HEIGHT);
            Color[] data = new Color[HEX_WIDTH * HEX_HEIGHT];
            
            // Fill with transparent
            for (int i = 0; i < data.Length; i++)
            {
                data[i] = Color.Transparent;
            }
            
            // Draw the hex outline using the exact same points as in the Python implementation
            int[,] points = new int[,] {
                {7, 0}, {6, 1}, {5, 1}, {4, 2}, {3, 2}, {2, 3}, {1, 3}, {0, 4}, {0, 5}, {0, 6}, 
                {0, 7}, {0, 8}, {0, 9}, {0, 10}, {1, 11}, {2, 11}, {3, 12}, {4, 12}, {5, 13}, {6, 13}, 
                {7, 14}, {8, 13}, {9, 13}, {10, 12}, {11, 12}, {12, 11}, {13, 11}, {14, 10}, {14, 9}, {14, 8}, 
                {14, 7}, {14, 6}, {14, 5}, {14, 4}, {13, 3}, {12, 3}, {11, 2}, {10, 2}, {9, 1}, {8, 1}
            };
            
            // Set each point to black (or the foreground color)
            for (int i = 0; i < points.GetLength(0); i++)
            {
                int x = points[i, 0];
                int y = points[i, 1];
                if (x >= 0 && x < HEX_WIDTH && y >= 0 && y < HEX_HEIGHT)
                {
                    data[y * HEX_WIDTH + x] = Color.Black;
                }
            }
            
            texture.SetData(data);
            return texture;
        }

        /// <summary>
        /// Draws the hex grid
        /// </summary>
        public void Draw(SpriteBatch spriteBatch)
        {
            // Draw the hex grid exactly as in the Python implementation
            for (int row = 1; row <= _hexGrid.Rows; row++)
            {
                int maxColumns = _hexGrid.GetMaxColumnsForRow(row);
                
                for (int column = 1; column <= maxColumns; column++)
                {
                    // Calculate position using the original algorithm
                    Vector2 position = GetHexPosition(row, column);
                    
                    // Draw the hex
                    spriteBatch.Draw(
                        _hexTexture,
                        position,
                        null,
                        Color.Black,
                        0f,
                        Vector2.Zero,
                        _scaleFactor, // Use the calculated scale factor
                        SpriteEffects.None,
                        0f
                    );
                }
            }
        }

        /// <summary>
        /// Calculates the position of a hex using the original Python algorithm
        /// </summary>
        private Vector2 GetHexPosition(int row, int column)
        {
            // Use the exact same formula as in the Python implementation
            float x = GRID_LEFT_OFFSET + HEX_HORIZONTAL_SPACING * (column - 1) + ((row - 1) % 2) * HEX_ODD_ROW_OFFSET;
            float y = GRID_TOP_OFFSET + HEX_VERTICAL_SPACING * (row - 1);
            
            // Scale the position to fit the window
            x *= _scaleFactor;
            y *= _scaleFactor;
            
            // Add the grid offset to center it in the window
            return new Vector2(x + GridOffset.X, y + GridOffset.Y);
        }
        
        /// <summary>
        /// Converts hex coordinates to screen coordinates
        /// </summary>
        /// <param name="row">Row (1-based)</param>
        /// <param name="column">Column (1-based)</param>
        /// <returns>Screen coordinates</returns>
        public Vector2 HexToScreenCoords(int row, int column)
        {
            // Get the top-left position of the hex
            Vector2 position = GetHexPosition(row, column);
            
            // Add half the hex width and height to get the center
            position.X += (HEX_WIDTH * _scaleFactor) / 2;
            position.Y += (HEX_HEIGHT * _scaleFactor) / 2;
            
            return position;
        }
    }
} 