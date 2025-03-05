using System;
using System.Threading;

namespace SpaceWar.UI
{
    /// <summary>
    /// The main entry point for the application.
    /// </summary>
    public static class Program
    {
        [STAThread]
        static void Main()
        {
            Console.WriteLine("SpaceWar application starting...");
            
            try
            {
                Console.WriteLine("Creating game instance...");
                using (var game = new BattleGridTest())
                {
                    Console.WriteLine("Game instance created. Running game...");
                    game.Run();
                    Console.WriteLine("Game.Run() completed.");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error running game: {ex}");
                Console.WriteLine($"ERROR running game: {ex}");
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey();
            }
            
            Console.WriteLine("Application ending. Press any key to close this window...");
            Console.ReadKey();
        }
    }
} 