# AI State: Test-Driven Development (TDD)

## Purpose
This state guides the AI to develop features using Test-Driven Development, ensuring all code is tested, functional, and maintainable from the start.

## When to Use This State
- When implementing new features or components
- When fixing bugs that can be replicated with a test
- When extending existing functionality with clear requirements

## State Maintenance Protocol
To maintain this TDD state throughout the session, you MUST:

1. **Always begin with a failing test** before writing any implementation code
2. **Mark each phase explicitly** using the state markers below
3. **Complete each phase fully** before moving to the next
4. **Remind yourself of the current phase** at least once per phase

### Required State Markers
```
[STATE: TDD-RED] Writing failing test for {feature/functionality}
[STATE: TDD-GREEN] Implementing minimal code to pass test
[STATE: TDD-REFACTOR] Improving code while maintaining test success
```

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

## Common Pitfalls to Avoid

- **Writing Tests After Implementation**: Defeats the purpose of TDD
- **Testing Too Much at Once**: Keep tests focused on single behaviors
- **Over-Engineering**: Implement only what's needed by current tests
- **Skipping Refactoring**: Quality matters; clean up your code
- **Breaking Test Isolation**: Tests should not depend on each other
- **Testing Implementation Details**: Focus on behavior, not how it's implemented

## Creating Non-Fragile Code with TDD

- **Interface-Based Design**: Code to interfaces rather than concrete implementations
- **Dependency Injection**: Pass dependencies rather than creating them internally
- **Composition Over Inheritance**: Prefer composition for more flexible designs
- **Single Responsibility**: Each class should have one reason to change
- **Small, Focused Classes**: Smaller classes are easier to test and maintain
- **Testable Constraints**: Don't rely on static methods, global state, or time-dependent code

## Transitioning to Other States

When you encounter an issue that needs a different approach:

- **To EXPLORATORY**: `[TRANSITION: EXPLORATORY]` - When you need to implement something not easily testable
- **To DEBUG**: `[TRANSITION: DEBUG]` - When you discover a bug during development
- **To REVIEW**: `[TRANSITION: REVIEW]` - When a feature is complete and needs review

## Required Discipline Practices

1. **After every test definition**: Explicitly mark with `[STATE: TDD-RED]` and verify the test fails
2. **After implementing passing code**: Explicitly mark with `[STATE: TDD-GREEN]` and verify tests pass
3. **When refactoring**: Explicitly mark with `[STATE: TDD-REFACTOR]` and verify tests still pass
4. **Every 15 minutes or after completing a cycle**: Remind yourself "I am following TDD principles: Red, Green, Refactor"
5. **If interrupted**: Re-read this section to realign with TDD state 