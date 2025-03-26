# AI State: Exploratory Programming

## Purpose
This state guides the AI in developing components that are difficult to test upfront through traditional TDD, such as visual elements, integrations with external systems, or complex interactive features.

## When to Use This State
- When implementing visual or UI components
- When working with MonoGame's rendering pipeline
- When prototyping features with unclear requirements
- When integrating with external systems
- When performance or real-time operations are critical

## State Maintenance Protocol
To maintain this EXPLORATORY state throughout the session, you MUST:

1. **Always begin with a clear specification** of what you're building and verification criteria
2. **Mark each incremental step** using the state markers below
3. **Document verification steps** for each increment
4. **Reflect on lessons learned** after completing each increment

### Required State Markers
```
[STATE: EXPLORATORY] Developing {component}
[STATE: EXPLORATORY] [SPEC] Description of what we're building and verification criteria
[STATE: EXPLORATORY] [INCREMENT #N] Implementing specific aspect of the component
[STATE: EXPLORATORY] [VERIFY] How this increment will be verified to work
[STATE: EXPLORATORY] [REFLECT] Lessons learned from this increment
```

## The Exploratory Workflow

### 1. Define Scope and Specification
```
[STATE: EXPLORATORY] Developing {component}
[STATE: EXPLORATORY] [SPEC] Clear description of what we're building and how we'll verify it works
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

## Best Practices for Non-Fragile Exploratory Code

### Component Isolation
- Create clean boundaries around exploratory components
- Design explicit interfaces for interaction with other systems
- Avoid tight coupling with existing code
- Use composition to make components replaceable

### Future-Proofing
- Identify which parts might need automated testing later
- Extract pure logic from UI/visual components where possible
- Create abstraction layers for external dependencies
- Document assumptions and constraints explicitly

### Progress Toward Testability
- Gradually move toward more testable code as understanding improves
- Extract core algorithms from visual/interactive components
- Create test hooks in hard-to-test components
- Implement logging for runtime verification

## Example (Shortened)
```csharp
[STATE: EXPLORATORY] Developing animated button component
[STATE: EXPLORATORY] [SPEC] Button that pulses when hovered and shows particle effect when clicked

[STATE: EXPLORATORY] [INCREMENT #1] Basic button rendering with hover detection
// Implementation code here...

[STATE: EXPLORATORY] [VERIFY] 
1. Run the game
2. Move mouse over button, confirm it changes from gray to white
3. Move mouse away, confirm it changes back to gray

[STATE: EXPLORATORY] [REFLECT]
- Hover detection works well
- Should extract input handling to make this more testable
- Will need to handle edge case when resolution changes
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

## Required Discipline Practices

1. **At the start of development**: Explicitly define spec with `[STATE: EXPLORATORY] [SPEC]`
2. **For each new increment**: Mark with `[STATE: EXPLORATORY] [INCREMENT #N]`
3. **After implementing an increment**: Provide verification steps with `[STATE: EXPLORATORY] [VERIFY]`
4. **After verification**: Reflect with `[STATE: EXPLORATORY] [REFLECT]`
5. **Every 15 minutes**: Remind yourself "I am exploring {specific aspect} with clear verification steps"
6. **If interrupted**: Re-read this section to realign with EXPLORATORY state 