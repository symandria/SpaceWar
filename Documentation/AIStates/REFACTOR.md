# AI State: Refactoring

## Purpose
This state guides the AI in improving existing code structure, readability, and maintainability without changing external behavior. The focus is on systematic, incremental improvements backed by tests to ensure functionality remains intact.

## When to Use This State
- When code works but has poor structure, duplication, or unclear naming
- When technical debt is impacting development velocity
- After exploratory programming has yielded working code that needs cleanup
- When preparing code for extension or modification
- When improving performance of existing functionality

## The Refactoring Workflow

### 1. Identify Refactoring Targets
```
[STATE: REFACTOR] Refactoring {component} to address {issues}
[ISSUES] Detailed description of code smells or problems to address
```

- Identify specific code smells or structural problems
- Prioritize issues based on impact and risk
- Ensure sufficient test coverage exists before starting
- Document the expected improvements

### 2. Ensure Test Coverage
```
[STATE: REFACTOR] [TESTS] Assessing test coverage for {component}
```

- Verify existing tests cover the functionality to be refactored
- Add missing tests before refactoring if coverage is insufficient
- Ensure tests verify behavior, not implementation details
- Document test gaps and how they're addressed

### 3. Incremental Refactoring
```
[STATE: REFACTOR] [STEP] {specific refactoring action}
```

- Work in small, verifiable steps
- Apply standard refactoring patterns with established names
- Run tests after each step to verify behavior is preserved
- Keep commits focused on single logical changes

### 4. Verification
```
[STATE: REFACTOR] [VERIFY] Verifying behavior after refactoring
```

- Run tests to ensure functionality is preserved
- Verify performance has not degraded unacceptably
- Check for any regressions in related components
- Document any unexpected findings

### 5. Documentation Updates
```
[STATE: REFACTOR] [DOCS] Updating documentation to reflect new structure
```

- Update comments and documentation to reflect new design
- Explain architectural changes if significant
- Document performance improvements or trade-offs
- Note any API changes, even if backward compatible

## Common Refactoring Patterns

### Extract Method
```csharp
[STATE: REFACTOR] [STEP] Extracting method from complex routine

// Before
public void ProcessTurn()
{
    // 20 lines of code that handle player input
    // 15 lines that update game state
    // 10 lines that check win conditions
}

// After
public void ProcessTurn()
{
    HandlePlayerInput();
    UpdateGameState();
    CheckWinConditions();
}

private void HandlePlayerInput() { /* 20 lines of code */ }
private void UpdateGameState() { /* 15 lines of code */ }
private void CheckWinConditions() { /* 10 lines of code */ }
```

### Replace Conditional with Polymorphism
```csharp
[STATE: REFACTOR] [STEP] Replacing ship type conditionals with polymorphism

// Before
public class Ship
{
    public enum ShipType { Fighter, Cruiser, Battleship }
    
    public ShipType Type { get; set; }
    
    public void Attack(Ship target)
    {
        switch (Type)
        {
            case ShipType.Fighter:
                // Fighter attack logic
                break;
            case ShipType.Cruiser:
                // Cruiser attack logic
                break;
            case ShipType.Battleship:
                // Battleship attack logic
                break;
        }
    }
}

// After
public abstract class Ship
{
    public abstract void Attack(Ship target);
}

public class Fighter : Ship
{
    public override void Attack(Ship target)
    {
        // Fighter attack logic
    }
}

public class Cruiser : Ship
{
    public override void Attack(Ship target)
    {
        // Cruiser attack logic
    }
}

public class Battleship : Ship
{
    public override void Attack(Ship target)
    {
        // Battleship attack logic
    }
}
```

### Introduce Parameter Object
```csharp
[STATE: REFACTOR] [STEP] Introducing RenderParameters object

// Before
public void RenderSprite(
    Texture2D texture, 
    Vector2 position, 
    Vector2 scale, 
    float rotation, 
    Color color, 
    Rectangle? sourceRectangle, 
    SpriteEffects effects, 
    float layerDepth)
{
    // Rendering logic
}

// After
public class RenderParameters
{
    public Texture2D Texture { get; set; }
    public Vector2 Position { get; set; }
    public Vector2 Scale { get; set; }
    public float Rotation { get; set; }
    public Color Color { get; set; }
    public Rectangle? SourceRectangle { get; set; }
    public SpriteEffects Effects { get; set; }
    public float LayerDepth { get; set; }
    
    public static RenderParameters Default => new RenderParameters
    {
        Scale = Vector2.One,
        Color = Color.White,
        Effects = SpriteEffects.None,
        LayerDepth = 0f
    };
}

public void RenderSprite(RenderParameters parameters)
{
    // Rendering logic
}
```

### Extract Interface
```csharp
[STATE: REFACTOR] [STEP] Extracting IGameObject interface

// Before
public class GameObject
{
    public Vector2 Position { get; set; }
    public void Update(GameTime gameTime) { /* ... */ }
    public void Draw(SpriteBatch spriteBatch) { /* ... */ }
    public bool CollidesWith(GameObject other) { /* ... */ }
}

// After
public interface IGameObject
{
    Vector2 Position { get; }
    void Update(GameTime gameTime);
    void Draw(SpriteBatch spriteBatch);
    bool CollidesWith(IGameObject other);
}

public class GameObject : IGameObject
{
    public Vector2 Position { get; set; }
    public void Update(GameTime gameTime) { /* ... */ }
    public void Draw(SpriteBatch spriteBatch) { /* ... */ }
    public bool CollidesWith(IGameObject other) { /* ... */ }
}
```

### Move Method
```csharp
[STATE: REFACTOR] [STEP] Moving collision detection to dedicated class

// Before
public class Ship
{
    public Rectangle Bounds { get; set; }
    
    public bool CollidesWith(Asteroid asteroid)
    {
        return Bounds.Intersects(asteroid.Bounds);
    }
}

// After
public class CollisionDetector
{
    public static bool CheckCollision(Rectangle bounds1, Rectangle bounds2)
    {
        return bounds1.Intersects(bounds2);
    }
}

public class Ship
{
    public Rectangle Bounds { get; set; }
    
    public bool CollidesWith(Asteroid asteroid)
    {
        return CollisionDetector.CheckCollision(Bounds, asteroid.Bounds);
    }
}
```

## Best Practices

### Test First
- Never refactor without tests
- Add tests first if they don't exist
- Prefer characterization tests for legacy code

### Small Steps
- Make small, incremental changes
- Commit after each successful refactoring
- Run tests frequently

### Code Quality
- Follow SOLID principles
- Ensure meaningful naming
- Reduce duplication
- Simplify complex conditionals
- Keep methods short and focused

### Documentation
- Document significant structural changes
- Update comments to reflect new design
- Explain non-obvious refactoring decisions

## Common Pitfalls to Avoid

- **Changing Behavior**: Refactoring should preserve external behavior
- **Big Bang Refactoring**: Avoid large, sweeping changes
- **Inadequate Testing**: Ensure sufficient test coverage before starting
- **Premature Abstraction**: Don't create abstractions until they're needed
- **Over-Engineering**: Keep solutions as simple as possible
- **Mixing Refactoring and Features**: Don't add new features during refactoring

## Transitioning to Other States

When appropriate, transition to:

- **To TDD**: `[TRANSITION: TDD]` - When refactoring reveals need for new functionality
- **To DEBUG**: `[TRANSITION: DEBUG]` - When refactoring exposes hidden bugs
- **To REVIEW**: `[TRANSITION: REVIEW]` - When refactoring is complete and needs review

## Reminder Statements

To maintain this state, periodically remind yourself:
- "I am refactoring {component} without changing its behavior"
- "Small, verified steps with tests run after each change"
- "Improve structure, names, and simplicity"
- "Tests must pass after every refactoring step"
- "Commit frequently with clear messages"

Remember to clearly document each refactoring step and verify behavior is preserved to maintain a safe, incremental improvement process. 