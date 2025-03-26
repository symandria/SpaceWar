# AI State: Architecture Planning

## Purpose
This state guides the AI in designing high-level system architecture before implementation begins. The focus is on establishing a clear, maintainable structure that meets requirements while facilitating future extension and change.

## When to Use This State
- At the beginning of a new project or major feature
- When planning significant refactoring of existing systems
- When facing design decisions with long-term implications
- When integration with external systems requires coordination
- When performance, scalability, or security concerns require architectural consideration

## The Architecture Planning Workflow

### 1. Gather and Clarify Requirements
```
[STATE: ARCHITECTURE] Planning architecture for {system/feature}
[REQUIREMENTS] Detailed description of functional and non-functional requirements
```

- Identify core functional requirements
- Define non-functional requirements (performance, security, etc.)
- Clarify constraints and limitations
- Identify stakeholders and their needs
- Document assumptions and questions

### 2. Identify System Components
```
[STATE: ARCHITECTURE] [COMPONENTS] Core components and their responsibilities
```

- Break down the system into logical components
- Define clear responsibilities for each component
- Identify data ownership and state management
- Consider separation of concerns
- Ensure components have high cohesion

### 3. Define Component Interfaces
```
[STATE: ARCHITECTURE] [INTERFACES] How components will interact
```

- Design clean interfaces between components
- Define data contracts and communication patterns
- Minimize dependencies between components
- Establish clear boundaries
- Consider abstraction levels and dependency direction

### 4. Evaluate Architecture
```
[STATE: ARCHITECTURE] [EVALUATION] Assessing the design against quality attributes
```

- Evaluate against quality attributes (performance, maintainability, etc.)
- Identify potential bottlenecks or failure points
- Consider alternative approaches for critical aspects
- Assess technical risk and mitigation strategies
- Validate architecture against requirements

### 5. Document Architecture
```
[STATE: ARCHITECTURE] [DOCS] Documentation of architectural decisions
```

- Create visual representations (diagrams, charts)
- Document key design decisions and their rationale
- Detail component interactions and data flow
- Specify technology choices and justification
- Create implementation roadmap or phasing plan

## MonoGame-Specific Architectural Considerations

### Game Loop and State Management
- How game states will be managed and transitioned
- How the main game loop handles updates and rendering
- Whether to use a component-based or object-oriented approach
- How time is managed and distributed to systems

### UI Architecture
- How UI elements are structured and composed
- How input is captured and processed
- How UI state is managed
- How UI connects to game logic

### Content Management
- How assets are loaded, cached, and unloaded
- How content is organized and referenced
- How to handle asset variants and platforms
- Content pipeline customization needs

### Entity Management
- Entity component system vs. traditional OOP
- How entities are created, updated, and destroyed
- How systems interact with entities
- How to handle entity communication

## Architecture Patterns for Games

### Component Pattern
```csharp
[STATE: ARCHITECTURE] [COMPONENTS] Component-based game object system

// Base component class
public abstract class Component
{
    public GameObject Owner { get; internal set; }
    
    public virtual void Initialize() {}
    public virtual void Update(GameTime gameTime) {}
    public virtual void Draw(SpriteBatch spriteBatch) {}
}

// Game object that hosts components
public class GameObject
{
    private List<Component> components = new List<Component>();
    
    public T AddComponent<T>() where T : Component, new()
    {
        var component = new T { Owner = this };
        components.Add(component);
        component.Initialize();
        return component;
    }
    
    public T GetComponent<T>() where T : Component
    {
        return components.OfType<T>().FirstOrDefault();
    }
    
    public void Update(GameTime gameTime)
    {
        foreach (var component in components)
        {
            component.Update(gameTime);
        }
    }
    
    public void Draw(SpriteBatch spriteBatch)
    {
        foreach (var component in components)
        {
            component.Draw(spriteBatch);
        }
    }
}

// Example usage
public class Player : GameObject
{
    public Player()
    {
        AddComponent<MovementComponent>();
        AddComponent<SpriteComponent>();
        AddComponent<CollisionComponent>();
    }
}
```

### State Pattern
```csharp
[STATE: ARCHITECTURE] [COMPONENTS] Game state management pattern

// State interface
public interface IGameState
{
    void Initialize();
    void LoadContent();
    void Update(GameTime gameTime);
    void Draw(GameTime gameTime);
    void UnloadContent();
}

// State manager
public class GameStateManager
{
    private Dictionary<Type, IGameState> states = new Dictionary<Type, IGameState>();
    private IGameState currentState;
    
    public void AddState<T>(T state) where T : IGameState
    {
        states[typeof(T)] = state;
    }
    
    public void ChangeState<T>() where T : IGameState
    {
        currentState?.UnloadContent();
        currentState = states[typeof(T)];
        currentState.Initialize();
        currentState.LoadContent();
    }
    
    public void Update(GameTime gameTime)
    {
        currentState?.Update(gameTime);
    }
    
    public void Draw(GameTime gameTime)
    {
        currentState?.Draw(gameTime);
    }
}
```

### Service Locator Pattern
```csharp
[STATE: ARCHITECTURE] [COMPONENTS] Service locator for game services

// Service locator
public static class ServiceLocator
{
    private static readonly Dictionary<Type, object> services = new Dictionary<Type, object>();
    
    public static void RegisterService<T>(T service)
    {
        services[typeof(T)] = service;
    }
    
    public static T GetService<T>()
    {
        if (services.TryGetValue(typeof(T), out var service))
        {
            return (T)service;
        }
        
        throw new InvalidOperationException($"Service of type {typeof(T)} is not registered");
    }
}

// Example usage
public interface IAudioService
{
    void PlaySound(string soundName);
}

// Register service
ServiceLocator.RegisterService<IAudioService>(new AudioService());

// Use service anywhere
ServiceLocator.GetService<IAudioService>().PlaySound("explosion");
```

## Common Pitfalls to Avoid

- **Over-Engineering**: Don't create complex architectures for simple problems
- **Premature Optimization**: Focus on clarity first, optimize specific bottlenecks later
- **Analysis Paralysis**: Don't get stuck in endless planning, use iterative approaches
- **Ignoring Constraints**: Consider the practical constraints of your platform and team
- **Rigidity**: Design for change, especially in game development
- **Not Considering Testing**: Ensure architecture facilitates testing
- **Not Documenting Rationale**: Document why decisions were made, not just what was decided

## Transitioning to Other States

When appropriate, transition to:

- **To TDD**: `[TRANSITION: TDD]` - When architecture is defined and ready for implementation
- **To EXPLORATORY**: `[TRANSITION: EXPLORATORY]` - When aspects need proof-of-concept exploration
- **To REVIEW**: `[TRANSITION: REVIEW]` - When architecture is ready for peer review

## Reminder Statements

To maintain this state, periodically remind yourself:
- "I am designing the architecture for {system} with a focus on maintainability and clarity"
- "Components should have high cohesion and loose coupling"
- "Design for change and extension, not just immediate requirements"
- "Balance between simplicity and flexibility"
- "Document decisions and their rationale"

Remember to clearly document architectural decisions and create diagrams that help visualize the system structure to facilitate understanding and implementation. 