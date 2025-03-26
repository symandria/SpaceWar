# AI State: Architecture Planning

## Purpose
This state guides the AI in designing high-level system structures, component relationships, and technical foundations. The focus is on creating robust, maintainable, and extensible systems that satisfy both immediate requirements and allow for future growth.

## When to Use This State
- When starting a new project or major feature
- When addressing significant structural problems
- When integrating multiple subsystems
- When designing for scalability or extensibility
- When establishing technical standards and patterns

## State Maintenance Protocol
To maintain this ARCHITECTURE state throughout the session, you MUST:

1. **Focus on high-level design** rather than implementation details
2. **Mark each architecture phase** using the state markers below
3. **Document decisions and their rationales** explicitly
4. **Consider multiple alternatives** before committing to a design
5. **Maintain discipline** by explicitly stating your current focus

### Required State Markers
```
[STATE: ARCHITECTURE] Designing {system/component}
[STATE: ARCHITECTURE] [REQUIREMENTS] System requirements and constraints
[STATE: ARCHITECTURE] [PRINCIPLES] Guiding architectural principles
[STATE: ARCHITECTURE] [ALTERNATIVES] Alternative approaches considered
[STATE: ARCHITECTURE] [DECISION] Architecture decision with rationale
[STATE: ARCHITECTURE] [COMPONENTS] Component breakdown and responsibilities
[STATE: ARCHITECTURE] [INTERFACES] Key interfaces and contracts
[STATE: ARCHITECTURE] [RISKS] Architectural risks and mitigations
[STATE: ARCHITECTURE] [DIAGRAM] Architecture diagram (textual representation)
```

## The Architecture Workflow

### 1. Define Requirements and Constraints
```
[STATE: ARCHITECTURE] Designing {system/component}
[STATE: ARCHITECTURE] [REQUIREMENTS] System requirements and constraints
```

- Identify functional requirements
- Define quality attributes (performance, scalability, etc.)
- Document technical constraints
- Clarify business constraints (time, resources, skills)
- Prioritize requirements and identify trade-offs

### 2. Establish Architectural Principles
```
[STATE: ARCHITECTURE] [PRINCIPLES] Guiding architectural principles
```

- Define key principles guiding the design
- Identify patterns and approaches to be used
- Establish terminology and conceptual model
- Document assumptions about the system context
- Set boundaries and scope for the architecture

### 3. Explore Alternative Approaches
```
[STATE: ARCHITECTURE] [ALTERNATIVES] Alternative approaches considered
```

- Consider multiple architectural approaches
- Evaluate each against requirements and principles
- Document pros and cons of each approach
- Consider trade-offs between alternatives
- Assess technical feasibility of each approach

### 4. Make and Document Decisions
```
[STATE: ARCHITECTURE] [DECISION] Architecture decision with rationale
```

- Document each significant decision
- Explain rationale, connecting to requirements
- Address rejected alternatives and why
- Note implications and dependencies of decisions
- Identify constraints imposed by the decision

### 5. Define Component Structure
```
[STATE: ARCHITECTURE] [COMPONENTS] Component breakdown and responsibilities
```

- Break down the system into key components
- Define clear responsibilities for each component
- Establish component ownership and boundaries
- Document component interactions and dependencies
- Ensure separation of concerns across components

### 6. Design Key Interfaces
```
[STATE: ARCHITECTURE] [INTERFACES] Key interfaces and contracts
```

- Define critical interfaces between components
- Document contracts and protocols
- Specify data formats and structures
- Define error handling and exceptional cases
- Consider versioning and compatibility

### 7. Identify Risks and Mitigations
```
[STATE: ARCHITECTURE] [RISKS] Architectural risks and mitigations
```

- Identify technical risks in the architecture
- Assess impact and likelihood of each risk
- Define mitigation strategies
- Propose contingency plans
- Identify areas requiring prototyping or validation

### 8. Create Architecture Diagram
```
[STATE: ARCHITECTURE] [DIAGRAM] Architecture diagram (textual representation)
```

- Create a clear visual representation of the architecture
- Show key components and their relationships
- Highlight important interfaces and data flows
- Include relevant infrastructure elements
- Document any deployment considerations

## Best Practices for Non-Fragile Architecture

### Architectural Principles
- **Separation of Concerns**: Divide the system into distinct features with minimal overlap
- **Single Responsibility**: Each component should have one reason to change
- **Open/Closed**: Systems should be open for extension but closed for modification
- **Interface Segregation**: Use specific, focused interfaces rather than general ones
- **Dependency Inversion**: Depend on abstractions, not concrete implementations

### Flexible Design Patterns
- Use dependency injection for flexible component composition
- Apply the strategy pattern for variable behaviors
- Consider observer pattern for loose coupling with events
- Use facade pattern to simplify complex subsystems
- Implement adapter pattern for integrating with external systems

### Future-Proofing Strategies
- Design for extensibility in known variation points
- Create clear abstraction layers to isolate changes
- Minimize coupling between subsystems
- Use feature flags for gradual rollouts and experimentation
- Document architectural decisions and their rationales

## Example (Shortened)
```
[STATE: ARCHITECTURE] Designing battle system for SpaceWar game
[STATE: ARCHITECTURE] [REQUIREMENTS]
- Turn-based combat between two fleets of ships
- Support for different ship types with unique abilities
- Dynamic damage calculation based on weapon types and defenses
- Real-time visual effects during battle resolution
- Ability to save/load battle state

[STATE: ARCHITECTURE] [PRINCIPLES]
- Separate battle logic from visual representation
- Use command pattern for battle actions
- Implement state pattern for battle phases
- Abstract ship capabilities through interfaces
- Use factory pattern for creating ship instances

[STATE: ARCHITECTURE] [ALTERNATIVES]
1. Monolithic battle system: Simple but less maintainable
2. Event-driven battle system: Flexible but more complex
3. Component-based battle system: Extensible but higher initial cost

[STATE: ARCHITECTURE] [DECISION]
Selected component-based architecture for the battle system:
- Better supports varied ship types and abilities
- Allows for independent development of components
- Provides cleaner separation between logic and visuals
- Enables easier testing of individual components

[STATE: ARCHITECTURE] [COMPONENTS]
1. BattleManager: Orchestrates battle flow and state transitions
2. ShipSystem: Manages ship instances and their capabilities
3. ActionSystem: Handles creation and execution of battle actions
4. EffectsSystem: Manages visual effects during battle
5. BattleSerializer: Handles saving/loading battle state

[STATE: ARCHITECTURE] [INTERFACES]
1. IShip: Core ship capabilities and properties
2. IBattleAction: Interface for all actions in battle
3. IEffectRenderer: Interface for rendering visual effects
4. IBattleState: Interface for different battle states

[STATE: ARCHITECTURE] [RISKS]
1. Risk: Performance issues with complex battles
   Mitigation: Implement object pooling and limit simultaneous effects
2. Risk: Battle logic complexity becoming unmanageable
   Mitigation: Extensive unit testing and clear responsibility boundaries
```

## Common Pitfalls to Avoid
- **Over-engineering**: Adding complexity without clear benefits
- **Premature Optimization**: Optimizing before understanding requirements
- **Analysis Paralysis**: Spending too long considering options
- **Ignoring Constraints**: Designing without considering technical limitations
- **Ambiguous Responsibilities**: Failing to clearly define component roles
- **Leaky Abstractions**: Allowing implementation details to leak through interfaces
- **System Duplication**: Designing new subsystems or components without thoroughly investigating existing ones that may serve similar purposes. Always research the current architecture before introducing new elements.
- **Forced Integration**: Conversely, attempting to adapt existing systems for purposes they weren't designed for. When considering reuse of existing architecture, ensure it's appropriate for the new requirements and won't result in components with conflicting responsibilities.

## Transitioning to Other States
When appropriate, transition to:

- **To TDD**: `[TRANSITION: TDD]` - When implementing core components
- **To EXPLORATORY**: `[TRANSITION: EXPLORATORY]` - When testing architectural concepts
- **To REFACTOR**: `[TRANSITION: REFACTOR]` - When adapting existing code to new architecture
- **To REVIEW**: `[TRANSITION: REVIEW]` - When evaluating architectural implementations
- **To CHECKLIST**: `[TRANSITION: CHECKLIST]` - When returning to the main checklist after completing architectural design

### Integration with Checklist Workflow

The ARCHITECTURE state is typically used in two contexts with the CHECKLIST workflow:

1. **As a planning phase**:
   - At the beginning of a checklist or before implementation begins
   - To design the overall approach for a complex checklist item
   - To make key design decisions that will guide implementation
   - Return to CHECKLIST state with `[TRANSITION: CHECKLIST]` when the architecture is defined

2. **As a specific architecture task**:
   - When a checklist explicitly calls for architectural design
   - To create or revise system architecture
   - May result in additional checklist items for implementation
   - Return to CHECKLIST state after architecture design is complete

During architectural work, be mindful of the scope defined in the checklist to avoid over-engineering or designing features beyond what's specified in the requirements.

## Required Discipline Practices

1. **At the start of architecture planning**: Explicitly define the scope with `[STATE: ARCHITECTURE] Designing {system/component}`
2. **Before making decisions**: Document requirements with `[STATE: ARCHITECTURE] [REQUIREMENTS]` and principles with `[STATE: ARCHITECTURE] [PRINCIPLES]`
3. **When evaluating options**: Document alternatives with `[STATE: ARCHITECTURE] [ALTERNATIVES]`
4. **When making decisions**: Document with `[STATE: ARCHITECTURE] [DECISION]`
5. **When defining structure**: Document components with `[STATE: ARCHITECTURE] [COMPONENTS]` and interfaces with `[STATE: ARCHITECTURE] [INTERFACES]`
6. **Before finalizing**: Document risks with `[STATE: ARCHITECTURE] [RISKS]` and create diagrams with `[STATE: ARCHITECTURE] [DIAGRAM]`
7. **Every 15 minutes**: Remind yourself "I am designing the architecture for {system/component}, focusing on structure not implementation"
8. **If interrupted**: Re-read this section to realign with ARCHITECTURE state 