using NUnit.Framework;
using SpaceWar.Core;
using System.Numerics;

namespace SpaceWar.Tests
{
    [TestFixture]
    public class HexGridTests
    {
        private HexGrid _hexGrid;

        [SetUp]
        public void Setup()
        {
            _hexGrid = new HexGrid(15, 11); // Using the same dimensions as the original game
        }

        [Test]
        public void HexToCoords_ShouldReturnCorrectCoordinates()
        {
            // Arrange
            int row = 1;
            int column = 1;

            // Act
            Vector2 coords = _hexGrid.HexToCoords(row, column);

            // Assert
            Assert.AreEqual(5, coords.X);
            Assert.AreEqual(18, coords.Y);
        }

        [Test]
        public void CoordsToHex_WithValidCoordinates_ShouldReturnCorrectHex()
        {
            // Arrange
            Vector2 coords = new Vector2(5, 18);

            // Act
            var hex = _hexGrid.CoordsToHex(coords);

            // Assert
            Assert.IsNotNull(hex);
            Assert.AreEqual(1, hex.Value.Row);
            Assert.AreEqual(1, hex.Value.Column);
        }

        [Test]
        public void CoordsToHex_WithInvalidCoordinates_ShouldReturnNull()
        {
            // Arrange
            Vector2 coords = new Vector2(1, 1);

            // Act
            var hex = _hexGrid.CoordsToHex(coords);

            // Assert
            Assert.IsNull(hex);
        }

        [Test]
        public void HexDistance_ShouldReturnCorrectDistance()
        {
            // Arrange
            var hex1 = (1, 1);
            var hex2 = (3, 3);

            // Act
            int distance = _hexGrid.HexDistance(hex1, hex2);

            // Assert
            Assert.AreEqual(3, distance);
        }

        [Test]
        public void GetAllHexes_ShouldReturnCorrectNumberOfHexes()
        {
            // Act
            var hexes = _hexGrid.GetAllHexes();

            // Assert
            Assert.AreEqual(_hexGrid.Rows * _hexGrid.Columns, hexes.Length);
        }
    }
} 