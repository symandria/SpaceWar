# AI State: Code Review

## Purpose
This state guides the AI in systematically evaluating code for quality, correctness, maintainability, and adherence to best practices. The focus is on providing constructive feedback that improves code quality and identifies potential issues before they cause problems.

## When to Use This State
- When a feature or component is complete and ready for review
- When preparing code for integration into the main codebase
- When evaluating code quality as part of maintenance
- When onboarding to understand an existing codebase
- When mentoring or providing feedback to other developers

## The Code Review Workflow

### 1. Understand Intent and Context
```
[STATE: REVIEW] Reviewing {component}
[INTENT] Description of what the code is supposed to accomplish
```

- Establish what the code is intended to do
- Identify the requirements or user stories it addresses
- Understand its place in the larger system
- Note any constraints or special requirements

### 2. Functional Correctness
```
[STATE: REVIEW] [FUNCTION] Assessing functional correctness
```

- Verify the code does what it's supposed to do
- Check for edge cases and error handling
- Identify missing functionality
- Note any potential bugs or incorrect assumptions

### 3. Code Quality Assessment
```
[STATE: REVIEW] [QUALITY] Evaluating code quality
```

- Assess adherence to SOLID principles
- Check for appropriate patterns and practices
- Evaluate naming, structure, and organization
- Identify code smells or anti-patterns
- Review comments and documentation

### 4. Performance Review
```
[STATE: REVIEW] [PERF] Analyzing performance considerations
```

- Identify potential performance bottlenecks
- Check resource usage and disposal
- Evaluate algorithm efficiency
- Note any concerns about scalability
- Review concurrent or async code for correctness

### 5. Security Assessment
```
[STATE: REVIEW] [SECURITY] Checking for security issues
```

- Look for input validation issues
- Check for proper error handling that doesn't expose details
- Identify potential security vulnerabilities
- Review authentication and authorization
- Check for secure data handling

### 6. Testing Adequacy
```
[STATE: REVIEW] [TESTS] Evaluating test coverage and quality
```

- Verify appropriate test coverage
- Check test quality and relevance
- Identify missing test cases, especially edge cases
- Ensure tests are testing behavior, not implementation
- Review test naming and organization

### 7. Summary and Recommendations
```
[STATE: REVIEW] [SUMMARY] Overall assessment and recommendations
```

- Provide an overall assessment of the code
- Prioritize issues by importance and risk
- Offer specific, actionable recommendations
- Note positive aspects and good practices found
- Suggest learning resources if appropriate

## Review Checklist

### General
- Code follows the project's style guide
- No unnecessary commented-out code
- Complex logic is well-documented
- DRY principle is followed
- Classes and methods have single responsibilities
- No magic numbers or strings
- Error messages are clear and helpful

### MonoGame Specific
- Resources are properly disposed
- Game components follow expected lifecycle
- Content loading is efficient and error-handled
- Draw and Update methods are optimized
- Input handling is clean and maintainable
- State transitions are clear and consistent

### Object-Oriented Design
- Classes have appropriate visibility
- Inheritance is used appropriately
- Interfaces are cohesive and well-defined
- Dependencies are explicit and minimized
- Composition is preferred over inheritance when appropriate

### Game Architecture
- Game states are well-managed
- UI components are decoupled from game logic
- Input handling is separated from business logic
- Rendering concerns are separated from game state
- Configuration is external where appropriate

## Examples

### Method Review
```csharp
[STATE: REVIEW] Reviewing UpdatePlayerPosition method
[FUNCTION] Method updates player position based on input and handles collisions

public void UpdatePlayerPosition(GameTime gameTime)
{
    // Get input direction
    var direction = new Vector2(0, 0);
    if (keyboard.IsKeyDown(Keys.A)) direction.X -= 1;
    if (keyboard.IsKeyDown(Keys.D)) direction.X += 1;
    if (keyboard.IsKeyDown(Keys.W)) direction.Y -= 1;
    if (keyboard.IsKeyDown(Keys.S)) direction.Y += 1;
    
    // Normalize and apply speed
    if (direction != Vector2.Zero)
    {
        direction.Normalize();
        direction *= Speed * (float)gameTime.ElapsedGameTime.TotalSeconds;
        
        // Update position
        Position += direction;
        
        // Check map bounds
        Position = new Vector2(
            MathHelper.Clamp(Position.X, 0, mapWidth),
            MathHelper.Clamp(Position.Y, 0, mapHeight)
        );
    }
}

[ISSUES]
1. Direct dependency on keyboard input makes this method harder to test
2. Collision detection and position update are mixed in the same method
3. Magic numbers (0, mapWidth, mapHeight) without clear origin
4. Method handles too many responsibilities
5. No defensive coding for null gameTime

[RECOMMENDATIONS]
1. Extract input handling to separate method/class
2. Split collision detection into its own method
3. Make map boundaries explicit parameters or properties
4. Consider a physics/movement component pattern
5. Add null check for gameTime parameter
```

### Class Review
```csharp
[STATE: REVIEW] Reviewing EnemyManager class
[FUNCTION] Class manages spawning and tracking of enemies

public class EnemyManager
{
    private List<Enemy> enemies = new List<Enemy>();
    private float spawnTimer = 0f;
    private Random random = new Random();
    
    public void Update(GameTime gameTime)
    {
        // Update spawn timer
        spawnTimer -= (float)gameTime.ElapsedGameTime.TotalSeconds;
        
        // Spawn new enemy if timer expired
        if (spawnTimer <= 0)
        {
            SpawnEnemy();
            spawnTimer = 2f; // Reset timer
        }
        
        // Update all enemies
        foreach (var enemy in enemies.ToList())
        {
            enemy.Update(gameTime);
            
            // Remove dead enemies
            if (!enemy.IsAlive)
            {
                enemies.Remove(enemy);
            }
        }
    }
    
    private void SpawnEnemy()
    {
        var position = new Vector2(
            random.Next(0, 800),
            random.Next(0, 600)
        );
        
        enemies.Add(new Enemy(position));
    }
    
    public void Draw(SpriteBatch spriteBatch)
    {
        foreach (var enemy in enemies)
        {
            enemy.Draw(spriteBatch);
        }
    }
}

[ISSUES]
1. Hard-coded spawn rate (2f) and screen dimensions (800, 600)
2. No maximum enemy limit could lead to performance issues
3. Updating and removing from a collection simultaneously is risky
4. No way to configure different enemy types or behaviors
5. Direct dependency on Enemy class hinders extensibility

[RECOMMENDATIONS]
1. Make spawn rate and boundaries configurable
2. Add maximum enemy count property
3. Use ToList() to create a copy before iteration (already done, good!)
4. Implement enemy factory pattern for different types
5. Consider using IEnemy interface instead of concrete Enemy class
```

## Common Pitfalls to Avoid

- **Nitpicking**: Focus on substantial issues, not stylistic preferences
- **Overwhelming Feedback**: Prioritize issues rather than listing every minor concern
- **Code Rewriting**: Suggest improvements, don't rewrite the entire solution
- **Being Too Abstract**: Provide concrete examples of suggested changes
- **Missing Positive Feedback**: Always note what's done well, not just issues
- **Ignoring Context**: Consider the constraints and requirements the code operates under

## Transitioning to Other States

When appropriate, transition to:

- **To REFACTOR**: `[TRANSITION: REFACTOR]` - When review identifies refactoring opportunities
- **To DEBUG**: `[TRANSITION: DEBUG]` - When review uncovers potential bugs
- **To TDD**: `[TRANSITION: TDD]` - When review suggests missing functionality requiring tests

## Reminder Statements

To maintain this state, periodically remind yourself:
- "I am reviewing {component} against established best practices"
- "Be constructive, specific, and actionable in feedback"
- "Consider both detailed implementation and broader architecture"
- "Balance criticism with recognition of good practices"
- "Focus on knowledge transfer, not just finding issues"

Remember to clearly document review findings in a way that helps improve both the code and the developer's understanding of best practices. 