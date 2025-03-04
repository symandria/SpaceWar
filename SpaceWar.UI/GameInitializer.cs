using Microsoft.Xna.Framework;
using System;
using System.Diagnostics;

namespace SpaceWar.UI
{
    /// <summary>
    /// Provides testable initialization for the game
    /// </summary>
    public class GameInitializer
    {
        /// <summary>
        /// Gets or sets the window width
        /// </summary>
        public int WindowWidth { get; set; } = 800;

        /// <summary>
        /// Gets or sets the window height
        /// </summary>
        public int WindowHeight { get; set; } = 600;

        /// <summary>
        /// Gets or sets the window title
        /// </summary>
        public string WindowTitle { get; set; } = "SpaceWar";

        /// <summary>
        /// Gets or sets whether the mouse cursor is visible
        /// </summary>
        public bool IsMouseVisible { get; set; } = true;

        /// <summary>
        /// Configures the graphics device manager
        /// </summary>
        /// <param name="graphics">The graphics device manager to configure</param>
        public void ConfigureGraphics(GraphicsDeviceManager graphics)
        {
            try
            {
                Debug.WriteLine($"Configuring graphics: Width={WindowWidth}, Height={WindowHeight}");
                graphics.PreferredBackBufferWidth = WindowWidth;
                graphics.PreferredBackBufferHeight = WindowHeight;
                graphics.ApplyChanges();
                Debug.WriteLine("Graphics configured successfully");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error configuring graphics: {ex}");
                Console.WriteLine($"Error configuring graphics: {ex}");
                throw;
            }
        }

        /// <summary>
        /// Configures the game window
        /// </summary>
        /// <param name="window">The game window to configure</param>
        public void ConfigureWindow(GameWindow window)
        {
            try
            {
                Debug.WriteLine($"Configuring window: Title={WindowTitle}");
                window.Title = WindowTitle;
                Debug.WriteLine("Window configured successfully");
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error configuring window: {ex}");
                Console.WriteLine($"Error configuring window: {ex}");
                throw;
            }
        }
    }
} 