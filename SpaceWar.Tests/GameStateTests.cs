using NUnit.Framework;
using SpaceWar.Core;

namespace SpaceWar.Tests
{
    [TestFixture]
    public class GameStateTests
    {
        private GameState _gameState;

        [SetUp]
        public void Setup()
        {
            _gameState = new GameState();
        }

        [Test]
        public void NewGameState_ShouldNotBeRunning()
        {
            // Assert
            Assert.IsFalse(_gameState.IsRunning);
            Assert.AreEqual(0, _gameState.CurrentTurn);
        }

        [Test]
        public void StartGame_ShouldSetIsRunningToTrue()
        {
            // Act
            _gameState.StartGame();

            // Assert
            Assert.IsTrue(_gameState.IsRunning);
            Assert.AreEqual(1, _gameState.CurrentTurn);
        }

        [Test]
        public void EndGame_ShouldSetIsRunningToFalse()
        {
            // Arrange
            _gameState.StartGame();

            // Act
            _gameState.EndGame();

            // Assert
            Assert.IsFalse(_gameState.IsRunning);
        }

        [Test]
        public void NextTurn_WhenGameIsRunning_ShouldIncrementTurn()
        {
            // Arrange
            _gameState.StartGame();
            int initialTurn = _gameState.CurrentTurn;

            // Act
            _gameState.NextTurn();

            // Assert
            Assert.AreEqual(initialTurn + 1, _gameState.CurrentTurn);
        }

        [Test]
        public void NextTurn_WhenGameIsNotRunning_ShouldNotIncrementTurn()
        {
            // Arrange
            int initialTurn = _gameState.CurrentTurn;

            // Act
            _gameState.NextTurn();

            // Assert
            Assert.AreEqual(initialTurn, _gameState.CurrentTurn);
        }
    }
} 