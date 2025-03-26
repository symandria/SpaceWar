# AI State: Debugging

## Purpose
This state guides the AI in systematically identifying, fixing, and preventing recurrence of bugs through regression tests. The focus is on root cause analysis, minimal effective fixes, and creating tests that will catch similar issues in the future.

## When to Use This State
- When unexpected behavior is reported or observed
- When tests are failing
- When integrating components reveals compatibility issues
- When performance problems or resource leaks are discovered
- When visual artifacts or rendering issues occur

## The Debugging Workflow

### 1. Problem Definition
```
[STATE: DEBUG] Debugging {issue description}
[PROBLEM] Detailed description of the observed issue
```

- Clearly articulate what's wrong and how it differs from expected behavior
- Identify the context and conditions where the issue occurs
- Document any error messages, stack traces, or logs
- Establish severity and impact

### 2. Reproduction
```
[STATE: DEBUG] [REPRO] Steps to reproduce the issue
```

- Create a reliable set of steps to reproduce the issue
- Note the frequency of reproduction (always, sometimes, rarely)
- Identify the minimal test case that demonstrates the issue
- Document environment factors (resolution, input devices, etc.)

### 3. Root Cause Analysis
```
[STATE: DEBUG] [ANALYSIS] Investigation of root cause
```

- Trace through code execution to identify where behavior diverges
- Examine state changes and data flow
- Review similar components for patterns
- Form a hypothesis about the cause
- Validate hypothesis through targeted tests or instrumentation

### 4. Fix Implementation
```
[STATE: DEBUG] [FIX] Implementation of solution
```

- Implement the minimal change needed to address the root cause
- Maintain clean code principles even in fixes
- Document why the fix works
- Note any trade-offs or potential side effects

### 5. Verification
```
[STATE: DEBUG] [VERIFY] Verification that the fix resolves the issue
```

- Verify fix using the established reproduction steps
- Check for regressions in related functionality
- Verify fix in various conditions if applicable
- Note any unexpected behavior, even if not directly related

### 6. Regression Test Creation
```
[STATE: DEBUG] [REGRESSION-TEST] Test to prevent this bug from recurring
```

- Create a test that would have caught this bug
- Ensure the test fails before the fix and passes after
- Focus on testing the behavior, not the implementation
- Include edge cases related to the bug
- Document what the test is checking and why

## Testing Strategies for Different Bug Types

### Functional Bugs
```csharp
[STATE: DEBUG] [REGRESSION-TEST] Test for incorrect collision detection
[TEST]
[Fact]
public void WhenObjectsOverlap_CollisionIsDetected()
{
    // Arrange
    var object1 = new GameObject(position: new Vector2(0, 0), size: new Vector2(10, 10));
    var object2 = new GameObject(position: new Vector2(5, 5), size: new Vector2(10, 10));
    
    // Act
    bool collisionDetected = CollisionDetector.CheckCollision(object1, object2);
    
    // Assert
    Assert.True(collisionDetected, "Collision should be detected when objects overlap");
}
```

### State Management Bugs
```csharp
[STATE: DEBUG] [REGRESSION-TEST] Test for improper state transition
[TEST]
[Fact]
public void WhenPauseButtonPressed_GameEntersPausedState()
{
    // Arrange
    var game = new GameState { CurrentState = GameState.Playing };
    var inputHandler = new InputHandler(game);
    var mockInput = new MockInput { IsPauseButtonPressed = true };
    
    // Act
    inputHandler.ProcessInput(mockInput);
    
    // Assert
    Assert.Equal(GameState.Paused, game.CurrentState);
}
```

### Resource Management Bugs
```csharp
[STATE: DEBUG] [REGRESSION-TEST] Test for texture disposal
[TEST]
[Fact]
public void WhenComponentIsDisposed_TexturesAreDisposed()
{
    // Arrange
    var mockTexture = new MockTexture();
    var component = new GameComponent(mockTexture);
    
    // Act
    component.Dispose();
    
    // Assert
    Assert.True(mockTexture.WasDisposed, "Texture should be disposed when component is disposed");
}
```

### Timing and Animation Bugs
```csharp
[STATE: DEBUG] [REGRESSION-TEST] Test for animation timing
[TEST]
[Fact]
public void WhenAnimationPlays_FramesAdvanceAtCorrectRate()
{
    // Arrange
    var animation = new Animation(frameDuration: 0.1f, frameCount: 5);
    var gameTime = new MockGameTime();
    
    // Act
    animation.Update(gameTime.AdvanceBy(0.05f)); // Half-frame duration
    
    // Assert
    Assert.Equal(0, animation.CurrentFrame); // Should still be on first frame
    
    // Act again
    animation.Update(gameTime.AdvanceBy(0.05f)); // Another half-frame
    
    // Assert
    Assert.Equal(1, animation.CurrentFrame); // Should advance to second frame
}
```

## Debugging Specific MonoGame Issues

### Content Loading
```csharp
[STATE: DEBUG] [ANALYSIS] Content loading failure
// Check the Content project file
// Verify file paths and asset references
// Ensure content processor is appropriate for the file type
// Check for missing files or dependencies
```

### Rendering
```csharp
[STATE: DEBUG] [ANALYSIS] Sprite rendering issue
// Check SpriteBatch usage (Begin/End pairs)
// Verify texture is not null
// Check sprite position, origin, and scale
// Review blend modes and sampler states
// Verify cameras and view transformations
```

### Input
```csharp
[STATE: DEBUG] [ANALYSIS] Input handling issue
// Check input state update sequence
// Verify input mapping and bindings
// Check for competing input handlers
// Verify input is processed in the right game state
```

## Common Pitfalls to Avoid

- **Symptom Fixing**: Fixing the symptom rather than the root cause
- **Hasty Fixes**: Implementing fixes without thorough understanding
- **Missing Regression Tests**: Failing to create tests that prevent recurrence
- **Over-Engineering**: Making the fix more complex than necessary
- **Incomplete Verification**: Not testing the fix thoroughly enough
- **Unrelated Changes**: Modifying unrelated code during the fix

## Transitioning to Other States

When appropriate, transition to:

- **To REFACTOR**: `[TRANSITION: REFACTOR]` - When the fix identifies a need for broader refactoring
- **To TDD**: `[TRANSITION: TDD]` - When new features need to be added as part of the solution
- **To REVIEW**: `[TRANSITION: REVIEW]` - When the fix is complete and needs review

## Reminder Statements

To maintain this state, periodically remind yourself:
- "I am debugging {specific issue} with systematic root cause analysis"
- "Each bug must have a corresponding regression test"
- "Fix the root cause, not just the symptoms"
- "Verify the fix thoroughly to prevent regressions"
- "Simple, focused fixes are better than complex ones"

Remember to clearly document the bug, reproduction steps, root cause, and fix rationale to facilitate knowledge sharing and prevent similar issues in the future. 