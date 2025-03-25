# SpaceWar Architecture Documentation

## Project Overview
SpaceWar is a turn-based space combat game with real-time battle animations. This document outlines the architecture for the C# version of the game, which is being developed as a more maintainable and extensible version of the original Python implementation.

## Game States and Flow

### 1. Menu State
The menu state handles game configuration and mode selection.

#### Components:
- **MenuManager**
  - Handles menu navigation
  - Manages menu state transitions
  - Processes menu input
  - Coordinates menu UI updates

- **ConfigurationManager**
  - Stores game configuration
  - Validates configuration settings
  - Manages default configurations
  - Handles configuration persistence

#### State Flow:
```
[Menu Navigation] → [Configuration Selection] → [Start Game]
```

### 2. Active Game State
The active game state manages the core gameplay loop.

#### Components:
- **GameBoard**
  - Manages game board layout
  - Handles board state
  - Processes board interactions
  - Coordinates with simulation

- **SimulationManager**
  - Controls simulation state
  - Processes game actions
  - Manages object interactions
  - Handles collision detection

- **TurnManager**
  - Manages turn sequence
  - Handles player/AI turns
  - Coordinates action resolution
  - Tracks game progress

#### State Flow:
```
[Turn Start] → [Player Input] → [Action Validation] → [Simulation] → [Turn End]
```

### 3. Summary State
The summary state displays game results and statistics.

#### Components:
- **ResultsManager**
  - Processes game results
  - Generates statistics
  - Manages result persistence
  - Coordinates summary display

- **SummaryUI**
  - Displays game statistics
  - Shows performance metrics
  - Handles summary navigation
  - Manages transition options

#### State Flow:
```
[Results Processing] → [Statistics Generation] → [Summary Display] → [Menu Return]
```

## Core Architecture

### 1. View System (UI Layer)
The view system leverages MonoGame's built-in component system and MonoGame.Extended for efficient rendering and input handling.

#### Components:
- **Game Components**
  - Built on MonoGame's DrawableGameComponent
  - Handles rendering and updates
  - Manages object state and animations
  - Processes input through MonoGame's input system

- **Scene Management**
  - Uses MonoGame.Extended scene graph
  - Handles layer management
  - Manages object hierarchy
  - Coordinates component updates

- **UI Components**
  - Built-in MonoGame.Extended UI system
  - Menu management
  - Button handling
  - Text rendering

#### Implementation Details:
- Built on MonoGame for efficient 2D rendering
- Uses MonoGame.Extended for scene management
- Leverages built-in component system
- Handles high-frequency updates (60+ FPS)
- Uses MonoGame's input system for user interaction

### 2. Game Logic (Core Engine)
The game logic layer contains all game rules and mechanics, completely isolated from the view system.

#### Components:
- **GameState**
  - Current game state container
  - State validation
  - State transitions
  - Event system for state changes

- **BattleSystem**
  - Combat resolution
  - Damage calculation
  - Special abilities
  - Turn management

- **MovementSystem**
  - Ship movement
  - Collision detection
  - Path validation
  - Animation coordination

#### Implementation Details:
- Fully testable in isolation
- Pure logic with no UI dependencies
- Event-driven architecture for state changes
- Command pattern for actions

### 3. State Management
The state management system uses MonoGame's event system to coordinate between game logic and view components.

#### Components:
- **Event System**
  - Game state change events
  - Input events
  - Animation events
  - UI state events

- **Animation System**
  - Built on MonoGame's timing system
  - Smooth movement interpolation
  - Particle effects
  - Visual effects

- **State Synchronization**
  - Event-based updates
  - State validation
  - Change tracking
  - Update coordination

#### Implementation Details:
- Uses MonoGame's event system
- Leverages built-in timing system
- Efficient state updates
- Clean component communication

## Data Flow
```
[Game Logic] → [State Events] → [Game Components] → [Rendering]
                     ↑                              ↓
                [Game State]                  [User Input] 
```

## Testing Strategy
1. **Unit Tests**
   - Game logic components
   - State management
   - Command processing

2. **Integration Tests**
   - State transitions
   - Command execution
   - Component updates

3. **Component Tests**
   - MonoGame component behavior
   - Input handling
   - Animation system

4. **End-to-End Tests**
   - Critical user paths
   - Game scenarios
   - Performance benchmarks

## Development Phases
1. **Phase 1: Core Infrastructure**
   - MonoGame project setup
   - Component system implementation
   - Basic scene management

2. **Phase 2: Game Logic**
   - Core game rules
   - Battle system
   - Movement system

3. **Phase 3: UI Implementation**
   - Menu system
   - Battle view
   - Summary view

4. **Phase 4: Polish**
   - Animations
   - Effects
   - Performance optimization

## Future Extensibility
- New components can be added easily
- Additional game mechanics can be implemented in isolation
- Animation system can be enhanced independently
- Multiple UI frameworks could be supported
- Network play could be added by extending state management 

## Menu System Architecture

### Menu Flow
```
[Splash Screen] → [Main Menu] → [Character Creation Menu] → [Player Menu] → [Battle Setup Menu/Customize Ship Menu]
```

### 1. Splash Screen
#### Components:
- **Background**
  - Animated or static background
  - Game title display
- **Play Button**
  - Hover animation
  - Click transition to Main Menu
  - Visual feedback system

### 2. Main Menu
#### Components:
- **Background**
  - Animated or static background
  - Game title display above buttons
- **Button Container**
  - Dynamic button layout system
  - Consistent spacing and alignment
- **Menu Buttons**
  - Continue (conditional on save existence)
  - New Game
  - Load Game (conditional on multiple saves)
  - Quit Game
- **State Management**
  - Save file detection
  - Button visibility control
  - Transition management

### 3. Character Creation Menu
#### Components:
- **Ship Display Area**
  - Top half of screen
  - Race-specific ship visualization
  - Ship name input field with "U.S.S." prefix
- **Captain Section**
  - Bottom half of screen
  - Captain name input field
  - "Captained by" label
- **Race Selection**
  - Race-specific background
  - Race selection buttons
  - Race indicator (top left)
- **Control Buttons**
  - Cancel (bottom left)
  - Race options (bottom middle)
  - Confirm (bottom right)
- **State Management**
  - Race-specific asset loading
  - Input validation
  - Save file creation

### 4. Player Menu
#### Components:
- **Ship Information Display**
  - Ship visualization
  - Captain details
  - Ship statistics
- **Action Buttons**
  - Battle
  - Customize Ship
  - Main Menu
- **State Management**
  - Ship data loading
  - Statistics tracking
  - Save state management

### 5. Customize Ship Menu (Stub)
#### Components:
- **Header**
  - "Customize Ship" title
- **Control Buttons**
  - Cancel (bottom left)
  - Confirm (bottom right)
- **State Management**
  - Save state handling
  - Transition management

### 6. Battle Setup Menu (Stub)
#### Components:
- **Header**
  - "Battle" title
- **Control Buttons**
  - Cancel (bottom left)
  - Engage! (bottom right)
- **State Management**
  - Battle initialization
  - Transition to Active Game State

### Menu Component System
```csharp
public interface IMenuComponent
{
    void Update(GameTime gameTime);
    void Draw(SpriteBatch spriteBatch);
    bool HandleInput(InputState input);
}

public class MenuButton : IMenuComponent
{
    private readonly Texture2D normalTexture;
    private readonly Texture2D hoverTexture;
    private readonly Action onClick;
    private bool isHovered;

    public void Update(GameTime gameTime)
    {
        // Handle hover state and animations
    }

    public bool HandleInput(InputState input)
    {
        // Handle click events
        return false;
    }
}

public class ButtonContainer : IMenuComponent
{
    private readonly List<MenuButton> buttons;
    private readonly float spacing;

    public void AddButton(MenuButton button)
    {
        buttons.Add(button);
        RecalculateLayout();
    }

    private void RecalculateLayout()
    {
        // Position buttons based on container rules
    }
}
```

### Menu State Management
```csharp
public class MenuStateManager
{
    private readonly Dictionary<string, bool> saveStates;
    private readonly Dictionary<Race, ShipAssets> raceAssets;

    public void LoadSaveStates()
    {
        // Detect and load save files
    }

    public bool ShouldShowContinue()
    {
        return saveStates.Any();
    }

    public bool ShouldShowLoadGame()
    {
        return saveStates.Count > 1;
    }
}
```

### Menu Transition System
```csharp
public class MenuTransitionManager
{
    private readonly Dictionary<Type, IMenuScene> menuScenes;
    private IMenuScene currentScene;

    public void TransitionTo<T>() where T : IMenuScene
    {
        if (menuScenes.TryGetValue(typeof(T), out var nextScene))
        {
            currentScene?.OnExit();
            currentScene = nextScene;
            currentScene.OnEnter();
        }
    }
}
``` 