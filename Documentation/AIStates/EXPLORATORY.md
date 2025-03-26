# AI State: Exploratory Programming

## Purpose
This state guides the AI in developing components that are difficult to test upfront through traditional TDD, such as visual elements, integrations with external systems, or complex interactive features.

## When to Use This State
- When implementing visual or UI components
- When working with MonoGame's rendering pipeline
- When prototyping features with unclear requirements
- When integrating with external systems
- When performance or real-time operations are critical

## The Exploratory Workflow

### 1. Define Scope and Specification
```
[STATE: EXPLORATORY] Developing {component}
[SPEC] Clear description of what we're building and how we'll verify it works
```

- Define clear boundaries of what you're exploring
- Establish acceptance criteria for success
- Identify manual verification methods
- Break down into small, manageable increments

### 2. Incremental Development
```
[STATE: EXPLORATORY] [INCREMENT #1] Implementing {specific aspect}
```

- Work in small, verifiable increments
- Focus on one aspect at a time
- Maintain clean, readable code even in exploration
- Document design decisions and rationale

### 3. Verification Points
```
[STATE: EXPLORATORY] [VERIFY] Verification steps for current increment
```

- Define clear manual verification procedures
- Document expected behavior
- Note any observed deviations
- Consider how this might be tested in the future

### 4. Reflection and Documentation
```
[STATE: EXPLORATORY] [REFLECT] Lessons learned from this increment
```

- Document what worked and what didn't
- Note any surprising behaviors or edge cases
- Identify patterns that could be abstracted
- Consider how to make similar components more testable

## Best Practices

### Code Quality
- Maintain high code quality standards despite exploratory nature
- Use meaningful names and consistent patterns
- Keep methods small and focused
- Document assumptions and design decisions

### Risk Mitigation
- Isolate exploratory code from critical systems when possible
- Create clean interfaces to exploratory components
- Add logging and telemetry for runtime verification
- Consider feature flags to easily disable problematic code

### Moving Toward Testability
- Identify core logic that could be extracted and tested
- Separate rendering/presentation from business logic
- Create abstractions for external dependencies
- Document test gaps for future coverage

## Examples

### Exploratory UI Component
```csharp
[STATE: EXPLORATORY] Developing animated button component
[SPEC] Button that pulses when hovered and shows particle effect when clicked
[INCREMENT #1] Basic button rendering with hover detection

public class AnimatedButton
{
    private Texture2D _texture;
    private Rectangle _bounds;
    private bool _isHovered;
    
    public AnimatedButton(Texture2D texture, Rectangle bounds)
    {
        _texture = texture;
        _bounds = bounds;
    }
    
    public void Update(MouseState mouseState)
    {
        var mousePoint = new Point(mouseState.X, mouseState.Y);
        _isHovered = _bounds.Contains(mousePoint);
    }
    
    public void Draw(SpriteBatch spriteBatch)
    {
        var color = _isHovered ? Color.White : Color.Gray;
        spriteBatch.Draw(_texture, _bounds, color);
    }
}

[VERIFY] 
1. Run the game
2. Move mouse over button, confirm it changes from gray to white
3. Move mouse away, confirm it changes back to gray
```

### Visual Effect
```csharp
[STATE: EXPLORATORY] Developing explosion particle effect
[SPEC] Particle effect that expands from center with particles that fade out
[INCREMENT #1] Basic particle emission system

public class ExplosionEffect
{
    private List<Particle> _particles = new List<Particle>();
    private Vector2 _position;
    private Random _random = new Random();
    
    public ExplosionEffect(Vector2 position)
    {
        _position = position;
        // Create 50 particles in random directions
        for (int i = 0; i < 50; i++)
        {
            var direction = new Vector2(
                (float)(_random.NextDouble() * 2 - 1),
                (float)(_random.NextDouble() * 2 - 1)
            );
            direction.Normalize();
            var speed = (float)(_random.NextDouble() * 100 + 50);
            var lifetime = (float)(_random.NextDouble() * 0.5 + 0.5);
            
            _particles.Add(new Particle(_position, direction, speed, lifetime));
        }
    }
    
    public bool Update(GameTime gameTime)
    {
        float deltaTime = (float)gameTime.ElapsedGameTime.TotalSeconds;
        foreach (var particle in _particles)
        {
            particle.Update(deltaTime);
        }
        
        // Remove dead particles
        _particles.RemoveAll(p => p.IsDead);
        
        // Return false when all particles are dead
        return _particles.Count > 0;
    }
    
    public void Draw(SpriteBatch spriteBatch)
    {
        foreach (var particle in _particles)
        {
            particle.Draw(spriteBatch);
        }
    }
}

[VERIFY]
1. Create explosion at mouse click position
2. Verify particles spread outward from center
3. Verify particles fade out over time
4. Verify effect cleans up after all particles are dead
```

## Common Pitfalls to Avoid

- **Scope Creep**: Keep exploration focused on specific components
- **Unverified Assumptions**: Always verify behavior through manual testing
- **Poor Documentation**: Document decisions, especially unusual ones
- **Neglecting Structure**: Maintain good architecture even in exploration
- **Insufficient Manual Testing**: Test thoroughly in various conditions
- **Skipping Post-Mortem**: Always reflect on what was learned

## Transitioning to Other States

When appropriate, transition to:

- **To TDD**: `[TRANSITION: TDD]` - When you've explored enough to clearly define testable behavior
- **To REFACTOR**: `[TRANSITION: REFACTOR]` - When the exploratory code works but needs cleanup
- **To DEBUG**: `[TRANSITION: DEBUG]` - When you discover unexpected behavior
- **To REVIEW**: `[TRANSITION: REVIEW]` - When exploration is complete and needs review

## Reminder Statements

To maintain this state, periodically remind yourself:
- "I am exploring {specific aspect} with clear verification steps"
- "Small, verifiable increments with clear documentation"
- "Separate what can be tested from what must be manually verified"
- "Document design decisions and verification procedures"

Remember to clearly mark each exploratory increment and verification step to maintain focus and ensure proper development flow. 