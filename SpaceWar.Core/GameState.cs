namespace SpaceWar.Core
{
    /// <summary>
    /// Represents the current state of the game
    /// </summary>
    public class GameState
    {
        /// <summary>
        /// Gets or sets whether the game is currently running
        /// </summary>
        public bool IsRunning { get; set; }

        /// <summary>
        /// Gets or sets the current game turn
        /// </summary>
        public int CurrentTurn { get; set; }

        /// <summary>
        /// Creates a new game state
        /// </summary>
        public GameState()
        {
            IsRunning = false;
            CurrentTurn = 0;
        }

        /// <summary>
        /// Starts a new game
        /// </summary>
        public void StartGame()
        {
            IsRunning = true;
            CurrentTurn = 1;
        }

        /// <summary>
        /// Ends the current game
        /// </summary>
        public void EndGame()
        {
            IsRunning = false;
        }

        /// <summary>
        /// Advances to the next turn
        /// </summary>
        public void NextTurn()
        {
            if (IsRunning)
            {
                CurrentTurn++;
            }
        }
    }
} 