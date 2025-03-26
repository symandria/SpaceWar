# AI State: Test-Driven Development (TDD)

## Purpose
This state guides the AI to develop features using Test-Driven Development, ensuring all code is tested, functional, and maintainable from the start.

## When to Use This State
- When implementing new features or components
- When fixing bugs that can be replicated with a test
- When extending existing functionality with clear requirements

## The TDD Workflow

### 1. RED Phase - Write a Failing Test
```
[STATE: TDD-RED] Writing failing test for {feature/functionality}
```

- Write a test that clearly defines expected behavior
- Ensure the test is minimal and focuses on a single aspect
- Verify the test fails (either compilation failure or test failure)
- Explain why the test is failing

### 2. GREEN Phase - Make the Test Pass
```
[STATE: TDD-GREEN] Implementing minimal code to pass test
```

- Write the minimal implementation to make the test pass
- Don't worry about code quality yet - just make it work
- Verify the test now passes
- Resist the urge to implement functionality not covered by tests

### 3. REFACTOR Phase - Improve the Code
```
[STATE: TDD-REFACTOR] Improving code while maintaining test success
```

- Improve code quality while keeping tests passing
- Apply SOLID principles, remove duplication, improve names
- Run tests after each significant change
- Only refactor what's covered by tests

## Testing Guidelines

### Test Structure
- Use descriptive test names following `WhenX_ThenY` pattern
- Structure tests with Arrange, Act, Assert pattern
- Make assertion failures descriptive and actionable

### What to Test
- Public APIs and interfaces
- Edge cases and error conditions
- Important business rules and game mechanics
- State transitions

### What Not to Test
- Implementation details that might change
- Framework code (MonoGame, etc.)
- Generated code or trivial code (getters/setters)

## Mocking External Dependencies

### For MonoGame
```csharp
// Example of mocking GraphicsDevice
public class MockGraphicsDevice : IGraphicsDeviceService
{
    public GraphicsDevice GraphicsDevice => new GraphicsDevice(
        MockGraphicsAdapter.CreateGraphicsAdapter(), 
        GraphicsProfile.Reach, 
        new PresentationParameters());
}
```

### For Game Components
```csharp
// Example of a test stub for a GameObject
public class StubGameObject : GameObject
{
    public bool UpdateWasCalled { get; private set; }
    
    public override void Update(GameTime gameTime)
    {
        UpdateWasCalled = true;
        base.Update(gameTime);
    }
}
```

## Examples

### Testing Game Logic
```csharp
[STATE: TDD-RED] Writing failing test for ship movement
[TEST]
[Fact]
public void WhenShipMovesForward_PositionChangesInFacingDirection()
{
    // Arrange
    var ship = new Ship
    {
        Position = Vector2.Zero,
        Rotation = 0 // Facing right
    };
    
    // Act
    ship.MoveForward(distance: 5);
    
    // Assert
    Assert.Equal(new Vector2(5, 0), ship.Position);
}
```

### Testing UI Components
```csharp
[STATE: TDD-RED] Writing failing test for button click behavior
[TEST]
[Fact]
public void WhenButtonIsClicked_ThenActionIsTriggered()
{
    // Arrange
    bool actionTriggered = false;
    var button = new Button(
        onClick: () => actionTriggered = true,
        position: new Vector2(10, 10),
        size: new Vector2(100, 50)
    );
    
    // Act
    button.HandleInput(new MockInputState
    {
        MousePosition = new Vector2(50, 30),
        IsLeftMouseButtonPressed = true,
        WasLeftMouseButtonPressed = false
    });
    
    // Assert
    Assert.True(actionTriggered);
}
```

## Common Pitfalls to Avoid

- **Writing Tests After Implementation**: Defeats the purpose of TDD
- **Testing Too Much at Once**: Keep tests focused on single behaviors
- **Over-Engineering**: Implement only what's needed by current tests
- **Skipping Refactoring**: Quality matters; clean up your code
- **Breaking Test Isolation**: Tests should not depend on each other
- **Testing Implementation Details**: Focus on behavior, not how it's implemented

## Transitioning to Other States

When you encounter an issue that needs a different approach:

- **To EXPLORATORY**: `[TRANSITION: EXPLORATORY]` - When you need to implement something not easily testable
- **To DEBUG**: `[TRANSITION: DEBUG]` - When you discover a bug during development
- **To REVIEW**: `[TRANSITION: REVIEW]` - When a feature is complete and needs review

## Reminder Statements

To maintain this state, periodically remind yourself:
- "I am following TDD principles: Red, Green, Refactor"
- "Tests first, implementation second"
- "What's the simplest thing that could work?"
- "Am I testing behavior, not implementation?"

Remember to clearly mark each step of the TDD cycle to maintain focus and ensure proper development flow. 