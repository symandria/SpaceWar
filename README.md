# SpaceWar

A C# implementation of the SpaceWar game, migrated from Python using MonoGame.

## Project Structure

- **SpaceWar.Core**: Contains the game logic and state management
- **SpaceWar.UI**: Contains the MonoGame implementation for rendering and input handling
- **SpaceWar.Tests**: Contains unit tests for the game logic

## Development Approach

This project follows a test-driven development (TDD) approach with a clear separation between game logic and presentation:

1. Game state and logic are implemented in the Core project
2. Rendering and input handling are implemented in the UI project
3. All game logic is covered by unit tests

## Getting Started

### Prerequisites

- Visual Studio 2022 with .NET desktop development workload
- MonoGame extension for Visual Studio
- .NET 6.0 SDK

### Building and Running

1. Open the solution in Visual Studio
2. Build the solution
3. Run the SpaceWar.UI project

## Testing

Run the tests using the Test Explorer in Visual Studio or using the `dotnet test` command. 