using NUnit.Framework;
using Moq;
using Microsoft.Xna.Framework;
using SpaceWar.UI;

namespace SpaceWar.Tests
{
    [TestFixture]
    public class GameInitializerTests
    {
        private GameInitializer _initializer;
        private Mock<GraphicsDeviceManager> _graphicsMock;
        private Mock<GameWindow> _windowMock;

        [SetUp]
        public void Setup()
        {
            _initializer = new GameInitializer();
            _graphicsMock = new Mock<GraphicsDeviceManager>(new Game());
            _windowMock = new Mock<GameWindow>();
        }

        [Test]
        public void DefaultValues_ShouldBeCorrect()
        {
            // Assert
            Assert.AreEqual(800, _initializer.WindowWidth);
            Assert.AreEqual(600, _initializer.WindowHeight);
            Assert.AreEqual("SpaceWar", _initializer.WindowTitle);
            Assert.IsTrue(_initializer.IsMouseVisible);
        }

        [Test]
        public void ConfigureGraphics_ShouldSetCorrectValues()
        {
            // Arrange
            _initializer.WindowWidth = 1024;
            _initializer.WindowHeight = 768;

            // Act
            _initializer.ConfigureGraphics(_graphicsMock.Object);

            // Assert
            _graphicsMock.VerifySet(g => g.PreferredBackBufferWidth = 1024);
            _graphicsMock.VerifySet(g => g.PreferredBackBufferHeight = 768);
        }

        [Test]
        public void ConfigureWindow_ShouldSetCorrectTitle()
        {
            // Arrange
            _initializer.WindowTitle = "Test Title";

            // Act
            _initializer.ConfigureWindow(_windowMock.Object);

            // Assert
            _windowMock.VerifySet(w => w.Title = "Test Title");
        }
    }
} 